"""
modules/vton/providers/provider_factory.py

Returns the correct provider instance based on config.

Design decisions:
- A factory function (not a class) keeps this simple. The service calls
  get_provider() once at startup; it doesn't need to know the class name.
- Adding a new provider = add one elif branch here and create the class.
  Zero other files change.
- Raises ValueError for unknown active_provider values so misconfiguration
  fails loudly at startup, not silently mid-request.
"""

from __future__ import annotations

from ..config import vton_config
from .base_provider import BaseVTONProvider
from .hf_space_provider import HFSpaceProvider


def get_provider() -> BaseVTONProvider:
    """
    Instantiate and return the active VTON inference provider.

    The choice is driven entirely by vton_config.active_provider.
    To add RunpodProvider: create the class, add an elif here.
    """
    name = vton_config.active_provider

    if name == "hf_space":
        return HFSpaceProvider(
            space_id=vton_config.hf_space_id,
            timeout=vton_config.timeout_seconds,
        )

    # Future providers slot in here:
    # elif name == "runpod":
    #     from .runpod_provider import RunpodProvider
    #     return RunpodProvider(endpoint=vton_config.runpod_endpoint, ...)
    #
    # elif name == "replicate":
    #     from .replicate_provider import ReplicateProvider
    #     return ReplicateProvider(...)
    #
    # elif name == "local":
    #     from .local_provider import LocalProvider
    #     return LocalProvider(model_path=vton_config.local_model_path)

    raise ValueError(
        f"Unknown VTON provider '{name}'. "
        f"Set VTON_ACTIVE_PROVIDER to one of: hf_space, runpod, replicate, local."
    )