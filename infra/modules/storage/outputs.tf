output "static_bucket_name" {
  description = "静的ファイルバケット名"
  value       = aws_s3_bucket.static.bucket
}

output "static_bucket_arn" {
  description = "静的ファイルバケット ARN"
  value       = aws_s3_bucket.static.arn
}

output "ml_artifacts_bucket_name" {
  description = "ML アーティファクトバケット名"
  value       = aws_s3_bucket.ml_artifacts.bucket
}

output "ml_artifacts_bucket_arn" {
  description = "ML アーティファクトバケット ARN"
  value       = aws_s3_bucket.ml_artifacts.arn
}

output "data_backup_bucket_name" {
  description = "データバックアップバケット名"
  value       = aws_s3_bucket.data_backup.bucket
}

output "data_backup_bucket_arn" {
  description = "データバックアップバケット ARN"
  value       = aws_s3_bucket.data_backup.arn
}
