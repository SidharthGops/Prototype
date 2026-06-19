"""
modules/vton/config/config.py

Module-scoped settings for the VTON pipeline.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class VTONConfig(BaseSettings):
    # Which provider to use: "hf_space" | "runpod" | "replicate" | "local"
    active_provider: str = "hf_space"

    # Hugging Face Space identifier (used by HFSpaceProvider only)
    hf_space_id: str = "yisol/IDM-VTON"

    # Seconds to wait for a response before raising TimeoutError
    timeout_seconds: int = 120

    # Applied when the caller sends no prompt
    default_prompt: str = (
        "A person wearing the garment, photorealistic, natural lighting, full body"
    )

    # ---------------------------------------------------------------
    # Gemini post-processing settings
    # ---------------------------------------------------------------

    # Set to your Google AI Studio API key, or leave empty to disable.
    # Get one at https://aistudio.google.com/app/apikey
    gemini_api_key: str = ""

    # Master switch. Even if gemini_api_key is set, refinement only runs
    # when this is True. Lets you enable/disable without touching the key.
    gemini_refinement_enabled: bool = False

    # Controls how aggressively Gemini corrects the image.
    # "light"  — fix only obvious artifacts, preserve as much as possible
    # "medium" — fix artifacts + improve fabric/drape realism (recommended)
    # "heavy"  — full editorial polish, may alter colors/background
    gemini_refinement_strength: str = "medium"

    class Config:
        env_prefix = "VTON_"
        env_file = ".env"
        extra = "ignore"


vton_config = VTONConfig()
