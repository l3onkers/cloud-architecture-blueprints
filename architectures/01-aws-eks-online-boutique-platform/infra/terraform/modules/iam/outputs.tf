output "aws_lb_controller_role_arn" {
  description = "IAM Role ARN for AWS Load Balancer Controller (IRSA)"
  value       = aws_iam_role.aws_lb_controller.arn
}

output "cluster_autoscaler_role_arn" {
  description = "IAM Role ARN for Cluster Autoscaler (IRSA)"
  value       = aws_iam_role.cluster_autoscaler.arn
}

output "ebs_csi_role_arn" {
  description = "IAM Role ARN for AWS EBS CSI Driver (EKS Pod Identity)"
  value       = aws_iam_role.ebs_csi_driver.arn
}

output "external_dns_role_arn" {
  description = "IAM Role ARN for ExternalDNS (EKS Pod Identity)"
  value       = aws_iam_role.external_dns.arn
}
