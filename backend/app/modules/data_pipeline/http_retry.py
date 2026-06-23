import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 2


async def fetch_with_retry(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30,
) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            if attempt == MAX_RETRIES:
                logger.error("Failed after %d attempts: %s — %s", MAX_RETRIES, url, exc)
                raise
            wait = BACKOFF_BASE**attempt
            logger.warning("Attempt %d failed for %s, retrying in %ds — %s", attempt, url, wait, exc)
            await asyncio.sleep(wait)
    raise RuntimeError("Unreachable")
