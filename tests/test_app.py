import pytest

TOKEN = "test-token"
GOOD = {"date": "01-10-26", "sleep": "23:00", "wake": "07:00", "quality": 80}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # empty database for every test 
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    import app
    monkeypatch.setattr(app, "ADMIN_TOKEN", TOKEN)
    app.storage.init()
    app.app.config["TESTING"] = True
    return app.app.test_client()


def admin(headers=None):
    """Headers with the admin token."""
    result = {"X-Admin-Token": TOKEN}
    result.update(headers or {})
    return result


def test_add_and_list(client):
    r = client.post("/records", json=GOOD)
    assert r.status_code == 201
    assert "id" in r.get_json()
    r = client.get("/records")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["factor"] == "без фактора"


def test_add_with_factor(client):
    client.post("/records", json={**GOOD, "factor": "кава"})
    assert client.get("/records").get_json()[0]["factor"] == "кава"


def test_add_rejects_bad_date_format(client):
    r = client.post("/records", json={**GOOD, "date": "2026-10-01"})
    assert r.status_code == 400


def test_add_rejects_text_quality(client):
    r = client.post("/records", json={**GOOD, "quality": "abc"})
    assert r.status_code == 400


def test_add_rejects_quality_out_of_range(client):
    assert client.post("/records", json={**GOOD, "quality": 0}).status_code == 400
    assert client.post("/records", json={**GOOD, "quality": 101}).status_code == 400


def test_add_rejects_missing_field(client):
    bad = dict(GOOD)
    del bad["wake"]
    assert client.post("/records", json=bad).status_code == 400


def test_add_rejects_empty_factor(client):
    assert client.post("/records", json={**GOOD, "factor": "  "}).status_code == 400


def test_add_rejects_sql_injection_text(client):
    r = client.post("/records", json={**GOOD, "date": "'; DROP TABLE records; --"})
    assert r.status_code == 400
    assert client.get("/records").status_code == 200  # table is still there 


def test_filter_by_quality(client):
    client.post("/records", json={**GOOD, "quality": 30})
    client.post("/records", json={**GOOD, "quality": 90})
    r = client.get("/records?min_quality=50&max_quality=100")
    assert [x["quality"] for x in r.get_json()] == [90]
    assert client.get("/records?min_quality=a&max_quality=b").status_code == 400


def test_admin_delete_requires_token(client):
    client.post("/records", json=GOOD)
    assert client.delete("/admin/records/1").status_code == 403
    assert client.delete("/admin/records/1", headers={"X-Admin-Token": "wrong"}).status_code == 403
    assert len(client.get("/records").get_json()) == 1  # record is still there 


def test_admin_delete_missing_returns_404(client):
    assert client.delete("/admin/records/999", headers=admin()).status_code == 404


def test_admin_rejects_requests_through_tunnel(client):
    client.post("/records", json=GOOD)
    tunnel = admin({"Cf-Connecting-Ip": "203.0.113.5"})
    assert client.delete("/admin/records/1", headers=tunnel).status_code == 403
    assert client.get("/admin/export", headers=tunnel).status_code == 403
    assert len(client.get("/records").get_json()) == 1


def test_public_delete_route_does_not_exist(client):
    client.post("/records", json=GOOD)
    assert client.delete("/records/1").status_code in (404, 405)
    assert len(client.get("/records").get_json()) == 1


def test_delete_is_written_to_audit_log(client):
    client.post("/records", json=GOOD)
    assert client.delete("/admin/records/1", headers=admin()).status_code == 200
    r = client.get("/admin/log", headers=admin())
    assert r.status_code == 200
    assert [x["action"] for x in r.get_json()] == ["delete", "add"]


def test_admin_log_requires_token_and_valid_limit(client):
    assert client.get("/admin/log").status_code == 403
    assert client.get("/admin/log?limit=abc", headers=admin()).status_code == 400


def test_factor_report_through_api(client):
    client.post("/records", json={**GOOD, "quality": 40, "factor": "кава"})
    client.post("/records", json={**GOOD, "quality": 60, "factor": "кава"})
    client.post("/records", json={**GOOD, "quality": 90, "factor": "спорт"})
    r = client.get("/report/factors")
    assert r.status_code == 200
    assert r.get_json()[0] == {"factor": "спорт", "nights": 1, "avg_quality": 90.0}
    assert r.get_json()[1] == {"factor": "кава", "nights": 2, "avg_quality": 50.0}
