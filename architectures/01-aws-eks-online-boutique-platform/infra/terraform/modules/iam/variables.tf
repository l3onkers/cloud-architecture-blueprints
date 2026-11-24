variable "project_name" {
  description = "Project name prefix for IAM roles and policies"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name for IRSA and Pod Identity associations"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS IAM OIDC Provider for IRSA trust policies"
  type        = string
}

variable "oidc_provider_url" {
  description = "URL of the EKS IAM OIDC Provider without https:// prefix"
  type        = string
}

variable "hosted_zone_arn" {
  description = "ARN of the Route 53 Hosted Zone managed by ExternalDNS"
  type        = string
}
