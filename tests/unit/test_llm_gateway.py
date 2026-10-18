import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.llm.gateway import LLMGateway


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def post(self, *args, **kwargs):
        return next(self.responses)


def make_settings():
    return SimpleNamespace(
        openrouter_api_key="test-key",
        llm_model="test/openrouter-model",
        llm_temperature=0.2,
        llm_timeout=2,
        openrouter_fallback_models="",
        local_llm_enabled=True,
        local_llm_base_url="http://localhost:1234/v1/chat/completions",
        local_llm_model="lmstudio-community/Qwen2.5-1.5B-Instruct-GGUF",
    )


def test_rate_limit_falls_back_to_local_model():
    responses = [
        FakeResponse(429, {"error": {"message": "Rate limit exceeded"}}),
        FakeResponse(
            200,
            {
                "choices": [
                    {"message": {"content": "Local response"}}
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            },
        ),
    ]
    gateway = LLMGateway(make_settings())

    with patch("src.llm.gateway.httpx.Client", return_value=FakeClient(responses)):
        result = gateway.generate("system", "user")

    assert result == "Local response"
    assert gateway.last_provider == "lm-studio-local"
    assert gateway.last_model == "lmstudio-community/Qwen2.5-1.5B-Instruct-GGUF"
    assert gateway.last_usage["prompt_tokens"] == 10


def test_nvidia_worker_request_limit_falls_back_to_local_model():
    responses = [
        FakeResponse(
            200,
            {
                "error": {
                    "code": 502,
                    "message": (
                        "Upstream error from Nvidia: ResourceExhausted: "
                        "Worker local total request limit reached (759/16)"
                    ),
                }
            },
        ),
        FakeResponse(
            200,
            {"choices": [{"message": {"content": "Local response"}}]},
        ),
    ]
    gateway = LLMGateway(make_settings())

    with patch("src.llm.gateway.httpx.Client", return_value=FakeClient(responses)):
        result = gateway.generate("system", "user")

    assert result == "Local response"
    assert gateway.last_provider == "lm-studio-local"


def test_capacity_on_primary_tries_next_openrouter_model():
    responses = [
        FakeResponse(
            429,
            {"error": {"message": "Rate limit exceeded"}},
        ),
        FakeResponse(
            200,
            {"choices": [{"message": {"content": "Backup response"}}]},
        ),
    ]
    gateway = LLMGateway(make_settings())
    gateway.fallback_models = ["liquid/lfm-2.5-2.6b:free"]
    requested_models = []

    def post(*args, **kwargs):
        requested_models.append(kwargs["json"]["model"])
        return next(response_iterator)

    response_iterator = iter(responses)
    fake_client = FakeClient([])
    fake_client.post = post

    with patch("src.llm.gateway.httpx.Client", return_value=fake_client):
        result = gateway.generate("system", "user")

    assert result == "Backup response"
    assert requested_models == [
        "test/openrouter-model",
        "liquid/lfm-2.5-2.6b:free",
    ]
    assert gateway.last_provider == "openrouter"
    assert gateway.last_model == "liquid/lfm-2.5-2.6b:free"


def test_authentication_error_does_not_fall_back():
    responses = [FakeResponse(401, {"error": {"message": "Invalid API key"}})]
    gateway = LLMGateway(make_settings())

    with patch("src.llm.gateway.httpx.Client", return_value=FakeClient(responses)):
        with pytest.raises(RuntimeError, match="401"):
            gateway.generate("system", "user")

    assert gateway.last_provider == "openrouter"