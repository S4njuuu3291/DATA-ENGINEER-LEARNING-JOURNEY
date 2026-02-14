data "aws_iam_user" "crawler_bot" {
  user_name = "crawler-bot-sanju"
}

resource "aws_s3_bucket" "bronze" {
  bucket = "sanju-scraper-bronze-data-8429517306"

  tags = {
    Layer   = "Bronze"
    Project = "Job-Scraper"
    Owner   = "Sanju"
  }
}

resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket = aws_s3_bucket.bronze.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_policy" "scraper_s3_write_policy" {
  name        = "scraper_s3_write_policy"
  description = "Write access for scraper to Bronze S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowListBucket"
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [
          aws_s3_bucket.bronze.arn
        ]
      },
      {
        Sid    = "AllowObjectReadWrite"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = [
          "${aws_s3_bucket.bronze.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "crawler_bot_s3_write" {
  user       = data.aws_iam_user.crawler_bot.user_name
  policy_arn = aws_iam_policy.scraper_s3_write_policy.arn
}
