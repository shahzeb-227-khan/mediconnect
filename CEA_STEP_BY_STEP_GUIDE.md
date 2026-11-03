# CEA Step-by-Step Guide: MediConnect on AWS (SE-490, Cloud Computing)

This guide turns `IMPLEMENTATION_PLAN.md` into an ordered checklist. Each step says:
- **Do**: what to build or change
- **Where**: the file or console location
- **Done when**: the checkpoint that proves the step works
- **Evidence**: the screenshot or file to keep for the report

Requirement numbers (R1 to R10) refer to the "System Requirements" section of the CEA statement.

---

## 0. What the marks are most likely tied to

I do not have your marking rubric. The CEA statement is organised around these items, so the guide follows them:

| Item | What the marker looks for | Steps |
|---|---|---|
| R1 Network | VPC, public/private subnets in 2 AZs, IGW, NAT, route tables | 5 |
| R2 Web tier | Nginx container, Dockerfile, publicly reachable | 4, 7 |
| R3 Application tier | FastAPI container, private, reachable only from web | 2, 4, 6 |
| R4 Database | Private managed PostgreSQL, not public | 6 |
| R5 Registry | Images in ECR with tags | 6, 8 |
| R6 CI/CD | GitHub Actions: build, test, push, deploy on every change | 9 |
| R7 Load balancing and scaling | ALB, target groups, ECS autoscaling | 7, 10 |
| R8 Security | Security groups per tier, least privilege, Secrets Manager | 1, 6 |
| R9 Enhancements (choose 1+) | Terraform (IaC), CloudWatch logs, cost estimate with 2 optimisations | 5, 7, 11 |
| R10 NFR justification | Written section mapping decisions to 8 NFRs, with honest limitations | 14 |
| Deliverables | Diagram, 13 screenshots, source files, 4 to 6 page report | 12, 13, 14, 15 |

The biggest mark risks are **R10 (NFR section)**, **the screenshots**, and **a working CI/CD run that you can show**. Do those with the same care as the code.

---

## Step 1: Secure the repository (Phase 0, R8)

**Do**
1. Confirm no secrets are tracked by git:
   ```bash
   git ls-files | grep -iE "\.env"
   ```
   The only result should be `.env.example` files. `backend/.env` and `frontend/.env` must not appear.
2. Rotate every key in `backend/.env`. These values have been used during development, so treat them as exposed: JWT secret, admin password, mail password, Cloudinary secret, Stripe secret and webhook secret, and the Gemini key.
3. Add `frontend/.env.example`. The README tells people to copy it, but the file does not exist. It should contain `VITE_API_BASE_URL=` with no value.
4. Commit `IMPLEMENTATION_PLAN.md`, which is currently untracked.

**Done when:** `git ls-files | grep env` shows only example files, and a new developer could set up the project from the `.env.example` files.

**Evidence:** Terminal output of the `git ls-files` check (for the report's security section).

---

## Step 2: Backend production readiness (Phase 1, R3)

Files: `backend/main.py`, `backend/alembic/`, `backend/src/utils/settings.py`

**Do**
1. **Remove the schema shortcut.** `main.py` calls `Base.metadata.create_all(bind=engine)`. Delete that line. Alembic becomes the only way the schema is created.
2. **Check the migration chain.** Your `alembic/versions/` has 5 migrations. Create an empty PostgreSQL database and run:
   ```bash
   alembic upgrade head
   ```
   Confirm `alembic.ini` and `alembic/env.py` read `DATABASE_URL` from settings and do not contain a hardcoded URL.
3. **Add two health endpoints** in `main.py`:
   - `GET /health` returns `{"status": "ok"}` with 200. This is liveness: the process is running.
   - `GET /health/db` runs `SELECT 1` through the engine and returns 200, or 503 if it fails. This is readiness: the database is reachable.
4. **Add structured logging to stdout** with `logging.basicConfig(level=logging.INFO, format=...)`. CloudWatch collects stdout, so there is no need to write log files.
5. **Keep CORS driven by config.** `allow_origins=[settings.ORIGIN_URL]` already does this. Keep it.

**Done when:** `uvicorn main:app` starts with only the variables in `.env.example`, `curl localhost:8000/health` returns 200, and `alembic upgrade head` works on an empty database.

**Evidence:** Terminal output of `alembic upgrade head` on the empty database, and the `/health` response.

---

## Step 3: Frontend production readiness (Phase 2, R2)

Files: `frontend/src/lib/api.js`, `frontend/vite.config.js`

**Do**
1. `api.js` falls back to `http://localhost:8000`. This is fine for development, but it must not end up in production. Vite replaces `VITE_*` values **at build time**, so the value must be passed when the Docker image is built, not when the container starts.
2. **Choose the routing design now** (this decides the Nginx config):
   - The frontend calls `/api/...` on the same domain.
   - Nginx forwards `/api/` to the backend. The trailing slash on `proxy_pass` removes the `/api` prefix, so `/api/patients` reaches FastAPI as `/patients`.
   - The public ALB only sends traffic to the frontend. The backend is reached only from the frontend, through the private network.
   - This avoids CORS problems and keeps the backend private.
3. Confirm `npm run build` succeeds in `frontend/`, and that `dist/` contains no `localhost`:
   ```bash
   grep -r "localhost" frontend/dist || echo "clean"
   ```
4. Check the Vercel SPA rewrite already in the repo. Nginx needs the same behaviour (`try_files`), which is in Step 4.

**Done when:** `npm run build` passes, and the production bundle does not contain `localhost`.

---

## Step 4: Containerisation (Phase 3, R2 and R3)

**Do**

**4a. `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```
- Pin the versions in `requirements.txt` (for example `fastapi==x.y.z`). Right now nothing is pinned, so builds are not reproducible. Generate pins with `pip freeze` from your working venv.

**4b. `backend/.dockerignore`**
```
.env
.venv
venv
__pycache__
*.pyc
.git
```
This is critical: without it, `.env` with your secrets is copied into the image.

**4c. `frontend/Dockerfile`** (multi-stage)
```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```
Node 22 is used because Vite 8 needs a recent Node version.

**4d. `frontend/nginx.conf`**
```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;

  location /api/ {
    proxy_pass http://backend:8000/;      # trailing slash strips /api
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location / {
    try_files $uri /index.html;           # SPA fallback for React Router
  }
}
```

**4e. `frontend/.dockerignore`**: `node_modules`, `dist`, `.env`

**4f. Root `docker-compose.yml`** (the current one is in `backend/`; move and extend it)
- `db`: `postgres:15`, a named volume, and a `healthcheck` using `pg_isready`
- `backend`: `build: ./backend`, `env_file: ./backend/.env`, `DATABASE_URL` pointing at `db:5432`, `depends_on` with `condition: service_healthy`
- `frontend`: `build: ./frontend`, `ports: "8080:80"`
- `adminer`: put it under `profiles: ["dev"]` so it only starts when requested

**Done when:** `docker compose up --build` runs all services, `http://localhost:8080` loads the app, and you can register and log in through the containers.

**Evidence:** Screenshot of `docker compose ps` showing healthy containers, and of the app running at localhost:8080.

---

## Step 5: Network design with Terraform (Phase 4, R1 and R9 IaC)

**Do**

Create the folder `infrastructure/` with the files from the plan: `main.tf`, `variables.tf`, `outputs.tf`, `networking.tf`, `ecs.tf`, `rds.tf`, `ecr.tf`, `security.tf`, `terraform.tfvars.example`. Keep real values out of git (`terraform.tfvars` goes in `.gitignore`).

Use this address plan. Each tier sits in two Availability Zones:

| Subnet | CIDR | Holds |
|---|---|---|
| Public A / B | 10.0.1.0/24, 10.0.2.0/24 | ALB, NAT Gateway |
| Private app A / B | 10.0.11.0/24, 10.0.12.0/24 | ECS frontend and backend tasks |
| Private DB A / B | 10.0.21.0/24, 10.0.22.0/24 | RDS PostgreSQL |

VPC: `10.0.0.0/16`.

- **Region:** `ap-south-1` (Mumbai) is the closest AWS region to Pakistan, which helps the latency NFR. State this choice and the reason in the report.
- **Internet Gateway:** attached to the VPC.
- **Public route table:** `0.0.0.0/0` to the IGW, associated with both public subnets.
- **NAT Gateway:** one, in public subnet A, with the private app route table sending `0.0.0.0/0` to it. Private tasks need it to pull images from ECR, read secrets, send logs, and call Stripe, Cloudinary, Gemini and the mail server. Use one NAT to save cost. State the trade-off: if that AZ fails, private outbound traffic stops (see the limitations).
- **DB route table:** no route to the internet at all.

**Done when:** `terraform fmt -check`, `terraform validate` and `terraform plan` all succeed, and after `terraform apply` the VPC console shows the 6 subnets, the routes and the NAT.

**Evidence:** VPC and CIDR screenshot; public and private subnet list; route tables with the IGW and NAT routes; NAT Gateway screenshot.

---

## Step 6: Security, registry, database and secrets (R4, R5, R8)

**Do**

**6a. Security groups (one per tier, least privilege)**

| Security group | Inbound rule | Source |
|---|---|---|
| `sg-alb` | TCP 80 (and 443 if you have a domain) | 0.0.0.0/0 |
| `sg-frontend` | TCP 80 | `sg-alb` only |
| `sg-backend` | TCP 8000 | `sg-frontend` only |
| `sg-rds` | TCP 5432 | `sg-backend` only |

No rule opens 22 or 5432 to the internet. Keep the default egress rules, since tasks need outbound access through NAT.

**6b. ECR**
- Two repositories: `mediconnect-frontend`, `mediconnect-backend`
- Enable scan on push and encryption
- Set tag mutability to `IMMUTABLE`, so a commit tag can never be overwritten

**6c. RDS PostgreSQL**
- Engine PostgreSQL 15, instance `db.t4g.micro` (or `db.t3.micro`)
- `publicly_accessible = false`
- Storage encryption on
- Subnet group using the two DB subnets
- Backup retention 7 days
- Multi-AZ: this is a trade-off. Turn it on for the availability NFR if your budget allows, and list it in the cost section. Otherwise say clearly in the report that it is single-AZ.

**6d. Secrets Manager**
- Create one secret (JSON object with all keys from `.env`, except non-sensitive values) or one secret per value
- In the ECS task definition, use a `secrets` block that references the ARN. Do not use an `environment` block for passwords
- The `DATABASE_URL` is built from the RDS endpoint and the password in the secret

**6e. IAM (least privilege)**
- **ECS task execution role:** pull from ECR, read the named secrets, write to CloudWatch Logs. Nothing else.
- **ECS task role:** empty or minimal, since the app does not call AWS APIs.
- **GitHub deploy role:** trusted only for your repo and the `main` branch through OIDC (set up in Step 9). It can push to ECR and update the ECS services only.

**Done when:** RDS shows "Publicly accessible: No", and the security group for RDS allows port 5432 only from the backend security group.

**Evidence:** Security group rules screenshot (all four groups); RDS instance page showing encryption and public access "No"; ECR repositories screenshot; Secrets Manager secret list (values hidden).

---

## Step 7: Compute, load balancer and scaling (R2, R3, R7, R9 logging)

**Do**

**7a. ECS cluster and task definitions (Fargate)**
- Frontend task: 0.25 vCPU, 512 MB, container port 80
- Backend task: 0.5 vCPU, 1 GB, container port 8000, with the `secrets` block from Step 6d
- Both tasks use the `awslogs` log driver to a CloudWatch log group with **7-day retention**
- Run both task types in the **private app subnets**. Only the ALB is in public subnets. This is the cleanest design, and it matches the plan's "private" requirement.

**7b. Service discovery for the backend.** The frontend's Nginx needs to find the backend. The simplest option is **ECS Service Connect** with the name `backend` on port 8000. This matches `proxy_pass http://backend:8000/` in `nginx.conf`.

**7c. Application Load Balancer**
- Public subnets, security group `sg-alb`
- Listener on port 80 (HTTPS on 443 with an ACM certificate if you have a domain; otherwise list it as a limitation)
- One target group for the frontend, type `ip`, health check path `/`, expected 200
- Default action forwards to the frontend target group

**7d. ECS services**
- `mediconnect-frontend`: desired count 2, attached to the ALB target group
- `mediconnect-backend`: desired count 2, Service Connect enabled, no ALB target group (the backend is reached only through the frontend)
- Deployment settings: minimum healthy 100%, maximum 200%, and the **deployment circuit breaker with rollback** turned on. This is your rollback mechanism for R6.

**7e. Autoscaling**
- Application Auto Scaling target on each service: min 1 (or 2), max 4
- Target tracking policy on average CPU at 60%

**7f. Alarms (CloudWatch)**
- ALB unhealthy host count greater than 0
- ECS service CPU above 80%
- RDS free storage space and CPU
- Send to an SNS topic with your email

**Done when:** The ALB target group shows healthy targets, opening the ALB DNS name in a browser shows the MediConnect home page, and a login through the deployed site works.

**Evidence:** ECS cluster and services screenshot; ALB listener and target group with healthy targets; CloudWatch log group with recent entries; one CloudWatch alarm; autoscaling policy; the running app in a browser (the ALB DNS in the address bar).

---

## Step 8: First manual deployment and migration

This proves the infrastructure works before automation (matches plan step 8 and 9).

**Do**
1. Log in to ECR, then build and push both images, tagged with a version such as `manual-1`:
   ```bash
   aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.ap-south-1.amazonaws.com
   docker build -t <ecr-url>/mediconnect-backend:manual-1 backend
   docker build -t <ecr-url>/mediconnect-frontend:manual-1 --build-arg VITE_API_BASE_URL=/api frontend
   docker push <ecr-url>/mediconnect-backend:manual-1
   docker push <ecr-url>/mediconnect-frontend:manual-1
   ```
2. Point both task definitions at these images, then update the services.
3. **Run the migration as a one-off ECS task** using the backend task definition with the command overridden to `alembic upgrade head`. Do not run it from your laptop, since the database is private. Keep the output in CloudWatch.

**Done when:** The migration task exits with code 0, and the app works on the ALB URL.

**Evidence:** The ECR listing with image tags; the one-off migration task's logs.

---

## Step 9: CI/CD with GitHub Actions (Phase 5, R6)

**Do**

**9a. AWS trust for GitHub (no long-lived keys)**
- In IAM, add an OIDC identity provider for `token.actions.githubusercontent.com`
- Create a role `mediconnect-github-deploy` that trusts only `repo:<your-github-user>/<repo>:ref:refs/heads/main`
- Store the role ARN and region as **repository variables** (not secrets), since they are not sensitive

**9b. GitHub environment**
- In repo settings, create an environment named `production` with a required reviewer. This gives you a manual approval gate for R8 and the plan's environment-protection requirement.

**9c. `.github/workflows/ci-cd.yml`**
```yaml
name: CI/CD

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - name: Frontend lint and build
        run: cd frontend && npm ci && npm run lint && npm run build
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Backend install and compile check
        run: cd backend && pip install -r requirements.txt && python -m compileall -q src main.py

  deploy:
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push images (tagged with the commit SHA)
        env:
          REGISTRY: ${{ steps.ecr.outputs.registry }}
        run: |
          docker build -t $REGISTRY/mediconnect-backend:$GITHUB_SHA backend
          docker build -t $REGISTRY/mediconnect-frontend:$GITHUB_SHA --build-arg VITE_API_BASE_URL=/api frontend
          docker push $REGISTRY/mediconnect-backend:$GITHUB_SHA
          docker push $REGISTRY/mediconnect-frontend:$GITHUB_SHA
      - name: Render and deploy task definitions
        # Use aws-actions/amazon-ecs-render-task-definition and
        # aws-actions/amazon-ecs-deploy-task-definition for each service,
        # with wait-for-service-stability: true.
        run: echo "Deploy step: see the two action steps described in the guide"
      - name: Post-deploy health check
        run: curl --fail ${{ vars.APP_URL }}/api/health
```
Replace the placeholder `run:` in the deploy step with the two `amazon-ecs-*` actions. They render the task definition with the new SHA image and wait until the service is stable. Note that `/api/health` works only if the Nginx `/api/` block forwards to the backend's `/health`.

**9d. Test the pipeline with a real change.** Make a small visible change (for example, the footer text), push it to `main`, and watch the run.

**Done when:** A pull request runs `validate`, a merge to `main` runs both jobs, the images appear in ECR tagged with the commit SHA, the ECS services update, and the change is visible on the ALB URL.

**Evidence:** Screenshot of the successful GitHub Actions run (both jobs green); the ECR tags showing the SHA; the ECS service events showing the new deployment; a before and after screenshot of your small change.

**Rollback** (for the report): explain that the circuit breaker rolls back a failed deployment automatically, and that you can also redeploy an earlier task definition revision.

---

## Step 10: Reliability and scaling tests (R7)

**Do**
1. **Traffic distribution:** open the ALB target group and show that both frontend targets are healthy. Refresh the app several times.
2. **Self-healing:** stop one running frontend task from the ECS console (or with `aws ecs stop-task`). ECS starts a replacement. Keep the ECS events tab showing the replacement.
3. **Scaling:** run a simple load test against the ALB URL, for example `hey -z 2m -c 50 http://<alb-dns>/`. Watch the CPU metric and the scaling event. If the CPU target is not reached, lower the target to 30% for the demo and say so in the report.
4. **Latency:** record average response time from the load test for the Performance NFR.

**Done when:** You have one screenshot each of the healthy targets, the replacement task, and a scale-out event.

**Evidence:** Those three screenshots, plus the load test output (latency numbers).

---

## Step 11: Cloud-native enhancements and cost (R9)

The plan chooses three enhancements. You need **at least one**, so three is safe.

**Do**
1. **Infrastructure as code:** the Terraform folder from Step 5 (already done). Show `terraform plan` output in the report.
2. **Centralised logging:** CloudWatch log groups with retention (done in Step 7). Show a log query or stream.
3. **Cost estimate:** Open the AWS Pricing Calculator and add each service with its settings: 2 Fargate frontend tasks, 2 Fargate backend tasks, the ALB, one NAT Gateway, RDS instance, storage, ECR, CloudWatch logs, Secrets Manager secrets, data transfer. Save the estimate and screenshot the summary.
4. **Two cost optimisations** (state the saving in your own numbers from the calculator):
   - Use **Graviton (ARM) Fargate** tasks, which are usually cheaper per vCPU. Test that the images build for ARM.
   - Keep **log retention** short (7 days) and **scale to a minimum** outside demo time.
   - Other valid options: one NAT Gateway instead of two, a smaller RDS class, scheduled scaling to zero for non-production, Fargate Spot for non-critical tasks.
5. **Tear-down:** after your evidence is captured, run `terraform destroy` so the account does not keep charging. Mention this in the report.

**Done when:** The estimate and the two optimisations are written in the report with numbers.

**Evidence:** Pricing Calculator summary screenshot; a short table of the cost optimisations.

---

## Step 12: Architecture diagram (Deliverable 1)

**Do**

Draw it in draw.io or Excalidraw and export as PNG to `docs/architecture-diagram.png`. It must show:
- Internet, the ALB in the public subnets, and the IGW
- Two AZs, each with a public subnet, a private app subnet and a private DB subnet
- NAT Gateway (public subnet to private subnets)
- ECS frontend (Nginx) tasks, and backend (FastAPI) tasks, in private subnets
- Amazon RDS PostgreSQL in the DB subnets, with no internet arrow
- Security boundaries: dashed boxes labelled `sg-alb`, `sg-frontend`, `sg-backend`, `sg-rds`, with the allowed ports on each arrow (80, 8000, 5432)
- The CI/CD flow: GitHub Actions to ECR to ECS, with the OIDC role
- Secrets Manager and CloudWatch, connected to the tasks

**Done when:** Someone who has never seen the project can follow the request path from the internet to the database.

---

## Step 13: Deployment evidence checklist (Deliverable 2)

Collect these screenshots, each with a short caption. Use the **Evidence checklist** from Phase 8 of the plan:

- [ ] VPC and CIDR
- [ ] Public and private subnets (both AZs)
- [ ] Route tables and Internet Gateway
- [ ] NAT Gateway
- [ ] ECS cluster and services
- [ ] ECR repositories and image tags (commit SHAs)
- [ ] Security groups (all four)
- [ ] ALB listener, target group, healthy targets
- [ ] RDS instance: subnet group, encryption, public access "No"
- [ ] CloudWatch logs and at least one alarm
- [ ] Successful GitHub Actions run
- [ ] Browser screenshot of the running app on the ALB URL
- [ ] Test output (Playwright report or pytest output)

**Tip:** Put the account ID and any keys out of view before screenshotting. Crop the browser URL bar if it shows private information.

---

## Step 14: Testing evidence

**Do**
1. Run the existing Playwright suite (in `mediconnect_testing/`) against the ALB URL instead of localhost. Set the base URL in `conftest.py`, then run:
   ```bash
   pytest -v --html=report.html
   ```
   Keep the report. The suite already covers functional, navigation, API, form, responsive, performance, accessibility and network mocking, which maps well to plan Phase 8.
2. Run a smoke check against the deployed API: `curl https://<alb>/api/health` (or `/api/` for the root).
3. Record that the tests cover role separation, invalid login, and appointment creation. Use the test names as evidence.

**Done when:** The test run against the deployed URL passes, and you have the report.

**Note:** There is no backend test suite yet. Be honest about this in the report. The backend is checked with compile checks, the migration run, the health checks and the Playwright API tests.

---

## Step 15: The report (Deliverable 4, 4 to 6 pages)

Use the 14 sections from plan Phase 9. Page budget (approximate):

| # | Section | Pages |
|---|---|---|
| 1 | Introduction and problem | 0.3 |
| 2 | Application overview | 0.3 |
| 3 | Cloud provider choice (AWS, ap-south-1, why) | 0.4 |
| 4 | Three-tier architecture and network (include diagram) | 0.8 |
| 5 | Containerisation (Dockerfiles, Nginx, compose) | 0.5 |
| 6 | Database and migrations (create_all removed, Alembic) | 0.3 |
| 7 | Registry and CI/CD workflow (include the workflow file summary) | 0.6 |
| 8 | Security controls (SGs, IAM, Secrets Manager, OIDC) | 0.5 |
| 9 | Load balancing, scaling, reliability | 0.5 |
| 10 | Enhancements and cost estimate | 0.4 |
| 11 | Testing and deployment evidence (screenshots) | 0.5 |
| 12 | **NFR justification** (see below) | **1.0** |
| 13 | Limitations and future improvements | 0.4 |
| 14 | Conclusion | 0.2 |

### Section 12: NFR justification (the part most likely to lose marks)

For each NFR, write three things: **the decision**, **the mechanism**, and **the evidence**. Tie each to a real choice in your build. Use this table as the skeleton:

| NFR | Decision in your build | Evidence to cite |
|---|---|---|
| Scalability | Stateless containers; ECS service with 2+ tasks behind the ALB and Service Connect | Target group with 2 targets; service desired count |
| Availability / Reliability | Two AZs; health checks; ECS replaces failed tasks; RDS managed (Multi-AZ if enabled) | Step 10 replacement screenshot; RDS config |
| Elasticity | Target tracking autoscaling on CPU | Scaling policy; scale-out event from load test |
| Security | Public ALB only; private tasks and RDS; tier SGs; Secrets Manager; OIDC deploy role | SG screenshots; RDS public access "No" |
| Maintainability / Deployability | Docker images; Terraform; CI/CD on every merge; circuit breaker rollback | Green workflow run; ECS deployment events |
| Performance / Latency | ALB distribution; Nginx serving static files; region close to users (ap-south-1) | Load test latency numbers |
| Cost-Efficiency | Fargate right-sizing; log retention; single NAT; cost estimate with 2 optimisations | Pricing Calculator summary |
| Portability | Docker images run identically through Compose; Terraform variables; standard PostgreSQL | `docker compose up` screenshot; repo structure |

**Known limitations** (state them honestly; the plan asks for this and markers reward it):
- Single region: this is not disaster recovery across regions.
- One NAT Gateway: if its AZ fails, private outbound traffic stops.
- If RDS is single-AZ, the database is a single point of failure.
- Rate limiting uses `slowapi`. Check `backend/src/utils/limiter.py`: if it uses in-memory storage (the default), each task keeps its own counter, so limits are not shared across tasks. Name this as a limitation, or move the storage to Redis.
- No HTTPS without a domain (state it, or add an ACM certificate if you have one).
- Stripe, Cloudinary, email and Gemini depend on third-party services.
- No backend unit tests yet; coverage is through Playwright and the deployment checks.
- Secrets rotation is manual.

---

## Step 16: Final checklist before submission

**Source files (Deliverable 3)**
- [ ] `backend/Dockerfile` and `backend/.dockerignore`
- [ ] `frontend/Dockerfile`, `frontend/nginx.conf`, `frontend/.dockerignore`
- [ ] Root `docker-compose.yml`
- [ ] `infrastructure/` Terraform folder (with `terraform.tfvars.example`, no real values)
- [ ] `.github/workflows/ci-cd.yml`
- [ ] Repository link (make sure the repo is accessible to your marker)

**Definition of Done (from the plan)**
- [ ] App runs locally with `docker compose up`
- [ ] Images are pushed to ECR with commit tags
- [ ] VPC has public and private layers
- [ ] Web tier is reachable through the ALB
- [ ] App tier is private
- [ ] PostgreSQL is private and migrations run
- [ ] No secrets in git, images or logs (check `docker history` and the CloudWatch logs)
- [ ] CI/CD tests, builds, pushes, deploys, verifies
- [ ] Health checks, logs and one alarm work
- [ ] Scaling and load balancing are documented and demonstrated
- [ ] Diagram and screenshots are collected
- [ ] Report has the NFR section and the limitations

**Before you leave the project**
- [ ] Run `terraform destroy` once evidence is captured
- [ ] Check the AWS Billing console for any running resources (NAT Gateways and ALBs cost money even when idle)

---

## Order of work (suggested timeline)

| Stage | Steps | Working time (estimate) |
|---|---|---|
| Secure and clean up | 1, 2, 3 | 1 to 2 days |
| Containers locally | 4 | 1 to 2 days |
| Cloud foundation | 5, 6 | 2 to 3 days |
| Compute and load balancer | 7, 8 | 2 to 3 days |
| CI/CD | 9 | 1 to 2 days |
| Testing and scaling | 10, 14 | 1 day |
| Enhancements, cost, diagram | 11, 12 | 1 day |
| Evidence and report | 13, 15, 16 | 2 to 3 days |

Work in this order. Each step depends on the one before it, and the screenshots are easiest to take at the moment you complete a step.
