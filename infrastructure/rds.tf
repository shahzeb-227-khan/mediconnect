resource "random_password" "db" {
  length  = 32
  special = true
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = aws_subnet.db[*].id

  tags = {
    Name = "${local.name_prefix}-db-subnets"
  }
}

resource "aws_secretsmanager_secret" "database" {
  name                    = "${local.name_prefix}/database"
  description             = "MediConnect RDS PostgreSQL connection credentials"
  recovery_window_in_days = 7

  tags = {
    Name = "${local.name_prefix}-database-secret"
  }
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db.result
    database = var.db_name
  })
}

resource "aws_db_instance" "main" {
  identifier              = "${local.name_prefix}-postgres"
  engine                  = "postgres"
  engine_version          = "15"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  max_allocated_storage   = 50
  storage_type            = "gp3"
  storage_encrypted       = true
  db_name                 = var.db_name
  username                = var.db_username
  password                = random_password.db.result
  port                    = 5432
  publicly_accessible     = false
  multi_az                = false
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  # Free Tier accounts may limit automated backup retention to zero days.
  # Backups can be enabled later if the account plan permits it.
  backup_retention_period = 0
  deletion_protection     = false
  skip_final_snapshot     = true
  apply_immediately       = true

  tags = {
    Name = "${local.name_prefix}-postgres"
    Tier = "database"
  }
}
