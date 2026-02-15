variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境"
  type        = string
}

variable "bucket_suffix" {
  description = "S3 バケット名のサフィックス（グローバルユニーク用）"
  type        = string
  default     = ""
}
