from httpx import AsyncClient


async def test_create_key(client: AsyncClient):
    resp = await client.post("/v1/keys", json={"email": "new@example.com"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["api_key"].startswith("gn_")
    assert data["email"] == "new@example.com"
    assert data["tier"] == "free"
    assert data["replaced"] is False


async def test_create_key_invalid_email(client: AsyncClient):
    resp = await client.post("/v1/keys", json={"email": "not-an-email"})
    assert resp.status_code == 422


async def test_create_key_replaces_old(client: AsyncClient):
    resp1 = await client.post("/v1/keys", json={"email": "dup@example.com"})
    key1 = resp1.json()["data"]["api_key"]
    assert resp1.json()["data"]["replaced"] is False

    resp2 = await client.post("/v1/keys", json={"email": "dup@example.com"})
    key2 = resp2.json()["data"]["api_key"]
    assert resp2.json()["data"]["replaced"] is True
    assert key2 != key1

    # old key should be disabled
    resp = await client.get("/v1/people", headers={"X-API-Key": key1}, params={"limit": 1})
    assert resp.status_code == 401

    # new key should work
    resp = await client.get("/v1/people", headers={"X-API-Key": key2}, params={"limit": 1})
    assert resp.status_code == 200


async def test_create_key_works_immediately(client: AsyncClient):
    resp = await client.post("/v1/keys", json={"email": "fresh@example.com"})
    key = resp.json()["data"]["api_key"]

    resp = await client.get("/v1/meta", headers={"X-API-Key": key})
    assert resp.status_code == 200
