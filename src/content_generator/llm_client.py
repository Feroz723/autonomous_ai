import os
import random
import time
from abc import ABC, abstractmethod

# Optional imports for real APIs
# import google.generativeai as genai
# import openai
# import requests  # for Ollama

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

# --- Real Implementations (Uncomment and configure to use) ---

# class GeminiClient(LLMClient):
#     def __init__(self, api_key=None):
#         self.api_key = api_key or os.getenv("GEMINI_API_KEY")
#         if not self.api_key:
#             raise ValueError("GEMINI_API_KEY not found")
#         genai.configure(api_key=self.api_key)
#         self.model = genai.GenerativeModel('gemini-pro')
#
#     def generate_text(self, prompt: str, system_prompt: str = None) -> str:
#         # Gemini doesn't have a separate system prompt in the basic generate_content
#         # You can prepend it to the prompt
#         full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
#         response = self.model.generate_content(full_prompt)
#         return response.text

# class OpenAIClient(LLMClient):
#     def __init__(self, api_key=None):
#         self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
#
#     def generate_text(self, prompt: str, system_prompt: str = None) -> str:
#         messages = []
#         if system_prompt:
#             messages.append({"role": "system", "content": system_prompt})
#         messages.append({"role": "user", "content": prompt})
#         
#         response = self.client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages
#         )
#         return response.choices[0].message.content

# class OllamaClient(LLMClient):
#     def __init__(self, base_url="http://localhost:11434", model="llama3.2"):
#         self.base_url = base_url
#         self.model = model
#
#     def generate_text(self, prompt: str, system_prompt: str = None) -> str:
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "stream": False
#         }
#         if system_prompt:
#             payload["system"] = system_prompt
#             
#         response = requests.post(f"{self.base_url}/api/generate", json=payload)
#         return response.json().get("response", "")

def get_llm_client() -> LLMClient:
    """Factory to get the configured LLM client."""
    provider = os.getenv("LLM_PROVIDER", "dummy").lower()
    
    if provider == "gemini":
        # return GeminiClient()
        print("Gemini client requested but not enabled in code. Using Dummy.")
        return DummyClient()
    elif provider == "openai":
        # return OpenAIClient()
        print("OpenAI client requested but not enabled in code. Using Dummy.")
        return DummyClient()
    elif provider == "ollama":
        # return OllamaClient()
        print("Ollama client requested but not enabled in code. Using Dummy.")
        return DummyClient()
    else:
        return DummyClient()
