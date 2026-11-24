output "hosted_zone_id" {
  description = "Route 53 Hosted Zone ID for the platform domain"
  value       = aws_route53_zone.primary.zone_id
}

output "hosted_zone_arn" {
  description = "Route 53 Hosted Zone ARN for ExternalDNS IAM policy scoping"
  value       = aws_route53_zone.primary.arn
}

output "certificate_arn" {
  description = "Validated ACM Certificate ARN covering domain_name and *.domain_name"
  value       = aws_acm_certificate_validation.wildcard.certificate_arn
}
