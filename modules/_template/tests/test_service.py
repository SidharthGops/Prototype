"""
Contract test: confirms this module's API accepts and returns the shapes
defined in schemas.py, WITHOUT needing any other module's code running.
This is what lets everyone merge to develop independently and daily.
"""

from modules._template.schemas.schemas import TemplateRequest, TemplateResponse
from modules._template.services.service import TemplateService


def test_health_check():
    service = TemplateService()
    assert service.health_check() is True


def test_process_returns_response_schema():
    service = TemplateService()
    request = TemplateRequest()
    # TODO: once implemented, assert isinstance(service.process(request), TemplateResponse)
