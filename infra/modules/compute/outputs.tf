output "alb_dns_name" {
  description = "ALB の DNS 名"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ALB の ARN"
  value       = aws_lb.main.arn
}

output "alb_zone_id" {
  description = "ALB のホストゾーン ID"
  value       = aws_lb.main.zone_id
}

output "alb_security_group_id" {
  description = "ALB セキュリティグループ ID"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "アプリケーションセキュリティグループ ID"
  value       = aws_security_group.app.id
}
output "ecr_repository_backend_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_frontend_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "target_group_arn" {
  description = "ターゲットグループ ARN"
  value       = aws_lb_target_group.app.arn
}

output "ec2_instance_id" {
  description = "EC2 インスタンス ID"
  value       = var.use_ec2 ? aws_instance.app[0].id : null
}

output "ec2_public_ip" {
  description = "EC2 パブリック IP"
  value       = var.use_ec2 ? aws_instance.app[0].public_ip : null
}

output "ecs_cluster_id" {
  description = "ECS クラスター ID"
  value       = var.use_ecs ? aws_ecs_cluster.main[0].id : null
}

output "ecs_service_name" {
  description = "ECS サービス名"
  value       = var.use_ecs ? aws_ecs_service.app[0].name : null
}
