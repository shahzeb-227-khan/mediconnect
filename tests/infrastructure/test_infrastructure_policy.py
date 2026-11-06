"""Policy tests: the Terraform files, Dockerfiles and pipeline must keep the
security and reliability decisions that the CEA report claims.

These read the files as text, so they need no AWS access and no extra libraries.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INFRA = ROOT / "infrastructure"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def block(text, resource_type, name):
    """Return the text of one `resource "type" "name" { ... }` block."""
    match = re.search(rf'resource "{resource_type}" "{name}" \{{', text)
    assert match, f"resource {resource_type}.{name} not found"
    rest = text[match.start():]
    nxt = re.search(r'\n(resource|data|variable|output|locals)\b', rest[10:])
    return rest if not nxt else rest[: nxt.start() + 10]


def ingress_blocks(sg_block):
    return re.findall(r"ingress \{.*?\n  \}", sg_block, flags=re.S)


# ---------- network ----------
def test_vpc_uses_expected_cidr_and_two_azs():
    variables = read(INFRA / "variables.tf")
    assert '"10.0.0.0/16"' in variables
    assert '"ap-south-1a"' in variables and '"ap-south-1b"' in variables


def test_six_subnets_exist_for_three_tiers():
    net = read(INFRA / "networking.tf")
    for tier in ("public", "app", "db"):
        assert f'resource "aws_subnet" "{tier}"' in net
    variables = read(INFRA / "variables.tf")
    for name in ("public_subnet_cidrs", "app_subnet_cidrs", "db_subnet_cidrs"):
        assert name in variables


def test_public_route_table_goes_to_internet_gateway():
    public = block(read(INFRA / "networking.tf"), "aws_route_table", "public")
    assert "aws_internet_gateway.main.id" in public


def test_app_route_table_goes_through_nat_gateway():
    app = block(read(INFRA / "networking.tf"), "aws_route_table", "app")
    assert "aws_nat_gateway.main.id" in app
    assert "aws_internet_gateway" not in app


def test_database_route_table_has_no_internet_route():
    db = block(read(INFRA / "networking.tf"), "aws_route_table", "db")
    assert "route {" not in db
    assert "0.0.0.0/0" not in db


def test_nat_gateway_sits_in_a_public_subnet():
    nat = block(read(INFRA / "networking.tf"), "aws_nat_gateway", "main")
    assert "aws_subnet.public[0].id" in nat


# ---------- security groups ----------
def test_only_the_load_balancer_allows_internet_ingress():
    sec = read(INFRA / "security.tf")
    for name in ("frontend", "backend", "rds"):
        for rule in ingress_blocks(block(sec, "aws_security_group", name)):
            assert "0.0.0.0/0" not in rule, f"{name} security group is open to the internet"
    alb_rules = ingress_blocks(block(sec, "aws_security_group", "alb"))
    assert any("0.0.0.0/0" in rule and "80" in rule for rule in alb_rules)


def test_tiers_are_chained_security_group_to_security_group():
    sec = read(INFRA / "security.tf")
    expectations = {
        "frontend": ("aws_security_group.alb.id", "80"),
        "backend": ("aws_security_group.frontend.id", "8000"),
        "rds": ("aws_security_group.backend.id", "5432"),
    }
    for name, (source, port) in expectations.items():
        rules = ingress_blocks(block(sec, "aws_security_group", name))
        assert len(rules) == 1, f"{name} should have exactly one ingress rule"
        assert source in rules[0]
        assert re.search(rf"from_port\s*=\s*{port}\b", rules[0])
        assert re.search(rf"to_port\s*=\s*{port}\b", rules[0])


# ---------- database ----------
def test_database_is_private_and_encrypted():
    rds = block(read(INFRA / "rds.tf"), "aws_db_instance", "main")
    assert re.search(r"publicly_accessible\s*=\s*false", rds)
    assert re.search(r"storage_encrypted\s*=\s*true", rds)
    assert 'engine                  = "postgres"' in rds or re.search(r'engine\s*=\s*"postgres"', rds)


def test_database_password_is_generated_not_hardcoded():
    rds = block(read(INFRA / "rds.tf"), "aws_db_instance", "main")
    assert "random_password.db.result" in rds
    assert not re.search(r'password\s*=\s*"[^"$]', rds)


def test_database_credentials_are_stored_in_secrets_manager():
    rds = read(INFRA / "rds.tf")
    assert 'resource "aws_secretsmanager_secret" "database"' in rds
    assert 'resource "aws_secretsmanager_secret_version" "database"' in rds


# ---------- registry ----------
def test_ecr_repositories_are_immutable_scanned_and_encrypted():
    ecr = read(INFRA / "ecr.tf")
    assert ecr.count('image_tag_mutability = "IMMUTABLE"') == 2
    assert ecr.count("scan_on_push = true") == 2
    assert ecr.count('encryption_type = "AES256"') == 2


# ---------- compute ----------
def test_containers_have_no_public_ip():
    ecs = read(INFRA / "ecs.tf")
    assert ecs.count("assign_public_ip = false") == 2
    assert "assign_public_ip = true" not in ecs


def test_services_roll_back_automatically_on_failed_deployments():
    ecs = read(INFRA / "ecs.tf")
    assert ecs.count("deployment_circuit_breaker") == 2
    assert ecs.count("rollback = true") == 2


def test_load_balancer_is_internet_facing_with_health_checked_target_group():
    ecs = read(INFRA / "ecs.tf")
    assert re.search(r"internal\s*=\s*false", block(ecs, "aws_lb", "main"))
    assert "health_check" in block(ecs, "aws_lb_target_group", "frontend")


def test_logs_go_to_cloudwatch_with_retention():
    ecs = read(INFRA / "ecs.tf")
    assert ecs.count('logDriver = "awslogs"') == 2
    assert ecs.count("retention_in_days = 7") == 2


def test_backend_secrets_are_injected_from_secrets_manager():
    ecs = read(INFRA / "ecs.tf")
    for key in ("JWT_SECRET_KEY", "STRIPE_SECRET_KEY", "GEMINI_API_KEY", "MAIL_PASSWORD"):
        assert f'"{key}"' in ecs
    assert "valueFrom" in ecs


# ---------- IAM ----------
def test_github_trust_policy_is_limited_to_this_repository():
    cicd = read(INFRA / "cicd.tf")
    sub = re.search(r'"token.actions.githubusercontent.com:sub"\s*=\s*"([^"]+)"', cicd)
    assert sub, "OIDC subject condition missing"
    assert sub.group(1).startswith("repo:shahzeb-227-khan")
    assert sub.group(1) != "repo:*"
    assert "sts.amazonaws.com" in cicd


def test_deploy_role_uses_no_wildcard_actions():
    cicd = read(INFRA / "cicd.tf")
    actions = re.findall(r'"([a-z0-9-]+:[A-Za-z0-9*]+)"', cicd)
    assert actions, "no IAM actions found"
    assert not [a for a in actions if a.endswith(":*")], "wildcard IAM action found"


def test_pass_role_is_restricted_to_ecs_tasks():
    cicd = read(INFRA / "cicd.tf")
    assert "iam:PassRole" in cicd
    assert '"iam:PassedToService" = "ecs-tasks.amazonaws.com"' in cicd


def test_no_access_keys_committed_in_infrastructure_files():
    pattern = re.compile(r"AKIA[0-9A-Z]{16}")
    for path in list(INFRA.glob("*.tf")) + [ROOT / ".github" / "workflows" / "ci-cd.yml"]:
        assert not pattern.search(read(path)), f"AWS access key found in {path.name}"


# ---------- containers ----------
def test_backend_image_runs_as_non_root_with_healthcheck():
    dockerfile = read(ROOT / "backend" / "Dockerfile")
    assert re.search(r"^USER appuser", dockerfile, flags=re.M)
    assert "HEALTHCHECK" in dockerfile


def test_frontend_image_is_a_multi_stage_build():
    dockerfile = read(ROOT / "frontend" / "Dockerfile")
    assert dockerfile.count("FROM ") == 2
    assert "COPY --from=build" in dockerfile


def test_compose_file_defines_all_three_tiers():
    compose = read(ROOT / "docker-compose.yml")
    for service in ("db:", "backend:", "frontend:"):
        assert re.search(rf"^  {service}", compose, flags=re.M)


# ---------- pipeline ----------
def test_pipeline_runs_build_then_test_then_deploy():
    workflow = read(ROOT / ".github" / "workflows" / "ci-cd.yml")
    jobs = re.findall(r"^  (build|test|deploy):", workflow, flags=re.M)
    assert jobs == ["build", "test", "deploy"]
    deploy = workflow[workflow.index("\n  deploy:"):]
    needs = re.search(r"needs:\s*\[([^\]]*)\]", deploy)
    assert needs, "deploy job must declare needs"
    assert {"build", "test"} <= {n.strip() for n in needs.group(1).split(",")}


def test_pipeline_deploys_only_from_main():
    workflow = read(ROOT / ".github" / "workflows" / "ci-cd.yml")
    deploy = workflow[workflow.index("\n  deploy:"):]
    assert "refs/heads/main" in deploy


def test_pipeline_uses_oidc_instead_of_stored_keys():
    workflow = read(ROOT / ".github" / "workflows" / "ci-cd.yml")
    assert "id-token: write" in workflow
    assert "role-to-assume" in workflow
    assert "AWS_ACCESS_KEY_ID" not in workflow
    assert "AWS_SECRET_ACCESS_KEY" not in workflow
