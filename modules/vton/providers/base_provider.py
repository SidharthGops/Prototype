"""
modules/vton/providers/base_provider.py

Abstract base class all VTON inference providers must implement.

Design decisions:
- The interface is intentionally minimal: one method (run) and one health check.
  Providers are not allowed to grow extra methods that the service layer calls
  directly — that would re-couple the service to a specific provider.
- Inputs and outputs are Python primitives (str for base64, str for prompt).
  No Pydantic models cross the provider boundary. This means providers never
  need to import from schemas/, and schema changes never ripple into provider code.
- run() is synchronous. If a provider needs async (e.g. polling a queue), it
  handles that internally and returns only when the result is ready. The service
  layer doesn't care how long it takes — it just awaits a base64 string back.
- VTONProviderError is defined here (not in schemas/) because it's an internal
  implementation detail: the API layer catches it and maps it to an HTTP 502.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class VTONProviderError(Exception):
    """Raised when a provider fails to produce a result."""


class BaseVTONProvider(ABC):
    """
    Contract every inference backend must satisfy.

    The service layer only ever calls these two methods. Swap the provider,
    and the service + API layers need zero changes.
    """

    @abstractmethod
    def run(
        self,
        person_image_b64: str,
        garment_image_b64: str,
        prompt: str,
    ) -> str:
        """
        Execute the try-on pipeline.

        Parameters
        ----------
        person_image_b64  : Base64-encoded person image.
        garment_image_b64 : Base64-encoded garment image.
        prompt            : Text prompt guiding generation.

        Returns
        -------
        str
            Base64-encoded output image.

        Raises
        ------
        VTONProviderError
            If inference fails for any reason (network, model error, timeout).
        """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Return True if the provider is reachable and ready to serve requests.
        Used by the service layer's health_check() which the gateway polls.
        """