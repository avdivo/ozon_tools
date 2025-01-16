import json
import httpx
from fastapi import HTTPException


class OzonClient:
    def __init__(self, base_url: str, client_id: str, api_key: str):
        self.base_url = base_url
        self.client_id = client_id
        self.api_key = api_key
        self.client = None  # Это будет асинхронный HTTP клиент

    async def startup(self):
        # Создание клиента при старте приложения
        self.client = httpx.AsyncClient()

    async def shutdown(self):
        # Закрытие клиента при остановке приложения
        if self.client:
            await self.client.aclose()

    async def make_request(self, endpoint: str, payload: dict) -> dict:
        if not self.client:
            raise HTTPException(status_code=500, detail="HTTP client is not initialized")

        headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            payload = json.dumps(payload)
            response = await self.client.post(f"{self.base_url}{endpoint}", data=payload, headers=headers)
            response.raise_for_status()  # Проверка на успешный ответ
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {e}")
