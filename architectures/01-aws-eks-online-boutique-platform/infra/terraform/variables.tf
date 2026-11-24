variable "aws_region" {
  description = "AWS region for all cloud infrastructure resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project identifier used for resource naming and tagging"
  type        = string
  default     = "online-boutique"
}

variable "cluster_name" {
  description = "Name of the Amazon EKS cluster"
  type        = string
  default     = "terraform-cluster"
}

variable "cluster_version" {
  description = "Kubernetes version for the Amazon EKS control plane and managed node groups"
  type        = string
  default     = "1.34"
}

variable "vpc_cidr" {
  description = "Primary IPv4 CIDR block for the Virtual Private Cloud"
  type        = string
  default     = "10.0.0.0/16"
}

variable "domain_name" {
  description = "Base DNS domain name for Route 53 hosted zone and ACM TLS certificates"
  type        = string
  default     = "boutique.example.com"
}

variable "bastion_allowed_cidr" {
  description = "List of allowed IPv4 CIDR blocks permitted to SSH into the bastion host"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}
