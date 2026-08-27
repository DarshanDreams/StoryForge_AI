from __future__ import annotations

import httpx


class LLMGateway:
    """
    OpenRouter gateway.

    Model:
    nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
    """

    def __init__(
        self,
        settings,
    ):

        self.api_key = (
            settings.openrouter_api_key
        )

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        self.model = (
            settings.llm_model
        )

        self.temperature = settings.llm_temperature

        self.timeout = (
            settings.llm_timeout
        )

        self.last_usage = {}

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        if not self.api_key:

            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured."
            )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": self.temperature,
            "provider": {
                "allow_fallbacks": True,
                "require_parameters": False,
            },
        }

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

        with httpx.Client(
            timeout=self.timeout
        ) as client:

            response = client.post(
                self.base_url,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            detail = response.text[:500]
            try:
                error_data = response.json().get("error", {})
                if isinstance(error_data, dict):
                    detail = error_data.get("message", detail)
            except ValueError:
                pass

            if response.status_code in (429, 502, 503, 504):
                raise RuntimeError(
                    "OpenRouter provider is temporarily unavailable "
                    f"({response.status_code}). The selected free model "
                    "may be at capacity. Enable a fallback provider or "
                    f"try again shortly. Details: {detail}"
                )

            raise RuntimeError(
                "OpenRouter request failed: "
                f"{response.status_code} {detail}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "OpenRouter returned invalid JSON: "
                f"{response.text[:500]}"
            ) from exc

        self.last_usage = data.get("usage", {}) or {}

        provider_error = data.get("error")
        if provider_error:
            if isinstance(provider_error, dict):
                message = provider_error.get("message", provider_error)
                code = provider_error.get("code")
                detail = f"{code}: {message}" if code else str(message)
            else:
                detail = str(provider_error)
            raise RuntimeError(f"OpenRouter returned an error: {detail}")

        choices = data.get("choices")
        if not choices:
            preview = str(data)[:500]
            raise RuntimeError(
                "OpenRouter returned no choices. Response: "
                f"{preview}"
            )

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )
        if isinstance(content, str) and content.strip():
            return content

        preview = str(data)[:500]
        raise RuntimeError(
            "OpenRouter response did not contain message content. "
            f"Response: {preview}"
        )