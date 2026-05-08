from abc import ABC, abstractmethod
from typing import Any, Dict


class MessagePublisherPort(ABC):

    @abstractmethod
    async def publish(self, routing_key: str, message: Dict[str, Any]) -> None:
        pass
