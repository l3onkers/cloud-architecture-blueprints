# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build

WORKDIR /src
COPY CartService.csproj .
RUN dotnet restore CartService.csproj

COPY Program.cs .
RUN dotnet publish CartService.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime

RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -D -s /sbin/nologin appuser

WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app/publish .

ENV ASPNETCORE_URLS=http://+:7070 \
    PORT=7070

USER 1001:1001
EXPOSE 7070

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:7070/healthz || exit 1

ENTRYPOINT ["dotnet", "CartService.dll"]
