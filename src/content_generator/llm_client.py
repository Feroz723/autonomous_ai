import os
import random
import time
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        pass

class DummyClient(LLMClient):
    """
    A dummy client that returns template-based responses.
    Useful for testing without API keys or costs.
    """
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        # Simulate processing time
        time.sleep(0.5)
        
        # Simple heuristic to detect what's being asked
        if "thread" in prompt.lower():
            return self._generate_dummy_thread(prompt)
        elif "tweet" in prompt.lower():
            return self._generate_dummy_tweet(prompt)
        elif "cta" in prompt.lower():
            return "🔥 DM me 'GROWTH' to get my free guide on this!"
        else:
            return f"Dummy response to: {prompt[:50]}..."

    def _generate_dummy_tweet(self, prompt):
        topics = ["AI", "Automation", "Solopreneurship", "Python"]
        topic = next((t for t in topics if t.lower() in prompt.lower()), "Success")
        
        templates = [
            f"Here's why {topic} is changing the game in 2025. 🚀\n\nMost people ignore it, but the top 1% are leveraging it daily.\n\nDon't get left behind. #AI #Solopreneur",
            f"Stop overcomplicating {topic}.\n\n1. Start small\n2. Iterate fast\n3. Profit\n\nIt's that simple. 💡 #{topic} #Growth",
            f"The secret to mastering {topic}? Consistency.\n\nDo it every day for 30 days and watch your life change. 📈"
        ]
        return random.choice(templates)

    def _generate_dummy_thread(self, prompt):
        return (
            "1/5 Here is a thread about the importance of this topic. 🧵\n\n"
            "It's crucial for modern business.\n\n---\n\n"
            "2/5 First point: Efficiency.\n\n"
            "Automation saves time. Time is money. 💰\n\n---\n\n"
            "3/5 Second point: Scalability.\n\n"
            "Systems allow you to grow without burnout. 📈\n\n---\n\n"
            "4/5 Third point: Freedom.\n\n"
            "The goal isn't just money, it's time freedom. 🏖️\n\n---\n\n"
            "5/5 Summary:\n"
            "- Automate everything\n"
            "- Build systems\n"
            "- Enjoy life\n\n"
            "Follow me for more! 🔔"
        )

class OpenAIClient(LLMClient):
    """OpenAI GPT client for content generation."""
    def __init__(self, api_key=None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

def get_llm_client() -> LLMClient:
    """Factory to get the configured LLM client."""
    # Auto-detect based on available API keys
    if os.getenv("OPENAI_API_KEY"):
        try:
            print("✅ Using OpenAI GPT-3.5-turbo for content generation")
            return OpenAIClient()
        except Exception as e:
            print(f"⚠️ Failed to initialize OpenAI client: {e}. Using Dummy.")
            return DummyClient()
    else:
        print("ℹ️ No API keys found. Using Dummy client for testing.")
        return DummyClient()
