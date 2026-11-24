variable "project_name" {
  description = "Project name prefix for EKS resources"
  type        = string
}

variable "cluster_name" {
  description = "Name of the Amazon EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes control plane and worker version"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where EKS is deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the EKS control plane and node groups"
  type        = list(string)
}

variable "bastion_security_group_id" {
  description = "Security group ID of the Bastion host permitted to reach the private EKS API"
  type        = string
}
