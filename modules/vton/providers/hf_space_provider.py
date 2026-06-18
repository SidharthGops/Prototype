"""
modules/vton/providers/hf_space_provider.py

Concrete provider that calls the IDM-VTON Hugging Face Space via gradio_client.

Design decisions:
- This is the ONLY file in the entire codebase that knows about Hugging Face or
  gradio_client. All HF-specific quirks (API names, temp-file paths, cold-start
  retries) live here and nowhere else.
- Base64 ↔ temp-file conversion happens here. The Gradio client requires file
  paths, but the rest of the module speaks base64. We write temp files, call the
  Space, read the result, then clean up — the caller never sees a file path.
- Retry logic (up to MAX_RETRIES attempts) handles HF Space cold starts, which
  can take 30–60 seconds on the free tier. A simple linear backoff is enough here;
  exponential backoff is overkill for a user-facing, synchronous endpoint.
- The Client is instantiated once per HFSpaceProvider instance (not per request),
  so repeated calls reuse the connection. The service layer creates one provider
  instance at startup, so this is effectively one connection for the lifetime of
  the process.
- We catch all exceptions from gradio_client and re-raise as VTONProviderError
  so the service layer has one error type to handle, regardless of provider.
"""

from __future__ import annotations

import base64
import os
import tempfile
import time
import logging

from .base_provider import BaseVTONProvider, VTONProviderError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10


class HFSpaceProvider(BaseVTONProvider):
    """
    Sends images to the IDM-VTON Hugging Face Space and returns the result.

    Usage
    -----
    provider = HFSpaceProvider(space_id="yisol/IDM-VTON", timeout=120)
    output_b64 = provider.run(person_b64, garment_b64, prompt)
    """

    def __init__(self, space_id: str, timeout: int = 120) -> None:
        self._space_id = space_id
        self._timeout = timeout
        self._client = self._build_client()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_client(self):
        """
        Lazily import and instantiate the Gradio Client.

        Lazy import keeps module load fast and avoids a hard crash at import
        time if gradio_client isn't installed in environments that only run
        other modules.
        """
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
        """
        Decode a base64 string to a named temp file. Returns the file path.
        Caller is responsible for deleting the file after use.
        """
        image_bytes = base64.b64decode(b64_data)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(image_bytes)
        tmp.flush()
        tmp.close()
        return tmp.name

    @staticmethod
    def _file_to_b64(file_path: str) -> str:
        """Read a file from disk and return its base64 representation."""
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
        Call IDM-VTON on the HF Space and return the result as base64.

        The IDM-VTON Gradio app exposes a `/tryon` endpoint that accepts:
          - ImageEditor dict with background/layers/composite keys
          - garment image file
          - text prompt
          - a few boolean/int flags kept at their defaults

        Refer to the Space's API tab for the current signature:
        https://huggingface.co/spaces/yisol/IDM-VTON?view=api
        """
        person_tmp = garment_tmp = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Write images to temp files (Gradio client expects file paths)
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

                # The IDM-VTON Space API signature (as of the public Space):
                # fn_index / api_name: "/tryon"
                # Positional args:
                #   0: dict {"background": FileData, "layers": [], "composite": None}
                #      for the ImageEditor component
                #   1: garment FileData
                #   2: prompt (str)
                #   3: auto-mask checkbox (bool)
                #   4: auto-crop checkbox (bool)
                #   5: denoise steps (int, default 30)
                #   6: seed (int, default 42)
                result = self._client.predict(
                    {"background": person_file, "layers": [], "composite": None},
                    garment_file,
                    prompt,
                    True,    # is_checked (use auto-generated mask)
                    True,   # is_checked_crop (UI default: no auto-crop)
                    30,     # denoise steps
                    42,     # seed
                    api_name="/tryon",
                )

                # result is a tuple; first element is the output image path
                output_path = result[0] if isinstance(result, (list, tuple)) else result
                output_b64 = self._file_to_b64(output_path)
                logger.info("HFSpaceProvider: inference succeeded on attempt %d", attempt)
                return output_b64

            except VTONProviderError:
                raise  # already wrapped, don't retry init errors

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
                # Always clean up temp files
                for path in (person_tmp, garment_tmp):
                    if path and os.path.exists(path):
                        os.unlink(path)
                person_tmp = garment_tmp = None

        # Unreachable, but satisfies type checkers
        raise VTONProviderError("Unexpected exit from retry loop")

    def health_check(self) -> bool:
        """
        Ping the HF Space by checking if the client can be instantiated.
        A full inference call would be too slow/costly for a health check.
        """
        try:
            # Rebuild client to confirm the Space is reachable
            self._build_client()
            return True
        except VTONProviderError:
            return False
