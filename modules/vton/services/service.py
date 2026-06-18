"""
modules/vton/services/service.py

Business logic for the VTON pipeline.

Design decisions:
- VTONService is the only public surface inside this module that the API layer
  touches. The API layer doesn't know about providers, config, or base64 details.
- The service receives and returns Pydantic schema objects (VTONRequest,
  VTONResponse). This keeps the API layer thin: it validates HTTP input → calls
  service.generate() → returns HTTP output. No business logic in routes.py.
- The provider is injected at construction time (dependency injection), not
  looked up per-request. This makes the service trivially testable: swap in a
  mock provider, call generate(), assert the output. No patching needed.
- VTONService implements the BaseModuleService interface from shared/interfaces/
  (process / health_check). When that shared module is wired up, just add the
  import and the : BaseModuleService annotation — no method signatures change.
- Default prompt fallback lives here (not in the provider, not in the route),
  because "what to do when the caller sends no prompt" is business logic.
- VTONProviderError is caught here and re-raised as VTONServiceError so that
  the API layer has a single, module-level error type to catch — it doesn't need
  to know the provider layer exists.
"""

from __future__ import annotations

import logging

from ..config import vton_config
from ..providers import BaseVTONProvider, VTONProviderError, get_provider
from ..schemas import VTONRequest, VTONResponse

logger = logging.getLogger(__name__)


class VTONServiceError(Exception):
    """Raised when the VTON pipeline cannot complete a request."""


class VTONService:
    """
    Orchestrates the try-on pipeline.

    Accepts a VTONRequest, delegates inference to the injected provider,
    and returns a VTONResponse. All provider and config details are hidden.

    Example
    -------
    service = VTONService()          # uses config-selected provider
    response = service.generate(request)
    """

    def __init__(self, provider: BaseVTONProvider | None = None) -> None:
        """
        Parameters
        ----------
        provider : Optional BaseVTONProvider
            If None, the provider is resolved from config via get_provider().
            Pass an explicit provider in tests to avoid real network calls.
        """
        self._provider: BaseVTONProvider = provider or get_provider()

    # ------------------------------------------------------------------
    # Public API (called by routes.py)
    # ------------------------------------------------------------------

    def generate(self, request: VTONRequest) -> VTONResponse:
        """
        Run the try-on pipeline and return the result image.

        Parameters
        ----------
        request : VTONRequest
            Validated request containing person image, garment image, and
            optional prompt.

        Returns
        -------
        VTONResponse
            Output image encoded as base64.

        Raises
        ------
        VTONServiceError
            If the provider fails or returns an unexpected result.
        """
        prompt = request.prompt or vton_config.default_prompt
        logger.info("VTONService.generate() — prompt: %.80s…", prompt)

        try:
            output_b64 = self._provider.run(
                person_image_b64=request.person_image,
                garment_image_b64=request.garment_image,
                prompt=prompt,
            )
        except VTONProviderError as exc:
            logger.error("Provider error: %s", exc)
            raise VTONServiceError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Unexpected error during VTON inference")
            raise VTONServiceError(f"Unexpected error: {exc}") from exc

        logger.info("VTONService.generate() — completed successfully")
        return VTONResponse(output_image=output_b64)

    # ------------------------------------------------------------------
    # BaseModuleService compat (shared/interfaces/module_interface.py)
    # ------------------------------------------------------------------

    def process(self, request: VTONRequest) -> VTONResponse:
        """
        Alias for generate(). Satisfies the BaseModuleService.process()
        contract so a future orchestrator can call any module uniformly.

        When shared/interfaces/module_interface.py exists, add:
            from shared.interfaces.module_interface import BaseModuleService
        and change the class declaration to:
            class VTONService(BaseModuleService):
        """
        return self.generate(request)

    def health_check(self) -> bool:
        """
        Delegate to provider. Returns True if the backend is reachable.
        The gateway calls this before routing traffic to this module.
        """
        return self._provider.health_check()