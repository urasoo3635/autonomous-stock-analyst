# =============================================================================
# S3 バケット
# =============================================================================

# 静的ファイル・フロントエンド用
resource "aws_s3_bucket" "static" {
  bucket = "${var.project_name}-${var.environment}-static${var.bucket_suffix}"

  tags = {
    Name = "${var.project_name}-${var.environment}-static"
  }
}

resource "aws_s3_bucket_versioning" "static" {
  bucket = aws_s3_bucket.static.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static" {
  bucket = aws_s3_bucket.static.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "static" {
  bucket = aws_s3_bucket.static.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ML モデルアーティファクト用
resource "aws_s3_bucket" "ml_artifacts" {
  bucket = "${var.project_name}-${var.environment}-ml-artifacts${var.bucket_suffix}"

  tags = {
    Name = "${var.project_name}-${var.environment}-ml-artifacts"
  }
}

resource "aws_s3_bucket_versioning" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# データバックアップ用
resource "aws_s3_bucket" "data_backup" {
  bucket = "${var.project_name}-${var.environment}-data-backup${var.bucket_suffix}"

  tags = {
    Name = "${var.project_name}-${var.environment}-data-backup"
  }
}

resource "aws_s3_bucket_versioning" "data_backup" {
  bucket = aws_s3_bucket.data_backup.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_backup" {
  bucket = aws_s3_bucket.data_backup.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_backup" {
  bucket = aws_s3_bucket.data_backup.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "data_backup" {
  bucket = aws_s3_bucket.data_backup.id

  rule {
    id     = "archive-old-backups"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
