# =============================================================================
# ルートレベル出力
# =============================================================================

# --- ネットワーク ---

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "パブリックサブネット ID"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "プライベートサブネット ID"
  value       = module.networking.private_subnet_ids
}

# --- コンピュート ---

output "alb_dns_name" {
  description = "ALB DNS 名"
  value       = module.compute.alb_dns_name
}

output "ec2_public_ip" {
  description = "EC2 パブリック IP（EC2 使用時のみ）"
  value       = module.compute.ec2_public_ip
}

output "ecs_cluster_id" {
  description = "ECS クラスター ID（ECS 使用時のみ）"
  value       = module.compute.ecs_cluster_id
}

# --- データベース ---

output "rds_endpoint" {
  description = "RDS エンドポイント"
  value       = module.database.rds_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis エンドポイント"
  value       = module.database.redis_endpoint
}

# --- ストレージ ---

output "static_bucket_name" {
  description = "静的ファイルバケット名"
  value       = module.storage.static_bucket_name
}

output "ml_artifacts_bucket_name" {
  description = "ML アーティファクトバケット名"
  value       = module.storage.ml_artifacts_bucket_name
}

# --- 監視 ---

output "app_log_group_name" {
  description = "アプリケーションログのロググループ名"
  value       = module.monitoring.app_log_group_name
}

output "sns_topic_arn" {
  description = "アラート SNS トピック ARN"
  value       = module.monitoring.sns_topic_arn
}
