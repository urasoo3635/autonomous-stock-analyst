# =============================================================================
# Route 53 ホストゾーン
# =============================================================================

resource "aws_route53_zone" "main" {
  name    = var.domain_name
  comment = "${var.project_name} ${var.environment} DNS zone"

  tags = {
    Name = "${var.project_name}-${var.environment}-zone"
  }
}

# =============================================================================
# ACM 証明書（SSL/TLS）
# =============================================================================

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cert"
  }
}

# DNS 検証レコード
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# =============================================================================
# DNS レコード（ALB 向け）
# =============================================================================

# ルートドメイン → ALB
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# www サブドメイン → ALB
resource "aws_route53_record" "app_www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# API サブドメイン → ALB
resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# =============================================================================
# Global Accelerator（固定 IP）
# =============================================================================

resource "aws_globalaccelerator_accelerator" "main" {
  count = var.enable_global_accelerator ? 1 : 0

  name            = "${var.project_name}-${var.environment}-accelerator"
  ip_address_type = "IPV4"
  enabled         = true

  tags = {
    Name = "${var.project_name}-${var.environment}-accelerator"
  }
}

resource "aws_globalaccelerator_listener" "main" {
  count = var.enable_global_accelerator ? 1 : 0

  accelerator_arn = aws_globalaccelerator_accelerator.main[0].id
  protocol        = "TCP"

  port_range {
    from_port = 80
    to_port   = 80
  }

  port_range {
    from_port = 443
    to_port   = 443
  }
}

resource "aws_globalaccelerator_endpoint_group" "main" {
  count = var.enable_global_accelerator ? 1 : 0

  listener_arn = aws_globalaccelerator_listener.main[0].id

  endpoint_configuration {
    endpoint_id = var.alb_arn
    weight      = 100
  }

  health_check_port             = 80
  health_check_protocol         = "HTTP"
  health_check_path             = "/health"
  health_check_interval_seconds = 30
  threshold_count               = 3
}
