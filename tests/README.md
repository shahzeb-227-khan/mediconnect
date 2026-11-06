# Automated tests

These tests run in the CI/CD pipeline (`.github/workflows/ci-cd.yml`) in the
order **build, then test, then deploy**. The deploy job only runs when both the
build and the test jobs pass.

| Folder | What it tests | Runner |
|---|---|---|
| `backend/` | FastAPI application against a real PostgreSQL database: health endpoints, authentication helpers, input validation, patient signup and login, admin management, public hospital catalogue | pytest |
| `frontend/` | Frontend helper functions (dates, API helpers, token storage) and the Nginx configuration that fixed the 504 and `/api` bugs | Node built-in test runner |
| `infrastructure/` | Security and reliability rules in the Terraform files, Dockerfiles and pipeline (private database, tier-to-tier security groups, no public IPs, least privilege IAM, build then test then deploy) | pytest |

## Run locally

Backend and infrastructure tests (from the repository root):

```
pip install -r backend/requirements.txt -r tests/requirements-test.txt
set TEST_DATABASE_URL=postgresql+psycopg2://internship_user:internship_pass@localhost:5432/mediconnect_test
python -m pytest tests -c tests/pytest.ini -v
```

The backend tests need a PostgreSQL database whose name contains `test`
(for example `docker compose up -d db`, then create `mediconnect_test`). The
fixtures create and drop all tables in that database, so the name check stops
them from touching a real database.

Infrastructure tests alone (no database needed):

```
python -m pytest tests/infrastructure -c tests/pytest.ini -v
```

Frontend tests (Node 22):

```
node --test tests/frontend
```
