import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_cars(async_client: AsyncClient):
    response = await async_client.get("/cars")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["cars"] == [
        {"car_id": "car_1", "problems": [], "status": "ok"},
        {"car_id": "car_2", "problems": [], "status": "ok"},
        {"car_id": "car_3", "problems": [], "status": "ok"},
        {"car_id": "car_4", "problems": [], "status": "ok"},
    ]
