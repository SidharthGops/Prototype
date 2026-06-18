"""
modules/vton/schemas/schemas.py

Public request/response contracts for the VTON module.

Design decisions:
- Fields are base64-encoded strings, not file paths or URLs. This keeps the HTTP
  contract self-contained: callers don't need shared filesystem access, and the
  module doesn't need to reach into storage to read files. The tradeoff is larger
  payloads, which is acceptable for image-sized inputs at this stage.
- VTONRequest extends no shared base right now because shared/ doesn't exist yet
  in this repo scaffold. When shared/schemas/base_schemas.py is added, VTONRequest
  and VTONResponse should extend JobRequest / JobResponse respectively. The shapes
  here are designed to be forward-compatible with that migration (no fields that
  would conflict).
- prompt is Optional because IDM-VTON works well with an empty prompt; callers
  shouldn't be forced to craft one. The service layer applies a sensible default.
- output_image is base64 so the caller can render it immediately without another
  round-trip to storage. A future version may return a signed URL instead.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class VTONRequest(BaseModel):
    """
    Input to POST /vton/generate.

    person_image  : Base64-encoded JPEG or PNG of the person to dress.
    garment_image : Base64-encoded JPEG or PNG of the garment to try on.
    prompt        : Optional text to guide the generation (e.g. 'casual outdoor look').
    """

    person_image: str = Field(
        ...,
        description="Base64-encoded person image (JPEG or PNG).",
    )
    garment_image: str = Field(
        ...,
        description="Base64-encoded garment image (JPEG or PNG).",
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Optional generation prompt. Defaults to a neutral try-on prompt.",
    )


class VTONResponse(BaseModel):
    """
    Output from POST /vton/generate.

    output_image : Base64-encoded result image of the person wearing the garment.
    """

    output_image: str = Field(
        ...,
        description="Base64-encoded try-on result image.",
    )


class VTONErrorResponse(BaseModel):
    """Returned when the pipeline fails."""

    detail: str = Field(..., description="Human-readable error message.")