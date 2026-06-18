"""
Business logic for this module lives here.
This class is the only thing that needs to implement BaseModuleService —
everything else in the module supports this.
"""

from shared.interfaces.module_interface import BaseModuleService
from modules._template.schemas.schemas import TemplateRequest, TemplateResponse
from shared.schemas.base_schemas import JobStatus


class TemplateService(BaseModuleService):
    def process(self, request: TemplateRequest) -> TemplateResponse:
        # TODO: implement this module's pipeline.
        raise NotImplementedError

    def health_check(self) -> bool:
        # TODO: confirm models/dependencies are loaded and ready.
        return True
