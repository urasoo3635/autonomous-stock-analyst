variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC の CIDR ブロック"
  type        = string
}

variable "availability_zones" {
  description = "使用するアベイラビリティゾーン"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "パブリックサブネットの CIDR ブロック"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "プライベートサブネットの CIDR ブロック"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "NAT ゲートウェイを有効にするか（コスト節約のため dev では無効推奨）"
  type        = bool
  default     = false
}
