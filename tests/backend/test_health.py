def test_root_reports_running(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "MediConnect API is running"}


def test_health_endpoint_used_by_alb_and_pipeline(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_reaches_postgres(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404
