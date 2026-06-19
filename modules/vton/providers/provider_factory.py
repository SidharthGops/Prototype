"""
modules/vton/providers/provider_factory.py

Returns the correct provider instance based on config.

Changes from original:
- If gemini_refinement_enabled is True AND gemini_api_key is set in config,
  a GeminiRefiner is constructed and injected into the provider.
- If either condition is false, provider behaves exactly as before (no refiner).
- No other file needs to change to enable/disable Gemini.
"""

from __future__ import annotations

import logging

from ..config import vton_config
from .base_provider import BaseVTONProvider
from .hf_space_provider import HFSpaceProvider
from .gemini_refiner import GeminiRefiner

logger = logging.getLogger(__name__)


def _build_refiner() -> "GeminiRefiner | None":
    """
    Construct a GeminiRefiner if config says to, otherwise return None.

    Conditions that must both be true to enable refinement:
    1. VTON_GEMINI_REFINEMENT_ENABLED=true
    2. VTON_GEMINI_API_KEY is non-empty

    Logs clearly at startup so you can see in server output whether
    refinement is active.
    """
    if not vton_config.gemini_refinement_enabled:
        logger.info("GeminiRefiner: disabled (VTON_GEMINI_REFINEMENT_ENABLED=false)")
        return None

    if not vton_config.gemini_api_key:
        logger.warning(
            "GeminiRefiner: VTON_GEMINI_REFINEMENT_ENABLED=true but "
            "VTON_GEMINI_API_KEY is not set — refinement will be skipped"
        )
        return None

    logger.info(
        "GeminiRefiner: enabled (strength=%s)",
        vton_config.gemini_refinement_strength,
    )
    return GeminiRefiner(
        api_key=vton_config.gemini_api_key,
        strength=vton_config.gemini_refinement_strength,  # type: ignore[arg-type]
    )


def get_provider() -> BaseVTONProvider:
    """
    Instantiate and return the active VTON inference provider,
    with Gemini refinement injected if configured.
    """
    name = vton_config.active_provider
    refiner = _build_refiner()

    if name == "hf_space":
        return HFSpaceProvider(
            space_id=vton_config.hf_space_id,
            timeout=vton_config.timeout_seconds,
            refiner=refiner,       # None if refinement is off — provider ignores it
        )

    # Future providers:
    # elif name == "runpod":
    #     from .runpod_provider import RunpodProvider
    #     return RunpodProvider(..., refiner=refiner)

    raise ValueError(
        f"Unknown VTON provider '{name}'. "
        f"Set VTON_ACTIVE_PROVIDER to one of: hf_space, runpod, replicate, local."
    )
