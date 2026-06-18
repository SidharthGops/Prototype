"""Module-specific settings. Keep tunables out of code and out of core/."""

from pydantic_settings import BaseSettings


class TemplateConfig(BaseSettings):
    # TODO: e.g. model_checkpoint_path: str = "..."
    pass


config = TemplateConfig()
