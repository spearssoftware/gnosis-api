import pytest
from httpx import AsyncClient


async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Gnosis API" in resp.json()["message"]


async def test_no_api_key(client: AsyncClient):
    resp = await client.get("/v1/people")
    assert resp.status_code in (401, 403, 422)


async def test_bad_api_key(client: AsyncClient):
    resp = await client.get("/v1/people", headers={"X-API-Key": "bad-key"})
    assert resp.status_code == 401


async def test_list_people(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/people", headers={"X-API-Key": api_key}, params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["limit"] == 5
    assert len(body["data"]) <= 5
    if body["data"]:
        person = body["data"][0]
        assert "slug" in person
        assert "name" in person


async def test_get_person(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/people/abraham", headers={"X-API-Key": api_key})
    if resp.status_code == 404:
        pytest.skip("abraham not in test data")
    assert resp.status_code == 200
    person = resp.json()["data"]
    assert person["slug"] == "abraham"
    assert person["name"] == "Abraham"


async def test_person_not_found(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/people/nonexistent-slug", headers={"X-API-Key": api_key})
    assert resp.status_code == 404


async def test_list_places(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/places", headers={"X-API-Key": api_key}, params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert body["meta"]["limit"] == 5


async def test_list_events(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/events", headers={"X-API-Key": api_key}, params={"limit": 5})
    assert resp.status_code == 200
    assert "data" in resp.json()


async def test_list_groups(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/groups", headers={"X-API-Key": api_key}, params={"limit": 5})
    assert resp.status_code == 200
    assert "data" in resp.json()


async def test_search(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/search", headers={"X-API-Key": api_key}, params={"q": "Abraham"})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    if body["data"]:
        assert body["data"][0]["entity_type"] in ("person", "place", "event", "group", "dictionary", "topic")


async def test_meta(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/meta", headers={"X-API-Key": api_key})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "version" in data
    assert "counts" in data


async def test_usage(client: AsyncClient, api_key: str):
    resp = await client.get("/v1/usage", headers={"X-API-Key": api_key})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["tier"] == "free"
    assert data["daily_used"] >= 1
