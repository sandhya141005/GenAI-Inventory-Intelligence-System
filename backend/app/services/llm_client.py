from groq import Groq
from openai import OpenAI

from app.core.config import settings


class LLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        provider = settings.LLM_PROVIDER
        if provider == "groq":
            return self._generate_groq(system_prompt, user_prompt)
        if provider == "openai":
            return self._generate_openai(system_prompt, user_prompt)
        return self._generate_mock(system_prompt, user_prompt)

    def _generate_groq(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.GROQ_API_KEY:
            if settings.OPENAI_API_KEY:
                return self._generate_openai(system_prompt, user_prompt)
            return self._missing_key_response("GROQ_API_KEY")

        client = Groq(api_key=settings.GROQ_API_KEY)
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
            return self._missing_key_response("OPENAI_API_KEY")

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""

    def _missing_key_response(self, key_name: str) -> str:
        if not settings.ALLOW_MOCK_LLM:
            raise RuntimeError(f"{key_name} is required for the configured LLM provider.")
        return self._generate_mock("", f"Missing {key_name}; returning development mock response.")

    def _generate_mock(self, _system_prompt: str, user_prompt: str) -> str:
        return (
            "Development mock response: inventory risk is concentrated in fast-moving SKUs, "
            "with near-term action recommended on replenishment, transfers, and markdown controls. "
            f"Request context: {user_prompt[:500]}"
        )
