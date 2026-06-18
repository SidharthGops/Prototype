"""
The ONLY entry point into this module. Nothing outside this file
should ever import from services/ or models/ directly.
"""

from fastapi import APIRouter
from modules._template.schemas.schemas import TemplateRequest, TemplateResponse
from modules._template.services.service import TemplateService

router = APIRouter()
service = TemplateService()


@router.post("/generate", response_model=TemplateResponse)
def generate(request: TemplateRequest) -> TemplateResponse:
    return service.process(request)
