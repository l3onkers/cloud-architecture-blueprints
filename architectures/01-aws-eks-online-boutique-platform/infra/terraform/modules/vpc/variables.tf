variable "aws_region" {
  description = "AWS region for the S3 Gateway Endpoint service name"
  type        = string
}

variable "project_name" {
  description = "Project name prefix for VPC resources"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name for subnet discovery tags"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "azs" {
  description = "Availability zones across which subnets are distributed"
  type        = list(string)
}

variable "public_subnets" {
  description = "CIDR blocks for the 3 public subnets"
  type        = list(string)
}

variable "private_subnets" {
  description = "CIDR blocks for the 3 private subnets"
  type        = list(string)
}
