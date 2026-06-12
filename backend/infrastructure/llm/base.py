from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: Optional[int] = None) -> dict:
        ...
