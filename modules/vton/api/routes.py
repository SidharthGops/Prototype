"""
modules/vton/api/routes.py

FastAPI router for the VTON module. This is the ONLY public entry point.

Design decisions:
- One router, one route, zero business logic. The route validates HTTP
  input (Pydantic does this automatically), calls service.generate(),
  and returns the response. Any logic beyond that belongs in service.py.
- The VTONService instance is created once at module load (module-level
  singleton). This keeps the provider connection alive between requests.
  If the service ever needs per-request state, use FastAPI Depends() instead.
- HTTP status mapping:
    200 — success
    422 — Pydantic validation failure (handled automatically by FastAPI)
    502 — provider/backend error (VTONServiceError)
    500 — unexpected, unhandled error
- The /health route is separate from the gateway-level health check and is
  useful for readiness probes in Kubernetes / docker-compose.
- Prefix ("/vton") is intentionally NOT set on the router itself — the gateway
  mounts it with the prefix so the module doesn't need to know where it's mounted.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..schemas import VTONRequest, VTONResponse, VTONErrorResponse
from ..services import VTONService, VTONServiceError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["VTON"])

# Module-level service singleton. One provider connection for the process lifetime.
_service = VTONService()


@router.post(
    "/vton/generate",
    response_model=VTONResponse,
    responses={
        200: {"model": VTONResponse, "description": "Try-on succeeded."},
        422: {"description": "Invalid request payload."},
        502: {"model": VTONErrorResponse, "description": "Inference backend error."},
        500: {"description": "Unexpected server error."},
    },
    summary="Generate a virtual try-on image.",
    description=(
        "Accepts a person image and a garment image (both base64-encoded), "
        "runs IDM-VTON inference, and returns the try-on result as a base64 image."
    ),
)
def generate(request: VTONRequest) -> VTONResponse:
    """POST /vton/generate"""
    logger.info("POST /vton/generate received")
    try:
        return _service.generate(request)
    except VTONServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        logger.exception("Unhandled error in POST /vton/generate")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.get(
    "/vton/health",
    summary="VTON module health check.",
    responses={
        200: {"description": "Module is ready."},
        503: {"description": "Backend unreachable."},
    },
)
def health() -> dict:
    """GET /vton/health"""
    ready = _service.health_check()
    if not ready:
        raise HTTPException(status_code=503, detail="VTON backend unreachable.")
    return {"status": "ok", "module": "vton"}