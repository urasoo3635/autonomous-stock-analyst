variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "パブリックサブネット ID のリスト"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "プライベートサブネット ID のリスト"
  type        = list(string)
}

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "container_port" {
  description = "アプリケーションコンテナのポート"
  type        = number
  default     = 8000
}

# --- EC2 ---

variable "use_ec2" {
  description = "EC2 を使用するか"
  type        = bool
  default     = false
}

variable "ec2_instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

variable "ec2_key_name" {
  description = "EC2 キーペア名"
  type        = string
  default     = ""
}

variable "ssh_allowed_cidrs" {
  description = "SSH アクセスを許可する CIDR ブロック"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# --- ECS ---

variable "use_ecs" {
  description = "ECS Fargate を使用するか"
  type        = bool
  default     = false
}

variable "ecs_task_cpu" {
  description = "ECS タスクの CPU ユニット"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "ECS タスクのメモリ (MiB)"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "ECS サービスの希望タスク数"
  type        = number
  default     = 1
}

variable "container_image" {
  description = "コンテナイメージ URI"
  type        = string
  default     = "nginx:latest"
}

variable "log_retention_days" {
  description = "CloudWatch ログ保持日数"
  type        = number
  default     = 30
}

variable "certificate_arn" {
  description = "ACM 証明書 ARN（HTTPS 有効化用。空の場合は HTTP のみ）"
  type        = string
  default     = ""
}
