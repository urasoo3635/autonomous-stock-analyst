# =============================================================================
# 共通変数
# =============================================================================

variable "project_name" {
  description = "プロジェクト名（リソース命名プレフィックスに使用）"
  type        = string
  default     = "stock-analyst"
}

variable "environment" {
  description = "デプロイ環境 (dev / staging / prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment は dev, staging, prod のいずれかを指定してください。"
  }
}

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "aws_profile" {
  description = "AWS CLI プロファイル名"
  type        = string
  default     = "default"
}

# =============================================================================
# ネットワーク
# =============================================================================

variable "vpc_cidr" {
  description = "VPC の CIDR ブロック"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "使用するアベイラビリティゾーン"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "public_subnet_cidrs" {
  description = "パブリックサブネットの CIDR ブロック"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "プライベートサブネットの CIDR ブロック"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# =============================================================================
# コンピュート
# =============================================================================

variable "use_ec2" {
  description = "EC2 を使用するかどうか（dev/staging 向け）"
  type        = bool
  default     = true
}

variable "use_ecs" {
  description = "ECS Fargate を使用するかどうか（prod 向け）"
  type        = bool
  default     = false
}

variable "ec2_instance_type" {
  description = "EC2 インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

variable "ec2_key_name" {
  description = "EC2 キーペア名（SSH 接続用）"
  type        = string
  default     = ""
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

variable "container_port" {
  description = "アプリケーションコンテナのポート"
  type        = number
  default     = 8000
}

# =============================================================================
# データベース
# =============================================================================

variable "db_instance_class" {
  description = "RDS インスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS ストレージ容量 (GB)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "stock_analyst"
}

variable "db_username" {
  description = "データベースマスターユーザー名"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_password" {
  description = "データベースマスターパスワード"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis ノードタイプ"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Redis キャッシュノード数"
  type        = number
  default     = 1
}

# =============================================================================
# ストレージ
# =============================================================================

variable "s3_bucket_suffix" {
  description = "S3 バケット名のサフィックス（グローバルユニーク用）"
  type        = string
  default     = ""
}

# =============================================================================
# 監視
# =============================================================================

variable "log_retention_days" {
  description = "CloudWatch ログの保持日数"
  type        = number
  default     = 30
}

variable "alarm_email" {
  description = "アラーム通知先のメールアドレス"
  type        = string
  default     = ""
}
