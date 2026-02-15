variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境"
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch ログの保持日数"
  type        = number
  default     = 30
}

variable "alarm_email" {
  description = "アラーム通知先メールアドレス"
  type        = string
  default     = ""
}

variable "ec2_instance_id" {
  description = "監視対象の EC2 インスタンス ID"
  type        = string
  default     = ""
}

variable "rds_instance_id" {
  description = "監視対象の RDS インスタンス識別子"
  type        = string
  default     = ""
}
