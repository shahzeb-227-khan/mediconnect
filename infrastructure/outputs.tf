output "vpc_id" {
  description = "MediConnect VPC ID."
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "MediConnect VPC CIDR."
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = aws_subnet.public[*].id
}

output "app_subnet_ids" {
  description = "Private application subnet IDs."
  value       = aws_subnet.app[*].id
}

output "db_subnet_ids" {
  description = "Private database subnet IDs."
  value       = aws_subnet.db[*].id
}

output "internet_gateway_id" {
  description = "Internet Gateway ID."
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_id" {
  description = "NAT Gateway ID."
  value       = aws_nat_gateway.main.id
}

output "route_table_ids" {
  description = "Route table IDs by tier."
  value = {
    public = aws_route_table.public.id
    app    = aws_route_table.app.id
    db     = aws_route_table.db.id
  }
}

output "security_group_ids" {
  description = "Security group IDs by tier."
  value = {
    alb      = aws_security_group.alb.id
    frontend = aws_security_group.frontend.id
    backend  = aws_security_group.backend.id
    rds      = aws_security_group.rds.id
  }
}

output "ecr_repository_urls" {
  description = "ECR repository URLs."
  value = {
    frontend = aws_ecr_repository.frontend.repository_url
    backend  = aws_ecr_repository.backend.repository_url
  }
}

output "rds_endpoint" {
  description = "Private RDS endpoint."
  value       = aws_db_instance.main.address
}

output "database_secret_arn" {
  description = "Secrets Manager ARN for database credentials."
  value       = aws_secretsmanager_secret.database.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "Public Application Load Balancer DNS name."
  value       = aws_lb.main.dns_name
}

output "application_secret_arn" {
  description = "ARN to use for the manually-created application secret."
  value       = var.application_secret_arn
  sensitive   = true
}

output "github_deploy_role_arn" {
  description = "IAM role ARN to configure as the GitHub AWS_DEPLOY_ROLE_ARN repository variable."
  value       = aws_iam_role.github_deploy.arn
}