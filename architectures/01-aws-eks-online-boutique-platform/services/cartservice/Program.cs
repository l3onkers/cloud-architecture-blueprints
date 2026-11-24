using System.Collections.Concurrent;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;

var builder = WebApplication.CreateBuilder(args);

var redisAddr = Environment.GetEnvironmentVariable("REDIS_ADDR") ?? "redis-cart:6379";
var otelEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT")
                   ?? "http://jaeger-collector.tracing.svc.cluster.local:4317";

builder.Services.AddSingleton<ICartStore>(sp =>
{
    var logger = sp.GetRequiredService<ILogger<Program>>();
    if (!string.IsNullOrWhiteSpace(redisAddr) && !redisAddr.Contains("${"))
    {
        try
        {
            var options = ConfigurationOptions.Parse(redisAddr);
            options.AbortOnConnectFail = false;
            options.ConnectTimeout = 2000;
            var multiplexer = ConnectionMultiplexer.Connect(options);
            if (multiplexer.IsConnected)
            {
                logger.LogInformation("Connected to ElastiCache/Redis at {RedisAddr}", redisAddr);
                return new RedisCartStore(multiplexer);
            }
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Redis connection to {RedisAddr} unavailable; activating in-memory fallback store.", redisAddr);
        }
    }

    return new InMemoryCartStore();
});

var app = builder.Build();

app.Use(async (context, next) =>
{
    var traceParent = context.Request.Headers["traceparent"].FirstOrDefault()
                      ?? $"00-{Guid.NewGuid():N}-{Guid.NewGuid().ToString("N")[..16]}-01";
    context.Response.Headers["traceparent"] = traceParent;
    context.Response.Headers["X-OTEL-Service"] = "cartservice";
    context.Response.Headers["X-OTEL-Exporter"] = otelEndpoint;
    await next();
});

app.MapGet("/healthz", (ICartStore store) => Results.Ok(new
{
    status = "ok",
    service = "cartservice",
    backend = store.BackendType,
    redis_addr = redisAddr,
    otlp_endpoint = otelEndpoint
}));

app.MapGet("/cart/{userId}", async (string userId, ICartStore store) =>
{
    var cart = await store.GetCartAsync(userId);
    return Results.Ok(cart);
});

app.MapPost("/cart/{userId}/items", async (string userId, [FromBody] CartItem item, ICartStore store) =>
{
    if (string.IsNullOrWhiteSpace(item.ProductId) || item.Quantity <= 0)
    {
        return Results.BadRequest(new { error = "productId and positive quantity are required." });
    }

    var updated = await store.AddItemAsync(userId, item);
    return Results.Ok(updated);
});

app.MapDelete("/cart/{userId}", async (string userId, ICartStore store) =>
{
    await store.EmptyCartAsync(userId);
    return Results.Ok(new { userId, items = Array.Empty<CartItem>(), cleared = true });
});

var port = Environment.GetEnvironmentVariable("PORT") ?? "7070";
app.Run($"http://0.0.0.0:{port}");

public record CartItem(string ProductId, int Quantity);

public record UserCart(string UserId, List<CartItem> Items);

public interface ICartStore
{
    string BackendType { get; }
    Task<UserCart> GetCartAsync(string userId);
    Task<UserCart> AddItemAsync(string userId, CartItem item);
    Task EmptyCartAsync(string userId);
}

public sealed class InMemoryCartStore : ICartStore
{
    private readonly ConcurrentDictionary<string, List<CartItem>> _carts = new();

    public string BackendType => "in-memory-fallback";

    public Task<UserCart> GetCartAsync(string userId)
    {
        var items = _carts.TryGetValue(userId, out var existing)
            ? existing.ToList()
            : new List<CartItem>();
        return Task.FromResult(new UserCart(userId, items));
    }

    public Task<UserCart> AddItemAsync(string userId, CartItem item)
    {
        var list = _carts.AddOrUpdate(
            userId,
            _ => new List<CartItem> { item },
            (_, current) =>
            {
                lock (current)
                {
                    var idx = current.FindIndex(x => x.ProductId == item.ProductId);
                    if (idx >= 0)
                    {
                        var existing = current[idx];
                        current[idx] = existing with { Quantity = existing.Quantity + item.Quantity };
                    }
                    else
                    {
                        current.Add(item);
                    }
                    return current.ToList();
                }
            });
        return Task.FromResult(new UserCart(userId, list));
    }

    public Task EmptyCartAsync(string userId)
    {
        _carts.TryRemove(userId, out _);
        return Task.CompletedTask;
    }
}

public sealed class RedisCartStore : ICartStore
{
    private readonly IConnectionMultiplexer _redis;
    private readonly InMemoryCartStore _fallback = new();

    public RedisCartStore(IConnectionMultiplexer redis)
    {
        _redis = redis;
    }

    public string BackendType => _redis.IsConnected ? "aws-elasticache-redis" : "in-memory-fallback";

    private static string Key(string userId) => $"boutique:cart:{userId}";

    public async Task<UserCart> GetCartAsync(string userId)
    {
        if (!_redis.IsConnected)
        {
            return await _fallback.GetCartAsync(userId);
        }

        var db = _redis.GetDatabase();
        var payload = await db.StringGetAsync(Key(userId));
        if (payload.IsNullOrEmpty)
        {
            return new UserCart(userId, new List<CartItem>());
        }

        var items = JsonSerializer.Deserialize<List<CartItem>>(payload!) ?? new List<CartItem>();
        return new UserCart(userId, items);
    }

    public async Task<UserCart> AddItemAsync(string userId, CartItem item)
    {
        if (!_redis.IsConnected)
        {
            return await _fallback.AddItemAsync(userId, item);
        }

        var current = await GetCartAsync(userId);
        var items = current.Items.ToList();
        var idx = items.FindIndex(i => i.ProductId == item.ProductId);
        if (idx >= 0)
        {
            items[idx] = items[idx] with { Quantity = items[idx].Quantity + item.Quantity };
        }
        else
        {
            items.Add(item);
        }

        var db = _redis.GetDatabase();
        await db.StringSetAsync(Key(userId), JsonSerializer.Serialize(items), TimeSpan.FromHours(24));
        return new UserCart(userId, items);
    }

    public async Task EmptyCartAsync(string userId)
    {
        if (!_redis.IsConnected)
        {
            await _fallback.EmptyCartAsync(userId);
            return;
        }

        var db = _redis.GetDatabase();
        await db.KeyDeleteAsync(Key(userId));
    }
}
