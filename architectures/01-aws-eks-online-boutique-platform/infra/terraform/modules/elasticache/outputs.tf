output "replication_group_id" {
  description = "ID of the ElastiCache Redis replication group"
  value       = aws_elasticache_replication_group.cart_store.id
}

output "primary_endpoint_address" {
  description = "Address of the primary endpoint for the ElastiCache Redis replication group"
  value       = aws_elasticache_replication_group.cart_store.primary_endpoint_address
}

output "security_group_id" {
  description = "Security Group ID guarding the ElastiCache Redis replication group"
  value       = aws_security_group.redis.id
}
