import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["message"] == "Hello World"
    assert "current_time" in response_json
    assert "current_uptime" in response_json
