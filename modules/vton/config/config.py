"""
modules/vton/config/config.py

Module-scoped settings for the VTON pipeline.

Design decisions:
- Uses pydantic-settings so every value can be overridden by an environment
  variable without changing code. The prefix VTON_ namespaces these cleanly
  away from core/ env vars.
- hf_space_id is the only value that ties this module to Hugging Face. If the
  team switches to RunPod tomorrow, they add a new provider, point active_provider
  to it, and this file gets one new optional field (runpod_endpoint). Nothing else
  changes.
- default_prompt lives here — not hardcoded in the service — so it's tuneable
  without a code deploy.
- timeout_seconds is provider-level; the HF Space can be slow on cold starts.
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

    class Config:
        env_prefix = "VTON_"
        env_file = ".env"
        extra = "ignore"


# Module-level singleton — import this everywhere inside the vton module.
# Do not instantiate VTONConfig() in multiple places; that makes env-var
# overrides unpredictable.
vton_config = VTONConfig()