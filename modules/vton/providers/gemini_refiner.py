"""
modules/vton/providers/gemini_refiner.py

Post-processing step that uses Gemini's image generation model to fix
common VTON artifacts: incomplete garment edges, deformed fabric, low
quality regions, and unnatural draping.

Design decisions:
- This is a pure utility class, not a provider. It doesn't implement
  BaseVTONProvider because it doesn't run a try-on pipeline — it only
  refines an existing output. Keeping it separate means you can reuse it
  in other modules (Catalog, Saree) without touching the provider contract.

- Graceful fallback on any failure. Gemini is an optional quality boost,
  not a critical path. If the API is down, the key is wrong, or the model
  returns no image part, the original image is returned unchanged. The
  caller never crashes because of refinement.

- Strength presets translate to different prompt strategies so callers
  don't need to craft prompts — they just set VTON_GEMINI_REFINEMENT_STRENGTH
  in their .env.

- The client is instantiated once at __init__ time (not per call), same
  pattern as HFSpaceProvider. This keeps the API connection warm between
  requests and avoids repeated auth overhead.

- We log every refinement attempt (success and failure) at INFO/WARNING
  level so you can see in server logs whether refinement is actually
  helping without adding metrics infrastructure.
"""

from __future__ import annotations

import base64
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Prompt templates per strength level.
# Each describes what to fix while preserving what matters (identity, pose).
_REFINEMENT_PROMPTS: dict[str, str] = {
    "light": (
        "This image is a virtual try-on result showing a person wearing a garment. "
        "Make minimal corrections only: remove obvious visual artifacts, "
        "clean up incomplete or jagged garment edges, and fix any pixelated regions. "
        "Do not change colors, composition, background, or the person's face. "
        "Preserve everything else exactly as-is."
    ),
    "medium": (
        "This image is a virtual try-on result showing a person wearing a garment. "
        "Fix the following issues if present: "
        "incomplete garment edges or missing fabric sections, "
        "unnatural fabric drape or deformed clothing geometry, "
        "low-quality or blurry regions on the garment, "
        "mismatched lighting between the person and the garment. "
        "Preserve the person's face, body pose, and the overall scene composition. "
        "The result should look like a professional fashion photograph."
    ),
    "heavy": (
        "This image is a virtual try-on result showing a person wearing a garment. "
        "Apply full editorial quality correction: "
        "fix any garment deformation, incomplete edges, or fabric artifacts, "
        "ensure natural fabric drape and realistic garment fit, "
        "correct any lighting inconsistencies between person and garment, "
        "sharpen and enhance overall image quality to a professional standard. "
        "The final result should look like a high-end fashion editorial photograph. "
        "Preserve the person's identity and facial features exactly."
    ),
}

RefinementStrength = Literal["light", "medium", "heavy"]


class GeminiRefiner:
    """
    Refines a VTON output image using Gemini's image generation model.

    Usage
    -----
    refiner = GeminiRefiner(api_key="...", strength="medium")
    refined_b64 = refiner.refine(output_b64, original_prompt)
    # If refinement fails for any reason, refined_b64 == output_b64
    """

    def __init__(
        self,
        api_key: str,
        strength: RefinementStrength = "medium",
    ) -> None:
        """
        Parameters
        ----------
        api_key  : Google AI Studio API key.
        strength : How aggressively to correct the image.
                   "light" | "medium" | "heavy"
        """
        self._strength = strength if strength in _REFINEMENT_PROMPTS else "medium"
        self._client = self._build_client(api_key)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _build_client(api_key: str):
        """
        Lazily import google-genai and build the client.
        Raises ImportError with a clear message if the package isn't installed.
        """
        try:
            from google import genai  # type: ignore
            return genai.Client(api_key=api_key)
        except ImportError as exc:
            raise ImportError(
                "google-genai is not installed. "
                "Run: pip install google-genai"
            ) from exc

    def _build_prompt(self, original_prompt: str) -> str:
        """
        Combine the strength-level instruction template with the original
        generation prompt so Gemini knows what style to target.
        """
        base = _REFINEMENT_PROMPTS[self._strength]
        if original_prompt:
            base += f"\n\nOriginal generation style: {original_prompt}"
        return base

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def refine(self, image_b64: str, original_prompt: str = "") -> str:
        """
        Send the image to Gemini for refinement.

        Parameters
        ----------
        image_b64       : Base64-encoded PNG/JPEG output from IDM-VTON.
        original_prompt : The prompt used for the original VTON generation.
                          Used to preserve intended style during refinement.

        Returns
        -------
        str
            Base64-encoded refined image, or the original image_b64 if
            refinement fails for any reason.
        """
        try:
            from google.genai import types  # type: ignore
        except ImportError:
            logger.warning("google-genai not available, skipping refinement")
            return image_b64

        prompt_text = self._build_prompt(original_prompt)
        logger.info(
            "GeminiRefiner: starting refinement (strength=%s)", self._strength
        )

        try:
            image_bytes = base64.b64decode(image_b64)

            response = self._client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/png",
                            ),
                            types.Part.from_text(text=prompt_text),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            # Extract the image part from the response.
            # Gemini may return text + image; we only want the image.
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    refined_b64 = base64.b64encode(
                        part.inline_data.data
                    ).decode("utf-8")
                    logger.info("GeminiRefiner: refinement successful")
                    return refined_b64

            # Gemini returned a response but no image part (e.g. safety block).
            logger.warning(
                "GeminiRefiner: no image in response — returning original. "
                "Response text: %s",
                _extract_text(response),
            )
            return image_b64

        except Exception as exc:
            # Never crash the request because of refinement.
            logger.error(
                "GeminiRefiner: refinement failed (%s) — returning original image",
                exc,
            )
            return image_b64


def _extract_text(response) -> str:
    """Pull any text parts from a Gemini response for logging."""
    try:
        parts = response.candidates[0].content.parts
        return " ".join(p.text for p in parts if hasattr(p, "text") and p.text)
    except Exception:
        return "(could not extract text)"