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

variable "private_subnet_ids" {
  description = "プライベートサブネット ID のリスト"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "アプリケーションセキュリティグループ ID"
  type        = string
}

# --- RDS ---

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

variable "db_max_allocated_storage" {
  description = "RDS 最大ストレージ容量 (GB)"
  type        = number
  default     = 50
}

variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "stock_analyst"
}

variable "db_username" {
  description = "データベースマスターユーザー名"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "データベースマスターパスワード"
  type        = string
  sensitive   = true
}

variable "multi_az" {
  description = "RDS Multi-AZ を有効にするか"
  type        = bool
  default     = false
}

# --- Redis（オプション） ---

variable "enable_redis" {
  description = "ElastiCache Redis を有効にするか"
  type        = bool
  default     = false
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
