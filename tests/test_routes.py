import asyncio

import pytest
from sqlalchemy import select

from app.models import URLItem, URLAccessLog
from app.utils.encoding import encode_base62


@pytest.mark.asyncio
async def test_create_short_url(client):
    payload = {"url": "https://www.google.com"}
    response = await client.post("/shorten", json=payload)

    assert response.status_code == 201
    data = response.json()
    # Add '/' because of pydantic HttpURL
    assert data["originalUrl"] == "https://www.google.com/"
    assert "shortCode" in data
    assert len(data["shortCode"]) == 8


@pytest.mark.asyncio
async def test_access_url_by_short_code(client, db_session):
    """
    - Create a URLItem in DB directly.
    - Calculate its Short Code.
    - Call the endpoint.
    - Assert Redirect (307).
    - Assert Background Task: Check URLAccessLog table.
    - Assert Atomic Update: Check URL.clicked_count incremented.
    """

    original = "https://www.example.com"
    url_obj = URLItem(short_code=1000, original_url=original, clicked_count=0)
    db_session.add(url_obj)
    await db_session.commit()

    expected_code = encode_base62(1000)
    response = await client.get(f"/{expected_code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == original

    # Wait for Background Tasks (Decorator Logic)
    await asyncio.sleep(0.2)

    # expire/refresh the session to see new data committed by the background task
    db_session.expire_all()

    result_log = await db_session.execute(
        select(URLAccessLog).where(URLAccessLog.url_id == 1000)
    )
    log_entry = result_log.scalar_one_or_none()

    assert log_entry is not None, "Access Log was not created"
    assert log_entry.url_id == 1000
    assert log_entry.ip_address is not None

    # Verify Atomic Increment
    result_url = await db_session.execute(select(URLItem).where(URLItem.short_code == 1000))
    updated_url = result_url.scalar_one()

    assert updated_url.clicked_count == 1, "Click count was not incremented"


@pytest.mark.asyncio
async def test_redirect_not_found(client):
    response = await client.get("/NONEXIST", follow_redirects=False)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_url_stats(client, db_session):
    """
    - Create a URL with existing clicks.
    - Call GET /stats/{short_code}.
    - Assert correct JSON response.
    - Test handling of non-existent code.
    """

    url_id = 9999
    initial_clicks = 50
    url_obj = URLItem(
        short_code=url_id,
        original_url="https://python.org",
        clicked_count=initial_clicks
    )
    db_session.add(url_obj)
    await db_session.commit()

    short_code = encode_base62(url_id)

    response = await client.get(f"/stats/{short_code}")

    assert response.status_code == 200
    data = response.json()

    assert data["shortCode"] == short_code
    assert data["originalUrl"] == "https://python.org"
    assert data["clickedCount"] == 50
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_get_stats_not_found(client):
    response = await client.get("/stats/ZZZZZZZZ")
    assert response.status_code == 404

    response = await client.get("/stats/invalid-char-?")
    assert response.status_code == 400

