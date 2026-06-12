import time
import logging
from typing import Optional
import httpx
from django.conf import settings
from .base import BaseLLMClient

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseLLMClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> dict:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        start = time.time()
        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                result = resp.json()
                elapsed = int((time.time() - start) * 1000)
                logger.info(
                    "DeepSeek call succeeded in %dms, prompt=%d completion=%d",
                    elapsed,
                    result.get("usage", {}).get("prompt_tokens", 0),
                    result.get("usage", {}).get("completion_tokens", 0),
                )
                return result
        except httpx.HTTPStatusError as e:
            logger.error("DeepSeek HTTP error: %s %s", e.response.status_code, e.response.text)
            raise
        except httpx.TimeoutException:
            logger.error("DeepSeek request timed out")
            raise
        except Exception as e:
            logger.error("DeepSeek request failed: %s", str(e))
            raise
