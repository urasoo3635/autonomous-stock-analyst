output "app_log_group_name" {
  description = "アプリケーションログのロググループ名"
  value       = aws_cloudwatch_log_group.app.name
}

output "access_log_group_name" {
  description = "アクセスログのロググループ名"
  value       = aws_cloudwatch_log_group.access.name
}

output "sns_topic_arn" {
  description = "アラート SNS トピック ARN"
  value       = aws_sns_topic.alerts.arn
}
