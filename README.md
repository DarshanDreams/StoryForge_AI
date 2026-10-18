# StoryForge AI

Production-style GenAI Story Intelligence Platform.

## Architecture

Streamlit
↓
Services
↓
LLM Gateway
↓
OpenRouter
↓
LLM

Additional layers:

- PostgreSQL
- Qdrant
- RAG
- LangGraph
- Agent tools
- Evaluation
- Observability
- Docker

## Run locally

Create environment:

```bash
python -m venv .venv
```

### Local model fallback

StoryForge uses OpenRouter normally. If OpenRouter is rate-limited, the free
provider is at capacity, or a temporary provider error occurs, it can send the
same request to a local model served by LM Studio. This fallback is opt-in and
intended for local development only:

1. Install LM Studio and download **Qwen2.5 1.5B Instruct GGUF**. Choose the
   **Q4_K_M** quantization if available; it is much lighter than the former 3B
   suggestion and suits lower-memory machines better.
2. Load the model in LM Studio and start its local server (default port 1234).
3. Set `LOCAL_LLM_MODEL` in `.env` to the exact model ID shown by LM Studio.

The default endpoint is `http://localhost:1234/v1/chat/completions`. Set
`LOCAL_LLM_ENABLED=true` only when LM Studio is running on the same machine as
the app. A local desktop model cannot serve as fallback for a cloud-hosted app.

### Deploy on Streamlit Community Cloud

1. Push the project to a GitHub repository and deploy `app.py` from Streamlit
   Community Cloud.
2. In the app's **Settings → Secrets**, add your OpenRouter key and model
   settings as TOML values, for example:

   ```toml
   OPENROUTER_API_KEY = "your_rotated_openrouter_key"
   OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"
   OPENROUTER_FALLBACK_MODELS = "liquid/lfm-2.5-2.6b:free,qwen/qwen3.8-27b:free,inclusionai/ling-3.1-flash"
   LOCAL_LLM_ENABLED = "false"
   ```

   Do not commit `.env` or API keys. A local LM Studio server on
   `localhost:1234` is not reachable from a hosted Streamlit app, so keep
   `LOCAL_LLM_ENABLED` off in the cloud.

3. Redeploy/restart the app after changing secrets. The app rotates through
   configured OpenRouter models when it detects rate limits or capacity errors.

The full creative workflow reuses one story retrieval across all steps, runs
its independent continuity and critique reviews in parallel, and sets per-step
output-token limits to avoid unnecessarily long generations.

Zero-priced OpenRouter models can still have shared quotas, provider outages,
or temporary 429 responses; no free provider can guarantee uninterrupted
service. For production reliability, configure a paid model/provider as an
additional fallback. The active Streamlit retrieval path is lightweight,
lexical in-memory retrieval. Packages for optional LangGraph, Qdrant,
SentenceTransformers, and LangSmith integrations are in
`requirements-optional.txt` rather than the hosted app's default requirements.
The active app code does not import Pydantic; optional packages may bring it in
transitively if you install them.
