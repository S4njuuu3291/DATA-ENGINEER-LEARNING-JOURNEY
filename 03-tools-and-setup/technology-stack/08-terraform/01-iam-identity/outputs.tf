output "user_arn" {
  description = "ARN dari IAM user baru"
  value       = aws_iam_user.crawler_bot.arn
}

output "access_key_id" {
  description = "Access key ID untuk IAM user"
  value       = aws_iam_access_key.crawler_bot.id
}

output "secret_access_key" {
  description = "Secret access key untuk IAM user"
  value       = aws_iam_access_key.crawler_bot.secret
  sensitive   = true
}
