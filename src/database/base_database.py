from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseDatabase(ABC):
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @contextmanager
    @abstractmethod
    def get_connection(self):
        pass
