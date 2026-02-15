# =============================================================================
# ルートレベル main.tf
# =============================================================================
# 注意: 本番運用では各環境ディレクトリ (infra/environments/{dev,staging,prod})
# から terraform apply を実行してください。
# このファイルは共通リファレンスとして残しています。

locals {
  project_name = var.project_name
  environment  = var.environment
}

module "networking" {
  source = "./modules/networking"

  project_name         = local.project_name
  environment          = local.environment
  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = var.environment != "dev"
}

module "compute" {
  source = "./modules/compute"

  project_name       = local.project_name
  environment        = local.environment
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  private_subnet_ids = module.networking.private_subnet_ids

  use_ec2           = var.use_ec2
  ec2_instance_type = var.ec2_instance_type
  ec2_key_name      = var.ec2_key_name
  use_ecs           = var.use_ecs
  ecs_task_cpu      = var.ecs_task_cpu
  ecs_task_memory   = var.ecs_task_memory
  ecs_desired_count = var.ecs_desired_count
  container_port    = var.container_port
}

module "database" {
  source = "./modules/database"

  project_name          = local.project_name
  environment           = local.environment
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  app_security_group_id = module.compute.app_security_group_id

  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password

  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
}

module "storage" {
  source = "./modules/storage"

  project_name  = local.project_name
  environment   = local.environment
  bucket_suffix = var.s3_bucket_suffix
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name       = local.project_name
  environment        = local.environment
  log_retention_days = var.log_retention_days
  alarm_email        = var.alarm_email
  ec2_instance_id    = var.use_ec2 ? module.compute.ec2_instance_id : ""
  rds_instance_id    = "${local.project_name}-${local.environment}-db"
}
