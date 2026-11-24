output "vpc_id" {
  description = "ID of the Online Boutique VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs across 3 AZs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs across 3 AZs"
  value       = module.vpc.private_subnet_ids
}

output "s3_gateway_endpoint_id" {
  description = "ID of the VPC S3 Gateway Endpoint attached to private route tables"
  value       = module.vpc.s3_gateway_endpoint_id
}

output "bastion_public_ip" {
  description = "Public IPv4 address of the hardened EC2 Bastion host"
  value       = module.bastion.public_ip
}

output "eks_cluster_name" {
  description = "Name of the Amazon EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL for the Amazon EKS Kubernetes API server"
  value       = module.eks.cluster_endpoint
}

output "elasticache_redis_primary_endpoint" {
  description = "Primary endpoint address of the ElastiCache Redis 7.1 cart store replication group"
  value       = module.elasticache.primary_endpoint_address
}

output "acm_certificate_arn" {
  description = "ARN of the DNS-validated ACM wildcard TLS certificate"
  value       = module.dns_acm.certificate_arn
}

output "aws_lb_controller_role_arn" {
  description = "IAM Role ARN for AWS Load Balancer Controller (IRSA)"
  value       = module.iam.aws_lb_controller_role_arn
}

output "cluster_autoscaler_role_arn" {
  description = "IAM Role ARN for Kubernetes Cluster Autoscaler (IRSA)"
  value       = module.iam.cluster_autoscaler_role_arn
}

output "ebs_csi_role_arn" {
  description = "IAM Role ARN for Amazon EBS CSI Driver (EKS Pod Identity)"
  value       = module.iam.ebs_csi_role_arn
}

output "external_dns_role_arn" {
  description = "IAM Role ARN for ExternalDNS (EKS Pod Identity)"
  value       = module.iam.external_dns_role_arn
}
