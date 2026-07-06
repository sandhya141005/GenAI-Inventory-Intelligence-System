import warnings
import httpx
from groq import Groq
from openai import OpenAI

from app.core.config import settings

# Suppress SSL verification warnings for demo/development
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Singleton httpx client for connection reuse
_http_client = None


def get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(verify=False, timeout=30.0)
    return _http_client


class LLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        provider = settings.LLM_PROVIDER
        if provider == "groq":
            return self._generate_groq(system_prompt, user_prompt)
        if provider == "openai":
            return self._generate_openai(system_prompt, user_prompt)
        raise RuntimeError(f"Unsupported LLM provider: {provider}")

    def _generate_groq(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.GROQ_API_KEY:
            if settings.OPENAI_API_KEY:
                return self._generate_openai(system_prompt, user_prompt)
            raise RuntimeError("GROQ_API_KEY is required for the configured LLM provider.")

        # NOTE: SSL verification disabled for Windows/Python 3.13 compatibility
        # For production deployment, ensure proper SSL certificates are configured
        client = Groq(api_key=settings.GROQ_API_KEY, http_client=get_http_client())
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""

    def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required for the configured LLM provider.")

        # NOTE: SSL verification disabled for Windows/Python 3.13 compatibility
        # For production deployment, ensure proper SSL certificates are configured
        client = OpenAI(api_key=settings.OPENAI_API_KEY, http_client=get_http_client())
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""
