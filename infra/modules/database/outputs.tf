output "rds_endpoint" {
  description = "RDS エンドポイント"
  value       = aws_db_instance.main.endpoint
}

output "rds_address" {
  description = "RDS ホストアドレス"
  value       = aws_db_instance.main.address
}

output "rds_port" {
  description = "RDS ポート"
  value       = aws_db_instance.main.port
}

output "rds_database_name" {
  description = "データベース名"
  value       = aws_db_instance.main.db_name
}

output "rds_security_group_id" {
  description = "RDS セキュリティグループ ID"
  value       = aws_security_group.rds.id
}

output "redis_endpoint" {
  description = "Redis エンドポイント"
  value       = var.enable_redis ? aws_elasticache_cluster.main[0].cache_nodes[0].address : null
}

output "redis_port" {
  description = "Redis ポート"
  value       = var.enable_redis ? aws_elasticache_cluster.main[0].cache_nodes[0].port : null
}
