resource "aws_iam_user" "crawler_bot" {
  name = "crawler-bot-sanju"

  tags = {
    Project   = "Job-Scraper"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_access_key" "crawler_bot" {
  user = aws_iam_user.crawler_bot.name
}