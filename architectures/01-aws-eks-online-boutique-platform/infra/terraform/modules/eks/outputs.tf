output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "Endpoint for the EKS Kubernetes API server"
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "oidc_provider_arn" {
  description = "ARN of the IAM OIDC Provider for the EKS cluster (used by IRSA)"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "oidc_provider_url" {
  description = "Issuer URL of the IAM OIDC Provider without https:// prefix"
  value       = replace(aws_iam_openid_connect_provider.eks.url, "https://", "")
}

output "node_security_group_id" {
  description = "Security Group ID attached to all EKS managed node group instances"
  value       = aws_security_group.node.id
}
