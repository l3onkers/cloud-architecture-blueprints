variable "project_name" {
  description = "Project name prefix for Bastion host resources"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where Bastion host is deployed"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC for restricting HTTPS egress to EKS API"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID for placing the Bastion EC2 instance"
  type        = string
}

variable "bastion_allowed_cidr" {
  description = "Allowed IPv4 CIDR blocks for inbound SSH access"
  type        = list(string)
}
