"""
The contract every module's services/service.py must implement.

Whoever calls a module (the API route, or a future orchestrator that
chains modules together) should only ever depend on THIS interface,
never on a module's internal classes or functions.
"""

from abc import ABC, abstractmethod
from shared.schemas.base_schemas import JobRequest, JobResponse


class BaseModuleService(ABC):
    """Implement this in every modules/<name>/services/service.py."""

    @abstractmethod
    def process(self, request: JobRequest) -> JobResponse:
        """Run this module's pipeline and return a standard result shape."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Used by the gateway / orchestrator to confirm this module is
        ready (models loaded, dependencies reachable) before routing to it."""
        raise NotImplementedError
