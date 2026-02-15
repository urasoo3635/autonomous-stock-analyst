# =============================================================================
# dev 環境設定
# =============================================================================
# EC2 ベースの開発環境。コスト最適化を優先。

terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "autonomous-stock-analyst-tfstate"
    key            = "environments/dev/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "autonomous-stock-analyst-tflock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  profile = var.aws_profile

  default_tags {
    tags = {
      Project     = "stock-analyst"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

# --- 変数 ---

variable "aws_profile" {
  description = "AWS CLI プロファイル名"
  type        = string
  default     = "default"
}

variable "db_password" {
  description = "RDS マスターパスワード"
  type        = string
  sensitive   = true
}

# --- モジュール呼び出し ---

module "networking" {
  source = "../../modules/networking"

  project_name         = "stock-analyst"
  environment          = "dev"
  vpc_cidr             = "10.0.0.0/16"
  availability_zones   = ["ap-northeast-1a", "ap-northeast-1c"]
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]
  enable_nat_gateway   = false # コスト節約
}

module "compute" {
  source = "../../modules/compute"

  project_name       = "stock-analyst"
  environment        = "dev"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  # EC2 を使用（dev 環境）
  use_ec2           = true
  ec2_instance_type = "t3.micro"
  use_ecs           = false

  container_port = 8000
}

module "database" {
  source = "../../modules/database"

  project_name          = "stock-analyst"
  environment           = "dev"
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  app_security_group_id = module.compute.app_security_group_id

  db_instance_class    = "db.t3.micro"
  db_allocated_storage = 20
  db_name              = "stock_analyst"
  db_username          = "dbadmin"
  db_password          = var.db_password
}

module "storage" {
  source = "../../modules/storage"

  project_name = "stock-analyst"
  environment  = "dev"
}

module "monitoring" {
  source = "../../modules/monitoring"

  project_name    = "stock-analyst"
  environment     = "dev"
  ec2_instance_id = module.compute.ec2_instance_id != null ? module.compute.ec2_instance_id : ""
  rds_instance_id = module.database.rds_endpoint != "" ? "stock-analyst-dev-db" : ""

  log_retention_days = 7 # dev では短期間
}

# --- 出力 ---

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "ec2_public_ip" {
  value = module.compute.ec2_public_ip
}

output "rds_endpoint" {
  value     = module.database.rds_endpoint
  sensitive = true
}
