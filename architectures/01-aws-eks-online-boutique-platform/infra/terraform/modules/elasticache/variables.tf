variable "project_name" {
  description = "Project name prefix for ElastiCache Redis resources"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where ElastiCache Redis is deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs across 3 AZs for the ElastiCache subnet group"
  type        = list(string)
}

variable "eks_node_security_group_id" {
  description = "Security group ID of the EKS worker nodes permitted to connect to Redis on port 6379"
  type        = string
}
