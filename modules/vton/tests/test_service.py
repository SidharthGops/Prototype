"""
modules/vton/tests/test_service.py

Test suite for the VTON module.

Design decisions:
- All tests use a mock provider. No real network calls, no HF Space required.
  This satisfies the architecture requirement: contract tests must pass without
  another module's code (or a remote service) running locally.
- MockProvider is a plain class (no MagicMock) so its behavior is explicit and
  readable. If a future provider adds a new method, Python will tell you at
  import time that MockProvider doesn't implement it.
- The contract tests (test_generate_contract, test_error_contract) verify the
  HTTP shape, not the ML output — that's the right level for a contract test.
  Correctness of the garment overlay is a visual QA concern, not a unit test.
- FastAPI's TestClient is used for HTTP contract tests so the full route →
  service → provider chain is exercised in a single test, not just the service
  in isolation.
"""

from __future__ import annotations

import base64
import os
import tempfile
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.vton.providers.base_provider import BaseVTONProvider, VTONProviderError
from modules.vton.providers.hf_space_provider import HFSpaceProvider
from modules.vton.services.service import VTONService, VTONServiceError
from modules.vton.schemas.schemas import VTONRequest, VTONResponse
from modules.vton.api.routes import router


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_b64_image() -> str:
    """Return a minimal valid 1×1 PNG as base64 (just enough to be non-empty)."""
    # Smallest valid PNG: 1x1 transparent pixel
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return base64.b64encode(png_bytes).decode("utf-8")


FAKE_B64 = _make_b64_image()
FAKE_OUTPUT_B64 = base64.b64encode(b"fake_output_image_bytes").decode("utf-8")


class MockSuccessProvider(BaseVTONProvider):
    """Always returns a fixed base64 string."""

    def run(self, person_image_b64, garment_image_b64, prompt) -> str:
        return FAKE_OUTPUT_B64

    def health_check(self) -> bool:
        return True


class MockFailProvider(BaseVTONProvider):
    """Always raises VTONProviderError."""

    def run(self, person_image_b64, garment_image_b64, prompt) -> str:
        raise VTONProviderError("Simulated provider failure")

    def health_check(self) -> bool:
        return False


@pytest.fixture
def success_service():
    return VTONService(provider=MockSuccessProvider())


@pytest.fixture
def fail_service():
    return VTONService(provider=MockFailProvider())


@pytest.fixture
def test_client_success():
    """TestClient with success provider wired into the router's service."""
    from modules.vton.api import routes as route_module
    original = route_module._service
    route_module._service = VTONService(provider=MockSuccessProvider())
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    yield client
    route_module._service = original  # restore


@pytest.fixture
def test_client_fail():
    from modules.vton.api import routes as route_module
    original = route_module._service
    route_module._service = VTONService(provider=MockFailProvider())
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    yield client
    route_module._service = original


# ---------------------------------------------------------------------------
# Unit tests — service layer
# ---------------------------------------------------------------------------

class TestVTONServiceSuccess:
    def test_generate_returns_vton_response(self, success_service):
        request = VTONRequest(
            person_image=FAKE_B64,
            garment_image=FAKE_B64,
            prompt="casual look",
        )
        response = success_service.generate(request)
        assert isinstance(response, VTONResponse)

    def test_output_image_is_nonempty(self, success_service):
        request = VTONRequest(
            person_image=FAKE_B64,
            garment_image=FAKE_B64,
        )
        response = success_service.generate(request)
        assert len(response.output_image) > 0

    def test_default_prompt_applied_when_none(self, success_service):
        """Service should not crash when prompt is None."""
        request = VTONRequest(
            person_image=FAKE_B64,
            garment_image=FAKE_B64,
            prompt=None,
        )
        response = success_service.generate(request)
        assert response.output_image == FAKE_OUTPUT_B64

    def test_health_check_true(self, success_service):
        assert success_service.health_check() is True

    def test_process_alias_works(self, success_service):
        """process() must behave identically to generate() (BaseModuleService compat)."""
        request = VTONRequest(
            person_image=FAKE_B64,
            garment_image=FAKE_B64,
        )
        assert success_service.process(request) == success_service.generate(request)


class TestVTONServiceFailure:
    def test_provider_error_raises_service_error(self, fail_service):
        request = VTONRequest(
            person_image=FAKE_B64,
            garment_image=FAKE_B64,
        )
        with pytest.raises(VTONServiceError):
            fail_service.generate(request)

    def test_health_check_false_on_fail_provider(self, fail_service):
        assert fail_service.health_check() is False


# ---------------------------------------------------------------------------
# Contract tests — HTTP layer
# ---------------------------------------------------------------------------

class TestVTONAPIContract:
    """
    These tests verify that the module's HTTP contract is stable.
    They exercise the full route → service → provider chain using a real
    FastAPI TestClient so there are no mocked HTTP concerns.
    """

    def test_generate_returns_200_with_output_image(self, test_client_success):
        """POST /vton/generate must return 200 with an output_image field."""
        resp = test_client_success.post(
            "/vton/generate",
            json={
                "person_image": FAKE_B64,
                "garment_image": FAKE_B64,
                "prompt": "summer outfit",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "output_image" in body
        assert isinstance(body["output_image"], str)
        assert len(body["output_image"]) > 0

    def test_generate_without_prompt_returns_200(self, test_client_success):
        """prompt is optional — omitting it must still return 200."""
        resp = test_client_success.post(
            "/vton/generate",
            json={
                "person_image": FAKE_B64,
                "garment_image": FAKE_B64,
            },
        )
        assert resp.status_code == 200

    def test_generate_missing_required_field_returns_422(self, test_client_success):
        """Missing garment_image must return 422 (Pydantic validation)."""
        resp = test_client_success.post(
            "/vton/generate",
            json={"person_image": FAKE_B64},
        )
        assert resp.status_code == 422

    def test_generate_provider_failure_returns_502(self, test_client_fail):
        """Provider failure must surface as 502, not 500."""
        resp = test_client_fail.post(
            "/vton/generate",
            json={
                "person_image": FAKE_B64,
                "garment_image": FAKE_B64,
            },
        )
        assert resp.status_code == 502
        assert "detail" in resp.json()

    def test_health_returns_200_when_ready(self, test_client_success):
        resp = test_client_success.get("/vton/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_returns_503_when_backend_down(self, test_client_fail):
        resp = test_client_fail.get("/vton/health")
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Provider unit tests (no network)
# ---------------------------------------------------------------------------

class TestBaseProviderInterface:
    def test_mock_success_provider_satisfies_interface(self):
        provider = MockSuccessProvider()
        result = provider.run(FAKE_B64, FAKE_B64, "test prompt")
        assert isinstance(result, str)
        assert provider.health_check() is True

    def test_mock_fail_provider_raises_provider_error(self):
        provider = MockFailProvider()
        with pytest.raises(VTONProviderError):
            provider.run(FAKE_B64, FAKE_B64, "test prompt")


class TestHFSpaceProviderPayload:
    def test_run_sends_image_editor_payload_matching_ui(self):
        class FakeClient:
            def __init__(self):
                self.calls = []
                self.output_path = None

            def predict(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp.write(base64.b64decode(FAKE_OUTPUT_B64))
                tmp.close()
                self.output_path = tmp.name
                return tmp.name, "masked-preview.png"

        fake_client = FakeClient()
        provider = HFSpaceProvider.__new__(HFSpaceProvider)
        provider._client = fake_client
        provider._handle_file = lambda path: {
            "path": path,
            "meta": {"_type": "gradio.FileData"},
        }

        try:
            assert provider.run(FAKE_B64, FAKE_B64, "Short sleeve shirt") == FAKE_OUTPUT_B64
            args, kwargs = fake_client.calls[0]
        finally:
            if fake_client.output_path and os.path.exists(fake_client.output_path):
                os.unlink(fake_client.output_path)

        human_editor = args[0]
        garment_file = args[1]

        assert human_editor["background"]["meta"]["_type"] == "gradio.FileData"
        assert human_editor["layers"] == []
        assert human_editor["composite"] is None
        assert garment_file["meta"]["_type"] == "gradio.FileData"
        assert args[2:] == ("Short sleeve shirt", True, False, 30, 42)
        assert kwargs == {"api_name": "/tryon"}
