# MediConnect Infrastructure

This Terraform configuration currently provisions the CEA network layer only:

- One VPC (`10.0.0.0/16`)
- Two public subnets across two Availability Zones
- Two private application subnets across two Availability Zones
- Two private database subnets across two Availability Zones
- Internet Gateway and public routes
- One NAT Gateway for private application subnet egress
- A database route table with no internet route
- Tier-specific security groups
- Encrypted private RDS PostgreSQL
- ECR repositories for frontend and backend images
- RDS credentials stored in Secrets Manager
- ECS Fargate services, Cloud Map service discovery, CloudWatch logs, and an
  internet-facing Application Load Balancer
- GitHub Actions OIDC provider and a repository-scoped deployment role

The NAT Gateway is billable. Run `terraform plan` before applying and destroy
the network when the lab is not in use.

The RDS instance is also billable and is configured as a small, single-AZ,
private PostgreSQL instance for the CEA demonstration. It is encrypted.
Automated backup retention is set to zero because some Free Tier accounts
restrict backup retention; this is a documented availability/recovery
limitation. It can be raised to seven days when the account permits it.

Before planning the ECS resources, create a separate Secrets Manager secret
containing the backend application settings. Do not commit its values. Set its
ARN in `terraform.tfvars` as `application_secret_arn`. The JSON keys required
are `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
`ADMIN_EMAIL`, `ADMIN_PASSWORD`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`,
`MAIL_PORT`, `MAIL_SERVER`, `MAIL_FROM_NAME`, `CLOUDINARY_CLOUD_NAME`,
`CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `STRIPE_SECRET_KEY`,
`STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, and `GEMINI_API_KEY`.

## Usage

From this directory:

```powershell
terraform init
terraform fmt -check
terraform validate
Copy-Item terraform.tfvars.example terraform.tfvars
terraform plan
terraform apply
```

Do not commit `terraform.tfvars` or `.terraform/`.

The ECS task definitions use the immutable `image_tag` ECR image (default
`manual-2`). Publish a new tag and update this variable before each later
application release.

After applying the OIDC resources, configure the `github_deploy_role_arn`
output as the GitHub repository variable `AWS_DEPLOY_ROLE_ARN`. Also configure
`AWS_REGION=ap-south-1` as a repository variable if it is not already present.