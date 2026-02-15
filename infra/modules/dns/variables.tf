variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境"
  type        = string
}

variable "domain_name" {
  description = "ドメイン名（例: stock-analyst.example.com）"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB の DNS 名"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB のホストゾーン ID"
  type        = string
}

variable "alb_arn" {
  description = "ALB の ARN"
  type        = string
}

variable "enable_global_accelerator" {
  description = "Global Accelerator を有効にして固定 IP を取得するか"
  type        = bool
  default     = false
}
