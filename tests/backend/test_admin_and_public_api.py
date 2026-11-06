"""Admin management and the public catalogue endpoints used by the web tier."""


def test_catalogue_is_empty_at_start(client):
    assert client.get("/cities").json() == []
    assert client.get("/specializations").json() == []
    hospitals = client.get("/hospitals").json()
    assert hospitals["total"] == 0 and hospitals["items"] == []


def test_admin_login_succeeds_with_configured_credentials(client):
    response = client.post("/admin/login", json={"email": "admin@mediconnect-demo.com", "password": "AdminPass123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_admin_login_rejects_wrong_password(client):
    response = client.post("/admin/login", json={"email": "admin@mediconnect-demo.com", "password": "nope"})
    assert response.status_code == 401


def test_admin_routes_require_a_token(client):
    assert client.post("/admin/cities", json={"name": "Karachi"}).status_code in (401, 403)


def test_patient_token_cannot_use_admin_routes(client, patient_headers):
    response = client.post("/admin/cities", json={"name": "Karachi"}, headers=patient_headers)
    assert response.status_code == 403


def test_admin_creates_city_and_public_list_shows_it(client, admin_headers):
    created = client.post("/admin/cities", json={"name": "Karachi", "province": "Sindh"}, headers=admin_headers)
    assert created.status_code == 200
    assert created.json()["name"] == "Karachi"
    public = client.get("/cities").json()
    assert [c["name"] for c in public] == ["Karachi"]


def test_duplicate_city_ignores_letter_case(client, admin_headers):
    client.post("/admin/cities", json={"name": "Karachi"}, headers=admin_headers)
    duplicate = client.post("/admin/cities", json={"name": "KARACHI"}, headers=admin_headers)
    assert duplicate.status_code == 400


def test_admin_creates_specialization(client, admin_headers):
    created = client.post("/admin/specializations", json={"name": "Cardiology"}, headers=admin_headers)
    assert created.status_code == 200
    assert [s["name"] for s in client.get("/specializations").json()] == ["Cardiology"]


def _make_hospital(client, headers, name="Aga Khan Hospital"):
    city = client.post("/admin/cities", json={"name": "Karachi"}, headers=headers).json()
    response = client.post(
        "/admin/hospitals",
        json={"name": name, "address": "Stadium Road", "city_id": city["id"]},
        headers=headers,
    )
    return city, response


def test_admin_creates_hospital_and_public_can_read_it(client, admin_headers):
    city, created = _make_hospital(client, admin_headers)
    assert created.status_code == 200
    hospital_id = created.json()["id"]

    listing = client.get("/hospitals").json()
    assert listing["total"] == 1
    assert listing["items"][0]["name"] == "Aga Khan Hospital"

    single = client.get(f"/hospitals/{hospital_id}")
    assert single.status_code == 200
    assert single.json()["name"] == "Aga Khan Hospital"


def test_hospital_search_and_city_filter(client, admin_headers):
    city, _ = _make_hospital(client, admin_headers)
    assert client.get("/hospitals", params={"search": "aga"}).json()["total"] == 1
    assert client.get("/hospitals", params={"search": "zzz"}).json()["total"] == 0
    assert client.get("/hospitals", params={"city_id": city["id"]}).json()["total"] == 1
    assert client.get("/hospitals", params={"city_id": city["id"] + 99}).json()["total"] == 0


def test_hospital_with_unknown_city_is_rejected(client, admin_headers):
    response = client.post(
        "/admin/hospitals",
        json={"name": "Ghost Hospital", "address": "Nowhere", "city_id": 9999},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_missing_hospital_returns_404(client):
    assert client.get("/hospitals/9999").status_code == 404


def test_hospital_with_no_doctors_returns_empty_page(client, admin_headers):
    _, created = _make_hospital(client, admin_headers)
    response = client.get(f"/hospitals/{created.json()['id']}/doctors")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_pagination_limit_is_validated(client):
    assert client.get("/hospitals", params={"limit": 0}).status_code == 422
    assert client.get("/hospitals", params={"skip": -1}).status_code == 422
