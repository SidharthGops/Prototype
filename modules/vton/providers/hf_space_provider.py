"""
modules/vton/providers/hf_space_provider.py

Concrete provider that calls the IDM-VTON Hugging Face Space via gradio_client,
then optionally refines the output with GeminiRefiner.

Changes from original:
- Accepts an optional GeminiRefiner at __init__ time (dependency injection,
  same pattern as VTONService accepting a provider).
- Calls refiner.refine() on the output before returning, only if a refiner
  was provided. The refiner handles its own fallback, so this file never
  needs to catch refinement errors.
- The prompt is now threaded all the way through run() so the refiner can
  use it as style context. It was previously used but not passed to refine().
"""

from __future__ import annotations

import base64
import os
import tempfile
import time
import logging
from typing import Optional

from .base_provider import BaseVTONProvider, VTONProviderError
from .gemini_refiner import GeminiRefiner

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


class HFSpaceProvider(BaseVTONProvider):
    """
    Sends images to the IDM-VTON Hugging Face Space and returns the result,
    optionally refined by Gemini.

    Usage
    -----
    # Without refinement (original behaviour)
    provider = HFSpaceProvider(space_id="yisol/IDM-VTON", timeout=120)

    # With Gemini refinement
    refiner = GeminiRefiner(api_key="...", strength="medium")
    provider = HFSpaceProvider(space_id="yisol/IDM-VTON", timeout=120, refiner=refiner)

    output_b64 = provider.run(person_b64, garment_b64, prompt)
    """

    def __init__(
        self,
        space_id: str,
        timeout: int = 120,
        refiner: Optional[GeminiRefiner] = None,
    ) -> None:
        self._space_id = space_id
        self._timeout = timeout
        self._refiner = refiner          # None = refinement disabled
        self._client = self._build_client()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_client(self):
        try:
            from gradio_client import Client, handle_file  # type: ignore
            logger.info("Connecting to HF Space: %s", self._space_id)
            self._handle_file = handle_file
            return Client(self._space_id)
        except Exception as exc:
            raise VTONProviderError(
                f"Failed to connect to HF Space '{self._space_id}': {exc}"
            ) from exc

    @staticmethod
    def _b64_to_tempfile(b64_data: str, suffix: str = ".png") -> str:
        image_bytes = base64.b64decode(b64_data)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(image_bytes)
        tmp.flush()
        tmp.close()
        return tmp.name

    @staticmethod
    def _file_to_b64(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    # ------------------------------------------------------------------
    # BaseVTONProvider interface
    # ------------------------------------------------------------------

    def run(
        self,
        person_image_b64: str,
        garment_image_b64: str,
        prompt: str,
    ) -> str:
        """
        Run IDM-VTON inference, then optionally refine with Gemini.

        Returns base64-encoded output image.
        """
        person_tmp = garment_tmp = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                person_tmp = self._b64_to_tempfile(person_image_b64, suffix=".png")
                garment_tmp = self._b64_to_tempfile(garment_image_b64, suffix=".png")

                logger.info(
                    "HFSpaceProvider: calling /tryon (attempt %d/%d)",
                    attempt,
                    MAX_RETRIES,
                )

                handle_file = getattr(self, "_handle_file", None)
                if handle_file is None:
                    from gradio_client import handle_file  # type: ignore

                person_file = handle_file(person_tmp)
                garment_file = handle_file(garment_tmp)

                result = self._client.predict(
                    {"background": person_file, "layers": [], "composite": None},
                    garment_file,
                    prompt,
                    True,   # auto-mask
                    True,   # auto-crop
                    30,     # denoise steps
                    42,     # seed
                    api_name="/tryon",
                )

                output_path = result[0] if isinstance(result, (list, tuple)) else result
                output_b64 = self._file_to_b64(output_path)
                logger.info(
                    "HFSpaceProvider: IDM-VTON inference succeeded on attempt %d",
                    attempt,
                )

                # ── Gemini refinement (optional) ──────────────────────
                if self._refiner is not None:
                    logger.info("HFSpaceProvider: sending output to GeminiRefiner")
                    output_b64 = self._refiner.refine(output_b64, prompt)
                # ──────────────────────────────────────────────────────

                return output_b64

            except VTONProviderError:
                raise

            except Exception as exc:
                logger.warning(
                    "HFSpaceProvider: attempt %d failed: %s", attempt, exc
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    raise VTONProviderError(
                        f"IDM-VTON inference failed after {MAX_RETRIES} attempts: {exc}"
                    ) from exc

            finally:
                for path in (person_tmp, garment_tmp):
                    if path and os.path.exists(path):
                        os.unlink(path)
                person_tmp = garment_tmp = None

        raise VTONProviderError("Unexpected exit from retry loop")

    def health_check(self) -> bool:
        try:
            self._build_client()
            return True
        except VTONProviderError:
            return False
