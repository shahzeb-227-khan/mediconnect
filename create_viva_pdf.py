from pathlib import Path
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Preformatted,
)


OUTPUT = Path("MediConnect_CEA_Viva_Explanation_Script.pdf")

CONTENT = r"""
# MediConnect CEA Viva and Presentation Script

## 1. CEA statement kya tha?

CEA ka matlab Complex Engineering Activity hai. Is project mein requirement thi ke ek existing web application ko cloud par deploy kiya jaye as a three-tier application.

Three tiers:

1. Web tier — frontend
2. Application tier — backend/business logic
3. Database tier — PostgreSQL database

CEA requirements:

- VPC/network banana
- Public aur private subnets use karna
- Frontend ko Docker container mein run karna
- Backend ko private subnet mein run karna
- Managed database use karna
- Container images registry mein push karna
- Load balancer lagana
- CI/CD pipeline banana
- Security groups aur secrets implement karna
- Scaling/reliability demonstrate karna
- CloudWatch monitoring use karna
- Architecture diagram aur technical report submit karna

Maine AWS ko cloud provider choose kiya aur Mumbai region ap-south-1 use kiya.

## 2. Original MediConnect project

MediConnect ek full-stack hospital appointment application hai.

Patient portal:
- Doctors search karna
- Hospitals browse karna
- Appointment book karna
- Token number dekhna
- Appointment history aur reviews

Doctor portal:
- Signup karna
- Hospital ke liye apply karna
- Fee aur availability manage karna
- Appointments dekhna

Admin portal:
- Cities, specializations aur hospitals manage karna
- Doctors approve/reject karna
- Appointments monitor karna

## 3. Original architecture

    React Frontend
           |
           v
    FastAPI Backend
           |
           v
    PostgreSQL Database

Frontend React/Vite mein tha. Backend FastAPI aur SQLAlchemy par based tha. Database PostgreSQL tha. Initially production network separation, Docker, AWS infrastructure, load balancing aur CI/CD missing thay.

## 4. Database

MediConnect mein PostgreSQL database use hua. Production mein PostgreSQL ko Amazon RDS par deploy kiya gaya:

- PostgreSQL engine
- db.t3.micro instance
- Encrypted storage
- Private database subnets
- Public access disabled
- Backend security group se port 5432 access

Database schema Alembic migrations se manage hota hai:

    alembic upgrade head

Pehle Base.metadata.create_all() use ho raha tha. Production ke liye isay remove karke Alembic ko schema-management ka single source banaya gaya.

## 5. Final AWS architecture

    Internet
       |
       v
    Application Load Balancer
       |
       v
    Frontend ECS Fargate Task
    (Nginx + React)
       |
       v
    Backend ECS Fargate Task
    (FastAPI)
       |
       v
    Amazon RDS PostgreSQL

Supporting services:

    GitHub Actions -> GitHub OIDC -> IAM Role -> ECR -> ECS
    ECS Tasks -> Secrets Manager
    ECS Tasks -> CloudWatch Logs

## 6. VPC and networking

VPC CIDR:

    10.0.0.0/16

Public subnets contain the internet-facing ALB and NAT Gateway connectivity. Private application subnets contain frontend and backend ECS tasks. Private database subnets contain RDS PostgreSQL.

Internet Gateway public subnet ko internet access deta hai. NAT Gateway private tasks ko outbound internet access deta hai without allowing inbound internet traffic.

## 7. Security groups

- ALB: Internet to ALB on port 80
- Frontend: ALB to frontend on port 80
- Backend: frontend to backend on port 8000
- RDS: backend to database on port 5432

Har tier ka separate security group least-privilege model provide karta hai.

## 8. Frontend deployment

Frontend React/Vite application hai. Dockerfile Node build stage aur Nginx production stage use karta hai. Nginx static files serve karta hai, SPA routing handle karta hai aur /api requests backend service ko forward karta hai.

## 9. Backend deployment

Backend FastAPI application private application subnet mein port 8000 par run hota hai. Startup par Alembic migrations run hoti hain, phir Uvicorn start hota hai.

Health endpoints:

    /health
    /health/db

## 10. ECR

Do ECR repositories banayi gayi:

    mediconnect-frontend
    mediconnect-backend

Images commit SHA tags ke saath push hoti hain. Isse har deployment traceable hota hai aur previous version rollback ho sakta hai.

## 11. ECS Fargate

Fargate use karne se EC2 servers, operating system patching aur capacity management ki zaroorat nahi rahi. Containers private subnets mein managed way se run hote hain.

## 12. Load balancer

Application Load Balancer public entry point hai. ALB healthy frontend task ko traffic forward karta hai aur unhealthy task ko traffic nahi deta. Target group tasks ki health track karti hai.

## 13. CI/CD pipeline

    Developer git push
            |
            v
    GitHub Actions
            |
            v
    Frontend lint/build
            |
            v
    Backend compile check
            |
            v
    OIDC authentication
            |
            v
    ECR login and image build
            |
            v
    Push images and update ECS
            |
            v
    Wait for stability and ALB health check

Pipeline frontend validation, backend compilation, Docker image build, ECR push, ECS deployment, service stability wait aur ALB health check perform karti hai.

## 14. OIDC kyun?

Long-lived AWS access keys GitHub mein store karna risky hota. GitHub OIDC short-lived token generate karta hai. IAM trust policy repository ko verify karke temporary role credentials issue karti hai. Permanent AWS keys GitHub mein store nahi ki gayi.

## 15. OIDC error

Initial error:

    Could not assume role with OIDC
    Not authorized to perform sts:AssumeRoleWithWebIdentity

Reason GitHub token ka subject IAM trust policy ke expected subject se match nahi kar raha tha. Trust policy ko repository-scoped subject par correct kiya gaya:

    repo:shahzeb-227-khan/mediconnect:*

## 16. Blank white screen error

Browser error:

    Uncaught TypeError: t.map is not a function

React array expect kar raha tha lekin API response object/error response tha. extractList helper add karke Landing, Search, Hospitals, Hospital Detail aur Doctor Signup responses normalize kiye gaye. Invalid response par empty array use hoti hai, isliye page blank nahi hota.

## 17. Hospitals and login error

Nginx variable-based proxy_pass request path ko wrong rewrite kar raha tha. /api/hospitals backend ke / path par ja raha tha aur POST login ko 405 Method Not Allowed mil raha tha.

Fix:

    rewrite ^/api/(.*)$ /$1 break;
    proxy_pass $backend;

Ab /api/patients/login backend ke /patients/login endpoint par correctly forward hota hai.

## 18. Empty database

Migrations tables create karti hain, sample data nahi. Isliye initial dashboard counters zero thay.

Correct demo flow:

1. City create
2. Specialization create
3. Hospital create
4. Doctor signup
5. Doctor hospital application
6. Admin approval
7. Patient signup/login
8. Appointment booking

## 19. Email error

CloudWatch error:

    SMTPServerDisconnected: Connection lost

Likely causes SMTP credentials, Gmail App Password, port, server ya ECS old secret. Correct Gmail settings:

    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_STARTTLS=True
    MAIL_SSL_TLS=False

Secret update ke baad ECS force new deployment required hoti hai because secrets task startup par load hoti hain.

## 20. ORIGIN_URL error

Email links pehle http://localhost use kar rahe thay. ECS configuration mein ORIGIN_URL ko ALB DNS se dynamic kiya gaya:

    http://${aws_lb.main.dns_name}

## 21. Secrets Manager

Secrets Manager mein JWT secret, admin credentials, mail credentials, Cloudinary, Stripe, Gemini aur database credentials rakhe gaye. ECS task definition runtime par secrets inject karti hai. Secrets source code, GitHub ya Docker image mein hardcode nahi hain.

## 22. CloudWatch

CloudWatch log groups:

    /ecs/mediconnect-cea/frontend
    /ecs/mediconnect-cea/backend

CloudWatch se startup, migrations, SMTP errors, application errors aur deployment health inspect ki gayi.

## 23. Scaling and reliability

ECS task stop karne par service replacement task launch karti hai. Desired count maintain hota hai aur new task ALB target group mein healthy hota hai. Desired count temporarily 2 karke multiple healthy targets aur traffic distribution demonstrate ki gayi.

Viva mein manual scale-out ko automatic CPU autoscaling na bolain jab tak policy ka actual proof available na ho.

## 24. AWS Console, Terraform and CLI

Terraform infrastructure creation ke liye use hua because it is repeatable, reviewable aur version-controlled. AWS CLI operational verification aur force deployment ke liye use hui. AWS Console visual inspection aur screenshots ke liye use hua.

Best approach:

    Terraform = infrastructure
    GitHub Actions = automated deployment
    AWS CLI = verification/operations
    AWS Console = inspection/screenshots

## 25. Security summary

- Private RDS
- Private ECS tasks
- Public ALB only
- Tier-specific security groups
- Secrets Manager
- GitHub OIDC
- No permanent AWS keys in GitHub
- ECR image scanning and immutable tags
- Health checks
- JWT authentication
- Role-separated portals

## 26. CEA completion

Completed: application, PostgreSQL, Docker, Compose, VPC, subnets, IGW, NAT, security groups, RDS, ECR, ECS Fargate, ALB, CloudWatch, Secrets Manager, OIDC, GitHub Actions, CI/CD, reliability evidence, architecture diagram, technical report and screenshot evidence.

## 27. Honest limitations

- Single AWS region
- HTTP ALB without a production domain/ACM certificate
- One NAT Gateway
- RDS single-AZ configuration
- Third-party dependencies for email, Stripe, Cloudinary and Gemini
- Manual secrets rotation
- Limited backend unit-test coverage
- Demo data initially had to be added manually

## 28. Final viva answer

MediConnect is a React and FastAPI hospital appointment application backed by PostgreSQL. I converted it into a secure three-tier AWS deployment. The frontend is containerized with Nginx and deployed on ECS Fargate behind an internet-facing Application Load Balancer. The FastAPI backend runs in private application subnets, while PostgreSQL runs privately on Amazon RDS. Images are stored in Amazon ECR. Terraform provisions the infrastructure, GitHub Actions builds and deploys images using GitHub OIDC, and CloudWatch collects container logs. Security is implemented through private subnets, tier-specific security groups, Secrets Manager, encrypted RDS storage, and short-lived OIDC credentials. ECS health checks and task replacement provide reliability, while scaling was demonstrated by running multiple tasks behind the ALB.

## 29. Presentation sequence

1. CEA statement
2. Original MediConnect
3. Three-tier architecture
4. Database
5. VPC and subnets
6. Security groups
7. Docker
8. ECR
9. ECS/Fargate
10. ALB
11. RDS
12. Secrets Manager
13. CloudWatch
14. GitHub OIDC
15. CI/CD
16. Errors and fixes
17. Scaling/self-healing
18. NFRs
19. Limitations
20. Live deployed demo
"""


def build() -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=24, spaceAfter=18
    )
    heading = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], fontSize=14, leading=18, spaceBefore=12, spaceAfter=8
    )
    body = ParagraphStyle(
        "BodyCustom", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=6
    )
    code = ParagraphStyle(
        "CodeCustom", parent=styles["Code"], fontName="Courier", fontSize=8, leading=10, leftIndent=12,
        backColor="#F2F2F2", borderPadding=6, spaceBefore=4, spaceAfter=8,
    )

    story = []
    for block in CONTENT.strip().split("\n\n"):
        lines = block.splitlines()
        first = lines[0].strip()
        if first.startswith("# "):
            story.append(Paragraph(first[2:], title))
        elif first.startswith("## "):
            story.append(Paragraph(first[3:], heading))
        elif all(line.startswith(("    ", "- ", "1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "9. ")) for line in lines):
            story.append(Preformatted("\n".join(line[4:] if line.startswith("    ") else line for line in lines), code))
        elif first.startswith("- ") or first[:2].isdigit():
            story.append(Paragraph("<br/>".join(line.replace("&", "&amp;") for line in lines), body))
        else:
            text = "<br/>".join(line.replace("&", "&amp;") for line in lines)
            story.append(Paragraph(text, body))
        story.append(Spacer(1, 4))

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="MediConnect CEA Viva and Presentation Script",
    )
    document.build(story)
    print(OUTPUT.resolve())


if __name__ == "__main__":
    build()
