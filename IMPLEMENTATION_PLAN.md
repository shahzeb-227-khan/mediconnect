# Design, Deployment, and Cloud-Native Enhancement of a Three-Tier Web Application

# Cloud Computing - (SE-490) - Complex Engineering Activity (CEA)

**Department of Software Engineering**

## CEA Statement

As a Cloud/DevOps Engineer, you are required to design, containerize, and deploy a three-tier web application on a cloud platform of your choice, and to build a CI/CD pipeline that automates the build and deployment process.

## System Requirements

Students must design and deploy a solution satisfying all of the following requirements.

## 1. Network Layer

- A Virtual Network / VPC with an appropriate CIDR/address range
- Public subnet(s) for internet-facing components
- Private subnet(s) for internal/backend components
- Internet connectivity (Internet Gateway / equivalent) for public subnets
- Appropriate route tables / routing rules
- NAT gateway or equivalent, if private-subnet resources require outbound internet access

## 2. Web Tier

Deploy the Web Tier as a Docker container (e.g., Nginx, Apache, or a front-end application), built from a well-structured Dockerfile. The Web Tier must be publicly accessible via a web browser, typically placed in the public subnet or behind a load balancer.

## 3. Application Tier

Deploy the Application Tier as a Docker container performing application/business logic (e.g., PHP, Python/Flask or Django, Node.js, Java/Spring Boot). Use a Dockerfile and, if the Web and Application tiers run together on the same host, a docker-compose.yml for local multi-service orchestration. The Application Tier must communicate securely with the Database Tier and should generally reside in a private subnet, reachable only from the Web Tier.

## 4. Database Tier

Deploy a managed database service (e.g., Amazon RDS, Azure Database, Google Cloud SQL) or a properly secured self-managed database instance. Supported engines may include MySQL, PostgreSQL, or MariaDB. The database must be accessible only through controlled network access — never directly exposed to the public internet.

## 5. Container Registry

Push the built Docker image(s) for the Web and/or Application tier to a container registry — e.g., GitHub Container Registry (GHCR), Docker Hub, Amazon ECR, Azure Container Registry, or Google Artifact Registry.

## 6. CI/CD Pipeline

Build a CI/CD pipeline that automatically builds, tests, and deploys the application on every code change — e.g., using GitHub Actions, GitLab CI/CD, Azure DevOps Pipelines, Jenkins, or CircleCI. The pipeline must, at minimum: build the Docker image, push it to the registry, and deploy/update the running application (e.g., by pulling the new image onto the target compute instance or updating a Kubernetes deployment).

## 7. Load Balancing and Scalability

Students should implement, where appropriate to their chosen platform:

- A load balancer (e.g., Application Load Balancer, Azure Load Balancer, GCP Load Balancing, or an Nginx/HAProxy-based equivalent)
- Target groups / backend pools
- Auto Scaling Groups or equivalent horizontal scaling mechanism

## 8. Security

Implement and justify suitable security controls, including:

- Security groups / firewall rules per tier
- Network segmentation between public and private subnets
- Principle of least privilege for inter-tier communication
- Secrets/credentials management (avoid hardcoding database credentials, API keys, etc.), including secrets used within the CI/CD pipeline

## 9. Additional Cloud-Native Enhancements (Choose at least one)

- Configure object storage (e.g., Amazon S3, Azure Blob Storage, Google Cloud Storage) to store static assets, uploaded files, or application backups.
- Provision and attach persistent block/file storage (e.g., Amazon EBS/EFS, Azure Disk/Files, GCP Persistent Disk/Filestore) where appropriate.
- Deploy the containerized application using Kubernetes (a managed service such as EKS/AKS/GKE, or a local cluster such as Minikube/Kind), including Kubernetes manifests (Deployment, Service, Ingress, etc.).
- Implement centralized logging and/or monitoring (e.g., CloudWatch, Azure Monitor, Google Cloud Operations, Prometheus/Grafana).
- Implement infrastructure-as-code for the deployment (e.g., Terraform, CloudFormation, Bicep, Pulumi).
- Estimate the monthly infrastructure cost using the relevant provider's pricing calculator and propose at least two cost optimization measures.

## 10. Non-Functional Requirements (NFR) Justification

A cloud-native deployment is judged not only by whether it works, but by whether it satisfies the quality attributes that matter for production systems. Students must explicitly justify, with reference to their own architecture and implementation choices, how their solution addresses each of the following NFRs:

- **Scalability** — how the design accommodates growth in load (e.g., horizontal scaling via Auto Scaling Groups, statelessness of application containers, load balancer distribution).
- **Availability / Reliability** — how the system avoids single points of failure (e.g., multi-AZ/region placement, managed database failover, redundant compute instances).
- **Elasticity** — how resources scale up and down automatically in response to demand, rather than being statically provisioned.
- **Security** — how confidentiality, integrity, and controlled access are enforced across tiers, the network, and the CI/CD pipeline itself.
- **Maintainability / Deployability** — how containerization and the CI/CD pipeline reduce manual effort and risk when releasing new versions.
- **Performance / Latency** — how the architecture (e.g., load balancing, caching, resource sizing, subnet/region placement) supports acceptable response times under expected load.
- **Cost-Efficiency** — how the chosen services and scaling strategy balance performance against running cost.
- **Portability** — how containerization reduces coupling to a specific cloud provider and eases migration.

You are not required to implement every NFR to an advanced degree, but must clearly state which design decisions support which NFRs, and honestly identify any NFRs your current solution does not fully address, along with how they could be improved.

## Required Deliverables

Each student/group must submit:

### 1. Architecture Diagram

A clearly labeled diagram showing all cloud services used, network design, connectivity between components, the container/CI-CD flow, and security boundaries.

### 2. Deployment Evidence (Screenshots)

- Network/VPC configuration and subnets
- Compute instances / container hosts
- Security groups / firewall rules
- Load balancer configuration
- Database instance
- Docker image build and registry listing
- CI/CD pipeline run (successful build and deploy)
- The running application, accessed via a browser

### 3. Source Files

- Dockerfile (and docker-compose.yml if used)
- Kubernetes manifests (if applicable)
- CI/CD pipeline definition file (e.g., deploy.yml for GitHub Actions)
- Link to the source code repository

### 4. Technical Report (4–6 pages)

The report should explain:

- Chosen cloud provider and justification
- Overall architecture and design decisions
- Services used and their role in each tier
- Containerization and CI/CD pipeline design
- Security considerations
- Testing results demonstrating successful automated deployment
- **NFR justification** — a dedicated section mapping specific design/implementation decisions to the non-functional requirements listed in System Requirements item 10, including any known limitations

---

# MediConnect Implementation Plan

## 1. Project Context and Current Position

MediConnect is an existing full-stack hospital and doctor appointment platform:

- **Frontend:** React, Vite, Tailwind CSS, and React Router.
- **Application tier:** FastAPI with SQLAlchemy-based business logic and REST APIs.
- **Database tier:** PostgreSQL with Alembic migrations.
- **Business features:** patient, doctor, and administrator portals; authentication; hospital and doctor search; appointments; queue tokens; reviews; payments; email verification; Cloudinary uploads; and an AI booking assistant.
- **Testing:** Playwright-based functional, navigation, API, form-validation, responsive, performance, accessibility, and network tests.

The application functionality is substantially implemented. The CEA work will focus on production hardening, containerization, cloud infrastructure, security, CI/CD, observability, and evidence.

### Current implementation status

| Area | Current status | CEA action required |
|---|---|---|
| Frontend | React/Vite application exists | Containerize and serve through Nginx |
| Backend | FastAPI APIs and business modules exist | Containerize and add production health checks |
| Database | PostgreSQL and Alembic files exist | Deploy private managed PostgreSQL and validate migrations |
| Local orchestration | Backend Compose runs PostgreSQL/Adminer | Extend or separate local production-like orchestration |
| Tests | Playwright suites exist | Standardize URLs, add CI-compatible smoke/API checks |
| Network | No cloud VPC deployment | Provision public/private subnet architecture |
| Registry | Not configured | Use Amazon ECR for frontend and backend images |
| CI/CD | No deployment workflow | Add GitHub Actions build, test, push, and deploy workflow |
| Load balancing | Not configured | Add Application Load Balancer and target groups |
| Scaling | Not configured | Add ECS service desired count and autoscaling, or equivalent |
| Security | Local environment configuration exists | Remove secrets from code flow and use managed secrets |
| Documentation | README exists | Add diagram, screenshots, report, and deployment runbook |

## 2. Recommended Cloud Platform and Architecture

### Recommended platform: Amazon Web Services

AWS is recommended because it provides direct equivalents for every CEA requirement and has widely documented services:

- Amazon VPC for network segmentation
- Public and private subnets across at least two Availability Zones
- Internet Gateway and NAT Gateway
- Application Load Balancer
- Amazon ECS with Fargate for managed container execution
- Amazon ECR for image storage
- Amazon RDS for private PostgreSQL
- AWS Secrets Manager for runtime credentials
- Amazon CloudWatch for logs and metrics
- S3 for optional backups/static/uploaded objects
- GitHub Actions for CI/CD
- Terraform for infrastructure-as-code

### Target architecture

```text
                         Internet
                             |
                    Application Load Balancer
                    Public subnets, HTTPS
                             |
              +--------------+--------------+
              |                             |
      Frontend ECS service            Backend ECS service
      Web tier / Nginx                Application tier
      Public ALB route                Private subnets
              |                             |
              +--------- /api proxy --------+
                                            |
                              Security group: backend -> DB
                                            |
                              Amazon RDS PostgreSQL
                              Private DB subnets

GitHub Actions -> ECR -> ECS service deployment
ECS tasks -> CloudWatch Logs
Runtime secrets -> AWS Secrets Manager
Optional files/backups -> Amazon S3
```

### Tier boundaries

| Tier | Proposed service | Exposure |
|---|---|---|
| Web | Nginx frontend container on ECS/Fargate | Internet-facing only through ALB |
| Application | FastAPI backend container on ECS/Fargate | Private; accepts traffic only from web/ALB security group |
| Database | Amazon RDS PostgreSQL | Private; accepts traffic only from backend security group |

## 3. Implementation Phases

### Phase 0 — Baseline, repository hygiene, and secrets

**Objectives**

- Confirm the application starts locally from a clean checkout.
- Separate development, test, and production configuration.
- Prevent credentials from entering source control or Docker images.

**Tasks**

- Review tracked files and confirm `.env` files are ignored.
- Rotate any credentials that have been exposed or used during development.
- Keep only placeholder variables in `.env.example`.
- Define a production configuration contract for database, JWT, mail, Stripe, Cloudinary, Gemini, and frontend API URL.
- Standardize frontend/backend/test ports and base URLs.
- Record the current test and build baseline before infrastructure changes.

**Exit criteria**

- No real secrets are committed.
- A new developer can configure the project using documented placeholders.
- Frontend build and backend compilation pass.

### Phase 1 — Backend production readiness

**Objectives**

- Make the FastAPI service safe and observable inside a container.

**Tasks**

- Add a lightweight `/health` endpoint for process health.
- Add a database readiness check for deployment health checks.
- Use structured application logging suitable for CloudWatch.
- Confirm CORS is driven by environment configuration.
- Confirm startup does not depend on `Base.metadata.create_all()` in production.
- Make Alembic the authoritative schema migration mechanism.
- Validate the complete Alembic chain on an empty PostgreSQL database.
- Configure Uvicorn workers and container signal handling.
- Add explicit production settings validation.

**Exit criteria**

- Backend starts with only documented environment variables.
- Health checks return useful status codes.
- `alembic upgrade head` creates the schema on an empty database.
- Backend API smoke tests pass.

### Phase 2 — Frontend production readiness

**Objectives**

- Produce a small, reproducible static frontend image.

**Tasks**

- Confirm the Vite build uses a production API URL.
- Add an Nginx configuration for SPA fallback routing.
- Configure `/api` reverse proxy behavior if frontend and backend share an ALB origin.
- Ensure no development localhost URL is baked into production assets.
- Add frontend runtime/build documentation.
- Verify authentication, booking, payment-return, and role-based routes after deployment.

**Exit criteria**

- `npm run build` succeeds from the `frontend` directory.
- Nginx serves the application and supports client-side routes.
- Frontend API requests resolve to the deployed backend.

### Phase 3 — Containerization and local orchestration

**Objectives**

- Build and run the complete application consistently in containers.

**Tasks**

- Add a multi-stage `frontend/Dockerfile` using a Node build stage and Nginx runtime stage.
- Add a `backend/Dockerfile` using a slim Python runtime.
- Add or update a root/local `docker-compose.yml` for frontend, backend, and PostgreSQL.
- Keep Adminer optional and development-only.
- Add health checks and dependency readiness behavior.
- Use named volumes only for local PostgreSQL data.
- Add `.dockerignore` files for frontend and backend.
- Test image builds without relying on files outside the build context.

**Exit criteria**

- Frontend image builds and serves the application.
- Backend image starts and reaches `/health`.
- PostgreSQL is reachable from the backend using the Compose service name.
- The complete local containerized flow supports a basic user journey.

### Phase 4 — Infrastructure as code

**Objectives**

- Provision repeatable AWS infrastructure without manual console-only configuration.

**Tasks**

- Create Terraform modules or a clearly structured Terraform stack.
- Define a VPC CIDR and two Availability Zones.
- Create public subnets for ALB/NAT routing and private subnets for ECS/RDS.
- Create an Internet Gateway and route tables.
- Create NAT Gateway routing for private outbound traffic where required.
- Create ECR repositories for frontend and backend images.
- Create ECS cluster, task definitions, services, and deployment configuration.
- Create an Application Load Balancer, listeners, target groups, and health checks.
- Create an RDS PostgreSQL instance or cluster in private DB subnets.
- Create security groups with tier-specific ingress rules.
- Create CloudWatch log groups and retention settings.
- Create IAM roles with least-privilege permissions.
- Create Secrets Manager entries or references for application secrets.
- Add variables, outputs, validation, and deployment documentation.

**Exit criteria**

- `terraform fmt`, validation, and plan succeed.
- Infrastructure can be provisioned from a clean account/region configuration.
- Database is not publicly accessible.
- ALB reaches the web tier and the web tier reaches the application tier.

### Phase 5 — Registry and CI/CD pipeline

**Objectives**

- Automate validation, image publication, and deployment on code changes.

**Pipeline stages**

1. Checkout source code.
2. Install frontend and backend dependencies.
3. Run frontend lint/build checks.
4. Run backend compilation and tests.
5. Build frontend and backend Docker images.
6. Scan images and dependencies where available.
7. Authenticate securely to Amazon ECR.
8. Push immutable commit-SHA image tags.
9. Render or update ECS task definitions.
10. Deploy services and wait for stability.
11. Run post-deployment health checks.
12. Publish deployment summary and failure logs.

**Tasks**

- Add `.github/workflows/ci-cd.yml`.
- Trigger validation on pull requests.
- Trigger build/push/deploy on the protected deployment branch.
- Use GitHub OIDC to assume an AWS deployment role instead of long-lived AWS keys.
- Store only non-sensitive configuration as repository variables.
- Store secrets in AWS Secrets Manager and reference them from ECS task definitions.
- Use environment protection rules for production deployment.
- Implement rollback through ECS task definition revision rollback.

**Exit criteria**

- A pull request runs automated checks.
- A merged deployment commit builds both images.
- Images appear in ECR with commit tags.
- ECS services update successfully.
- The workflow verifies the deployed application.

### Phase 6 — Load balancing, scaling, and reliability

**Objectives**

- Demonstrate production-style traffic distribution and recovery.

**Tasks**

- Configure ALB listeners and target groups.
- Use path-based routing for frontend and backend routes where appropriate.
- Configure ECS service health checks.
- Run at least two backend tasks for the availability demonstration if budget permits.
- Configure target tracking autoscaling based on CPU or request load.
- Define deployment minimum healthy percentage and maximum percentage.
- Configure RDS backups, retention, encryption, and maintenance settings.
- Use multiple Availability Zones for private and database subnets.
- Document remaining single points of failure and improvement options.

**Exit criteria**

- ALB distributes traffic to healthy targets.
- Unhealthy tasks are replaced automatically.
- A scaling policy exists and is documented.
- RDS is private and backup settings are verified.

### Phase 7 — Security, observability, and cloud-native enhancement

**Objectives**

- Satisfy the security and additional cloud-native requirements with evidence.

**Tasks**

- Enforce tier-specific security groups.
- Allow public ingress only to ALB ports 80/443.
- Allow web/application traffic only from approved security groups.
- Allow PostgreSQL port 5432 only from the backend security group.
- Enable encryption at rest for RDS, ECR, logs, and object storage where applicable.
- Use HTTPS with an AWS Certificate Manager certificate if a domain is available.
- Enable CloudWatch container logs and basic alarms.
- Add alarms for unhealthy targets, task failures, high CPU, high memory, and database availability.
- Choose infrastructure-as-code, centralized logging, and cost estimation as the primary enhancements.
- Optionally add S3 for application backups or uploaded objects.

**Exit criteria**

- No database or backend task is publicly reachable.
- Runtime secrets are not in source code or image layers.
- Logs can be viewed centrally.
- At least one monitoring alarm is demonstrated.
- At least two cost optimization measures are documented.

### Phase 8 — Testing and deployment evidence

**Objectives**

- Prove that the deployed system works and satisfies the CEA requirements.

**Testing tasks**

- Run backend syntax/compile checks.
- Run database migration tests against a clean PostgreSQL instance.
- Run frontend lint and production build.
- Run container build checks.
- Run API smoke tests against the deployed URL.
- Run Playwright smoke and core functional tests against the deployed frontend.
- Test role separation for patient, doctor, and admin portals.
- Test invalid login and authorization behavior.
- Test appointment creation and queue token behavior.
- Test payment success/cancel return routes without exposing payment secrets.
- Test ALB health checks and task replacement.
- Test a controlled CI/CD deployment from a small code change.

**Evidence checklist**

- [ ] VPC and CIDR screenshot
- [ ] Public and private subnet screenshot
- [ ] Route tables and Internet Gateway screenshot
- [ ] NAT Gateway screenshot, if used
- [ ] ECS cluster/services screenshot
- [ ] ECR repositories and image tags screenshot
- [ ] Security groups screenshot
- [ ] ALB listeners, target groups, and healthy targets screenshot
- [ ] RDS instance, subnet group, encryption, and public-access setting screenshot
- [ ] CloudWatch logs/alarms screenshot
- [ ] Successful GitHub Actions run screenshot
- [ ] Browser screenshot of the running application
- [ ] Test output screenshot or report

### Phase 9 — Technical report and presentation

**Objectives**

- Produce the final CEA submission in the required format.

**Report structure**

1. Introduction and problem statement
2. Existing MediConnect application overview
3. Cloud provider selection and justification
4. Three-tier architecture and network design
5. Containerization design
6. Database and migration strategy
7. Container registry and CI/CD workflow
8. Security controls
9. Load balancing, scaling, and reliability
10. Cloud-native enhancements and cost estimate
11. Testing and deployment evidence
12. Dedicated NFR justification
13. Limitations and future improvements
14. Conclusion

## 4. NFR Justification Plan

| NFR | MediConnect design decision | Evidence/measurement |
|---|---|---|
| Scalability | Stateless frontend/backend containers behind an ALB; ECS service can run multiple tasks | Target group distribution and service task count |
| Availability / Reliability | Multiple Availability Zones, managed RDS, health checks, automatic task replacement | ALB health status, ECS deployment events, RDS configuration |
| Elasticity | ECS Service Auto Scaling based on CPU or request demand | Scaling policy and deployment/scale event |
| Security | Public ALB only; private ECS/RDS; tier-specific security groups; Secrets Manager; HTTPS | Security group and secret configuration screenshots |
| Maintainability / Deployability | Docker images, Terraform, automated GitHub Actions deployment | Successful pipeline run and infrastructure code |
| Performance / Latency | ALB distribution, right-sized tasks, health checks, efficient static Nginx serving | Browser/API response measurements and task metrics |
| Cost-Efficiency | Fargate sizing, controlled desired count, log retention, scheduled non-production shutdown, right-sized RDS | Cost estimate and at least two optimization measures |
| Portability | Docker images, Compose local workflow, Terraform variables, PostgreSQL standard | Local container run and documented provider-specific boundaries |

### Known limitations to state honestly

- A single-region deployment is not equivalent to multi-region disaster recovery.
- NAT Gateway and managed services add cost.
- Advanced observability and distributed tracing may not be implemented in the first version.
- External integrations such as Stripe, Cloudinary, email, and Gemini remain dependent on third-party availability.
- Auto scaling requires representative load testing and may be demonstrated at a limited academic scale.
- A production domain and HTTPS certificate may be omitted if the course environment does not provide DNS access.

## 5. Proposed Repository Structure

```text
.
├── IMPLEMENTATION_PLAN.md
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── alembic/
│   └── src/
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   └── src/
├── docker-compose.yml
├── infrastructure/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── networking.tf
│   ├── ecs.tf
│   ├── rds.tf
│   ├── ecr.tf
│   ├── security.tf
│   └── terraform.tfvars.example
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docs/
│   ├── architecture-diagram.png
│   ├── deployment-evidence/
│   └── technical-report.md
└── testing/
```

## 6. Definition of Done

The implementation will be considered complete when:

- [ ] MediConnect runs locally using the documented containerized workflow.
- [ ] Frontend and backend images build reproducibly.
- [ ] Images are pushed to the selected registry.
- [ ] The VPC contains public and private subnet layers.
- [ ] The web tier is publicly reachable through the load balancer.
- [ ] The application tier is private and reachable only through approved paths.
- [ ] PostgreSQL is deployed privately and migrations run successfully.
- [ ] No secrets are committed, baked into images, or printed in logs.
- [ ] CI/CD automatically tests, builds, pushes, deploys, and verifies changes.
- [ ] Health checks, logs, and at least one monitoring alarm are operational.
- [ ] Scaling and load-balancing configuration is documented and demonstrated.
- [ ] Required screenshots and architecture diagram are collected.
- [ ] The 4–6 page technical report includes the dedicated NFR section.
- [ ] Known limitations and future improvements are clearly documented.

## 7. Suggested Execution Order

1. Secure and standardize configuration.
2. Fix production database migration behavior.
3. Add backend health/readiness endpoints.
4. Add frontend and backend Dockerfiles.
5. Add local full-stack Docker Compose.
6. Test the containerized application locally.
7. Create Terraform infrastructure.
8. Create ECR repositories and push a manual test image.
9. Deploy the first working cloud version.
10. Add GitHub Actions CI/CD.
11. Add load balancing, scaling, alarms, and logging.
12. Run end-to-end testing against the deployed URL.
13. Capture evidence and prepare the report.
14. Perform a final security and requirements review.

## 8. Completion Summary Template

At the end of the project, record:

- Cloud provider and region:
- Repository URL:
- Deployed application URL:
- ECR repository URLs:
- ECS cluster/service names:
- RDS engine and instance class:
- Terraform version:
- CI/CD workflow URL:
- Last successful deployment commit:
- Test suites executed:
- Known limitations:
- Estimated monthly cost:
- Cost optimization measures:
