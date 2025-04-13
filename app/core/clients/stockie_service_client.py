import logging
from typing import Any, Optional

import httpx

from app.core.settings.config import config

logger = logging.getLogger(__name__)


class StockieServiceClient:
    def __init__(self):
        self.base_url = config.BACKEND_URL
        self.api_key = config.BACKEND_API_KEY
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Optional[dict[str, Any]] = None) -> Any:
        return await self._request("POST", endpoint, json=data)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json,
                )
                response.raise_for_status()
                json_data = response.json()

                if json_data.get("status") == "success":
                    return json_data.get("data")

                logger.error(f"Backend error @ {url}: {json_data.get('message')}")
                raise Exception(f"Backend error: {json_data.get('message')}")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"[{method}] {url} -> HTTP {e.response.status_code}: {e.response.text}"
            )
            raise Exception(f"HTTP error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Network error @ {url}: {str(e)}")
            raise Exception("Network error")
        except Exception as e:
            logger.error(f"Unhandled error in BEClient @ {url}: {str(e)}")
            raise
