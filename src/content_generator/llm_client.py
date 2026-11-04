"""LLM provider clients with retries and explicit fallback warnings."""

import os
import random
import sys
import time
from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from src.utils import circuit
except ImportError:
    try:
        import circuit
    except ImportError:
        circuit = None
        print("⚠️ Circuit breaker utility unavailable; provider circuit breaking is disabled.")


class LLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        raise NotImplementedError


class DummyClient(LLMClient):
    """Template responses for local tests; enable intentionally via USE_DUMMY_LLM=true."""

    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        time.sleep(0.1)
        prompt_lower = prompt.lower()
        if "thread" in prompt_lower:
            return self._generate_dummy_thread(prompt)
        if "tweet" in prompt_lower:
            return self._generate_dummy_tweet(prompt)
        if "cta" in prompt_lower:
            return "🔥 DM me 'GROWTH' to get my free guide on this!"
        if "product" in prompt_lower or "lead magnet" in prompt_lower:
            return "Create a '30-Day AI Automation Checklist' PDF. It solves the problem of not knowing where to start. High value, easy to consume."
        return f"Dummy response to: {prompt[:50]}..."

    @staticmethod
    def _generate_dummy_tweet(prompt):
        topics = ["AI", "Automation", "Solopreneurship", "Python"]
        topic = next((item for item in topics if item.lower() in prompt.lower()), "Success")
        return random.choice([
            f"Here's why {topic} is changing the game. 🚀\n\nMost people ignore it, but the top 1% are leveraging it daily.\n\nDon't get left behind. #AI #Solopreneur",
            f"Stop overcomplicating {topic}.\n\n1. Start small\n2. Iterate fast\n3. Profit\n\nIt's that simple. 💡 #{topic} #Growth",
            f"The secret to mastering {topic}? Consistency.\n\nDo it every day for 30 days and watch your life change. 📈",
        ])

    @staticmethod
    def _generate_dummy_thread(prompt):
        return (
            "1/5 Here is a thread about the importance of this topic. 🧵\n\nIt's crucial for modern business.\n\n---\n\n"
            "2/5 First point: Efficiency.\n\nAutomation saves time. Time is money. 💰\n\n---\n\n"
            "3/5 Second point: Scalability.\n\nSystems allow you to grow without burnout. 📈\n\n---\n\n"
            "4/5 Third point: Freedom.\n\nThe goal isn't just money, it's time freedom. 🏖️\n\n---\n\n"
            "5/5 Summary:\n- Automate everything\n- Build systems\n- Enjoy life\n\nFollow me for more! 🔔"
        )


def _fallback(prompt: str, system_prompt: str, reason: str) -> str:
    """Return a dummy result only when fallback is enabled, and make degradation visible."""
    if os.getenv("LLM_FALLBACK_TO_DUMMY", "true").strip().lower() not in {"1", "true", "yes", "on"}:
        raise RuntimeError(f"LLM request failed and dummy fallback is disabled: {reason}")
    print(f"⚠️ LLM degraded mode: using dummy content ({reason})")
    return DummyClient().generate_text(prompt, system_prompt)


class OpenAIClient(LLMClient):
    """OpenAI Chat Completions client with bounded retries."""

    def __init__(self, api_key=None):
        try:
            import openai
        except ImportError as exc:
            raise ImportError("openai package not installed; install with pip install openai") from exc
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is required for LLM_PROVIDER=openai")
        self.client = openai.OpenAI(api_key=key)
        self.provider_name = "openai"

    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        if circuit and circuit.is_open(self.provider_name):
            return _fallback(prompt, system_prompt, f"{self.provider_name} circuit is open")
        messages = ([{"role": "system", "content": system_prompt}] if system_prompt else [])
        messages.append({"role": "user", "content": prompt})
        last_error = None
        for attempt in range(max(1, max_retries + 1)):
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                )
                result = response.choices[0].message.content if response.choices else None
                if not result or not result.strip():
                    raise ValueError("Empty response from OpenAI")
                if circuit:
                    circuit.clear_failure(self.provider_name)
                return result.strip()
            except Exception as exc:
                last_error = exc
                error = str(exc).lower()
                if "rate limit" in error or "quota" in error or "429" in error:
                    if circuit:
                        circuit.mark_failure(self.provider_name)
                    break
                if attempt < max_retries:
                    time.sleep(min(2 ** attempt + random.uniform(0, 1), 30))
        return _fallback(prompt, system_prompt, f"OpenAI request failed: {last_error}")


class GeminiClient(LLMClient):
    """Google Gemini client with retries and a configurable request delay."""

    def __init__(self, api_key=None):
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError("google-generativeai is not installed") from exc
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is required")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        self.provider_name = "gemini"
        self.request_delay = max(0.0, float(os.getenv("GEMINI_REQUEST_DELAY_SECONDS", "0")))

    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        if circuit and circuit.is_open(self.provider_name):
            return _fallback(prompt, system_prompt, f"{self.provider_name} circuit is open")
        if self.request_delay:
            time.sleep(self.request_delay)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        last_error = None
        for attempt in range(max(1, max_retries)):
            try:
                response = self.model.generate_content(full_prompt)
                result = getattr(response, "text", None)
                if result and result.strip():
                    if circuit:
                        circuit.clear_failure(self.provider_name)
                    return result.strip()
                raise ValueError("Empty response from Gemini")
            except Exception as exc:
                last_error = exc
                error = str(exc).lower()
                if "quota" in error or "rate limit" in error or "429" in error:
                    if circuit:
                        circuit.mark_failure(self.provider_name)
                    break
                if attempt + 1 < max_retries:
                    time.sleep(min(2 ** (attempt + 1) + random.uniform(0, 1), 30))
        return _fallback(prompt, system_prompt, f"Gemini request failed: {last_error}")


def get_llm_client() -> LLMClient:
    """Create the configured client; dummy mode is explicit or clearly reported."""
    if os.getenv("USE_DUMMY_LLM", "false").strip().lower() in {"1", "true", "yes", "on"}:
        print("🤖 USE_DUMMY_LLM is enabled; using template responses.")
        return DummyClient()

    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider not in {"auto", "gemini", "openai", "dummy"}:
        raise ValueError(f"Unsupported LLM_PROVIDER {provider!r}; choose auto, gemini, openai, or dummy")
    if provider == "dummy":
        print("🤖 LLM_PROVIDER=dummy; using template responses.")
        return DummyClient()

    candidates = []
    if provider in {"auto", "gemini"} and (provider == "gemini" or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        candidates.append(("gemini", GeminiClient))
    if provider in {"auto", "openai"} and (provider == "openai" or os.getenv("OPENAI_API_KEY")):
        candidates.append(("openai", OpenAIClient))

    errors = []
    for name, client_class in candidates:
        if circuit and circuit.is_open(name):
            errors.append(f"{name} circuit is open")
            continue
        try:
            return client_class()
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            if provider != "auto":
                break

    if provider == "auto" and not candidates:
        reason = "no provider API key configured"
    else:
        reason = "; ".join(errors) or f"could not initialize provider {provider}"
    return _fallback("", None, reason) if os.getenv("LLM_FALLBACK_TO_DUMMY", "true").strip().lower() in {"1", "true", "yes", "on"} else _raise_missing_provider(reason)


def _raise_missing_provider(reason: str):
    raise RuntimeError(
        f"No usable LLM provider: {reason}. Set USE_DUMMY_LLM=true for intentional offline mode, "
        "or configure LLM_PROVIDER and its API key."
    )
