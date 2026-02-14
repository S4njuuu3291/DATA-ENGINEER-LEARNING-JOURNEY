output "bronze_bucket_name" {
  description = "Nama bucket Bronze"
  value       = aws_s3_bucket.bronze.bucket
}

output "bronze_bucket_arn" {
  description = "ARN bucket Bronze"
  value       = aws_s3_bucket.bronze.arn
}

output "attached_user" {
  description = "IAM user yang menerima policy"
  value       = data.aws_iam_user.crawler_bot.user_name
}
