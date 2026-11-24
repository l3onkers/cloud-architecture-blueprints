variable "project_name" {
  description = "Project name prefix for Route 53 and ACM resources"
  type        = string
}

variable "domain_name" {
  description = "Generic base domain name for Route 53 Hosted Zone and ACM wildcard certificate"
  type        = string
}
