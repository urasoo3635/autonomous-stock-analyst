output "zone_id" {
  description = "Route 53 ホストゾーン ID"
  value       = aws_route53_zone.main.zone_id
}

output "name_servers" {
  description = "ネームサーバー（ドメインレジストラに設定が必要）"
  value       = aws_route53_zone.main.name_servers
}

output "certificate_arn" {
  description = "ACM 証明書 ARN"
  value       = aws_acm_certificate.main.arn
}

output "domain_name" {
  description = "ドメイン名"
  value       = var.domain_name
}

output "static_ips" {
  description = "Global Accelerator の固定 IP アドレス"
  value = var.enable_global_accelerator ? [
    for attr in aws_globalaccelerator_accelerator.main[0].ip_sets[0].ip_addresses : attr
  ] : []
}

output "accelerator_dns_name" {
  description = "Global Accelerator の DNS 名"
  value       = var.enable_global_accelerator ? aws_globalaccelerator_accelerator.main[0].dns_name : null
}
