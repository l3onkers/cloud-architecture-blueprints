resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis-sg"
  description = "Security group for ElastiCache Redis cart store allowing TCP 6379 exclusively from EKS worker nodes"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow Redis TCP 6379 strictly from EKS worker node security group"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.eks_node_security_group_id]
  }

  egress {
    description = "Allow Redis replication outbound communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-redis-sg"
  }
}

resource "aws_elasticache_subnet_group" "redis" {
  name        = "${var.project_name}-redis-subnet-group"
  description = "Private subnet group across 3 AZs for ElastiCache Redis cart store"
  subnet_ids  = var.private_subnet_ids
}

resource "aws_elasticache_parameter_group" "redis71" {
  name   = "${var.project_name}-redis71-params"
  family = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
}

resource "aws_elasticache_replication_group" "cart_store" {
  replication_group_id       = "${var.project_name}-cart-redis"
  description                = "Online Boutique ElastiCache Redis 7.1 cluster for cartservice"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = "cache.t4g.small"
  num_cache_clusters         = 2
  port                       = 6379
  parameter_group_name       = aws_elasticache_parameter_group.redis71.name
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  security_group_ids         = [aws_security_group.redis.id]
  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auto_minor_version_upgrade = true

  tags = {
    Name      = "${var.project_name}-cart-redis"
    Component = "cartservice"
  }
}
