output "instance_id" {
  description = "EC2 Instance ID of the Bastion host"
  value       = aws_instance.bastion.id
}

output "public_ip" {
  description = "Public IPv4 address of the Bastion host"
  value       = aws_instance.bastion.public_ip
}

output "security_group_id" {
  description = "Security Group ID of the Bastion host"
  value       = aws_security_group.bastion.id
}
