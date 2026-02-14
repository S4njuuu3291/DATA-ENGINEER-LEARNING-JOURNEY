output "aws_account_id" {
  description = "AWS Account ID yang digunakan"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region_configured" {
  description = "AWS Region yang dikonfigurasi di provider"
  value       = var.aws_region
}

output "aws_caller_arn" {
  description = "ARN dari AWS caller (user/role yang digunakan)"
  value       = data.aws_caller_identity.current.arn
}

output "terraform_version" {
  description = "Versi Terraform yang digunakan"
  value       = local.terraform_version
}

# Data source untuk mendapatkan informasi AWS account saat ini
data "aws_caller_identity" "current" {}
