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
        raise RuntimeError(f"Unsupported LLM provider: {provider}")

    def _generate_groq(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.GROQ_API_KEY:
            if settings.OPENAI_API_KEY:
                return self._generate_openai(system_prompt, user_prompt)
            raise RuntimeError("GROQ_API_KEY is required for the configured LLM provider.")

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
            raise RuntimeError("OPENAI_API_KEY is required for the configured LLM provider.")

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
