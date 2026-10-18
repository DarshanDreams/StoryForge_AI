from __future__ import annotations

import httpx
from threading import local


class _CapacityError(RuntimeError):
    """Raised when an OpenRouter model/provider cannot accept requests now."""


class LLMGateway:
    """
    OpenRouter gateway.

    Model is configurable through OPENROUTER_MODEL or LLM_MODEL.
    """

    def __init__(
        self,
        settings,
    ):

        self.api_key = (
            settings.openrouter_api_key
        )

        self.base_url = getattr(
            settings,
            "openrouter_base_url",
            "https://openrouter.ai/api/v1/chat/completions",
        )

        self.model = (
            settings.llm_model
        )
        fallback_models = getattr(settings, "openrouter_fallback_models", "")
        self.fallback_models = [
            model.strip()
            for model in fallback_models.split(",")
            if model.strip() and model.strip() != self.model
        ]

        self.temperature = settings.llm_temperature

        self.timeout = (
            settings.llm_timeout
        )

        self._request_state = local()
        self.last_usage = {}
        self.last_provider = "openrouter"
        self.last_model = self.model
        self.local_fallback_enabled = getattr(
            settings, "local_llm_enabled", False
        )
        self.local_base_url = getattr(
            settings,
            "local_llm_base_url",
            "http://localhost:1234/v1/chat/completions",
        )
        self.local_model = getattr(
            settings,
            "local_llm_model",
            "qwen2.5-3b-instruct",
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> str:
        self.last_usage = {}
        self.last_provider = "openrouter"
        self.last_model = self.model

        if not self.api_key:

            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured."
            )

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
            "HTTP-Referer": (
                "https://storyforge-ai.streamlit.app"
            ),
            "X-Title": (
                "StoryForge AI"
            ),
        }

        models = [self.model, *self.fallback_models]
        capacity_errors = []
        for model in models:
            try:
                return self._generate_openrouter_model(
                    model,
                    system_prompt,
                    user_prompt,
                    headers,
                    max_tokens,
                )
            except _CapacityError as exc:
                capacity_errors.append(f"{model}: {exc}")

        reason = (
            "All configured free OpenRouter models are currently at capacity. "
            + " | ".join(capacity_errors)
        )
        if self.local_fallback_enabled:
            return self._generate_local(
                system_prompt,
                user_prompt,
                reason,
                max_tokens=max_tokens,
            )
        raise RuntimeError(reason)

    def _generate_openrouter_model(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        headers: dict[str, str],
        max_tokens: int | None = None,
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "provider": {
                "allow_fallbacks": True,
                "require_parameters": False,
            },
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise _CapacityError(f"request transport failed: {exc}") from exc

        if response.status_code != 200:
            detail = response.text[:500]
            try:
                error_data = response.json().get("error", {})
                if isinstance(error_data, dict):
                    detail = error_data.get("message", detail)
            except ValueError:
                pass

            if response.status_code in (429, 502, 503, 504):
                raise _CapacityError(
                    f"HTTP {response.status_code}: {detail}"
                )
            raise RuntimeError(
                f"OpenRouter request failed for {model}: "
                f"{response.status_code} {detail}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"OpenRouter returned invalid JSON for {model}: "
                f"{response.text[:500]}"
            ) from exc

        provider_error = data.get("error")
        if provider_error:
            if isinstance(provider_error, dict):
                message = provider_error.get("message", provider_error)
                code = provider_error.get("code")
                detail = f"{code}: {message}" if code else str(message)
            else:
                detail = str(provider_error)
            if self._is_capacity_error(detail):
                raise _CapacityError(detail)
            raise RuntimeError(
                f"OpenRouter returned an error for {model}: {detail}"
            )

        choices = data.get("choices")
        if not choices:
            raise _CapacityError(
                f"OpenRouter returned no choices: {str(data)[:300]}"
            )

        content = choices[0].get("message", {}).get("content")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            finish_reason = choices[0].get("finish_reason", "unknown")
            raise _CapacityError(
                f"provider returned no message content "
                f"(finish_reason={finish_reason})"
            )

        self.last_usage = data.get("usage", {}) or {}
        self.last_provider = "openrouter"
        self.last_model = model
        return content

    def _generate_local(
        self,
        system_prompt: str,
        user_prompt: str,
        openrouter_error: str,
        max_tokens: int | None = None,
    ) -> str:
        payload = {
            "model": self.local_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.local_base_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError(
                f"{openrouter_error}. Local model '{self.local_model}' "
                f"at {self.local_base_url} was unavailable: {exc}. "
                "Start the LM Studio local server, load the configured model, "
                "and verify LOCAL_LLM_MODEL matches its model ID."
            ) from exc

        choices = data.get("choices")
        if not choices:
            raise RuntimeError(
                f"{openrouter_error}. Local model '{self.local_model}' "
                "returned no choices. Verify that the model is loaded in "
                "LM Studio and its local server is running."
            )

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                f"{openrouter_error}. Local model '{self.local_model}' "
                "returned an empty response."
            )

        self.last_usage = data.get("usage", {}) or {}
        self.last_provider = "lm-studio-local"
        self.last_model = self.local_model
        return content

    @staticmethod
    def _is_capacity_error(message: str) -> bool:
        normalized = message.lower()
        return any(
            marker in normalized
            for marker in (
                "rate limit",
                "rate_limit",
                "429",
                "resourceexhausted",
                "too many requests",
                "quota exceeded",
                "capacity",
                "request limit reached",
                "total request limit",
                "provider is at capacity",
                "model is at capacity",
                "temporarily unavailable",
                "overloaded",
            )
        )

    @property
    def last_usage(self) -> dict:
        return getattr(self._request_state, "usage", {})

    @last_usage.setter
    def last_usage(self, value: dict) -> None:
        self._request_state.usage = value

    @property
    def last_provider(self) -> str:
        return getattr(self._request_state, "provider", "openrouter")

    @last_provider.setter
    def last_provider(self, value: str) -> None:
        self._request_state.provider = value

    @property
    def last_model(self) -> str:
        return getattr(self._request_state, "model", self.model)

    @last_model.setter
    def last_model(self, value: str) -> None:
        self._request_state.model = value