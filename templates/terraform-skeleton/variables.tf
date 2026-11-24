variable "aws_region" {
  description = "Primary cloud region for multi-AZ deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Canonical blueprint identifier"
  type        = string
  default     = "gaia-cloud-blueprint"
}

variable "environment" {
  description = "Deployment stage (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "Primary VPC CIDR block spanning 3 Availability Zones"
  type        = string
  default     = "10.0.0.0/16"
}

variable "domain_name" {
  description = "Parameterized base domain name for ACM TLS and ExternalDNS"
  type        = string
  default     = "blueprint.example.com"
}
