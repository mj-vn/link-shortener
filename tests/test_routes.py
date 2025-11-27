import pytest


@pytest.mark.asyncio
async def test_create_short_url(client):
    payload = {"url": "https://www.google.com"}
    response = await client.post("/shorten", json=payload)

    assert response.status_code == 201
    data = response.json()
    # Add '/' because of pydantic HttpURL
    assert data["original_url"] == "https://www.google.com/"
    assert "short_code" in data
    assert len(data["short_code"]) == 8


@pytest.mark.asyncio
async def test_redirect_not_found(client):
    response = await client.get("/NONEXIST", follow_redirects=False)
    assert response.status_code == 404

