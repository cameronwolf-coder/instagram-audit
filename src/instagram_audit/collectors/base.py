"""Base collector interface."""
from abc import ABC, abstractmethod
from instagram_audit.core import Snapshot


class Collector(ABC):
    """Abstract base class for data collectors."""

    @abstractmethod
    def collect(self) -> Snapshot:
        """Collect and return a snapshot."""
        pass
