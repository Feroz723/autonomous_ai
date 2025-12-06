import os
import random
import time
import sys
from abc import ABC, abstractmethod

# Add src to path if needed to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

try:
    from src.utils import circuit
except ImportError:
    # Fallback if running from a different context
    try:
        import circuit
    except ImportError:
        print("⚠️ Could not import circuit breaker utility. Circuit breaking disabled.")
        circuit = None

class LLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        pass

class DummyClient(LLMClient):
    """
    A dummy client that returns template-based responses.
    Useful for testing without API keys or costs.
    """
    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        # Simulate processing time
        time.sleep(0.1)
        
        # Simple heuristic to detect what's being asked
        if "thread" in prompt.lower():
            return self._generate_dummy_thread(prompt)
        elif "tweet" in prompt.lower():
            return self._generate_dummy_tweet(prompt)
        elif "cta" in prompt.lower():
            return "🔥 DM me 'GROWTH' to get my free guide on this!"
        elif "product" in prompt.lower() or "lead magnet" in prompt.lower():
             return "Create a '30-Day AI Automation Checklist' PDF. It solves the problem of not knowing where to start. High value, easy to consume."
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
    """OpenAI GPT client with retries and circuit breaker."""
    def __init__(self, api_key=None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.provider_name = "openai"
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def generate_text(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> str:
        # Check circuit breaker
        if circuit and circuit.is_open(self.provider_name):
            print(f"⚠️ Circuit open for {self.provider_name}. Falling back to Dummy.")
            return DummyClient().generate_text(prompt, system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Retry logic
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Success! Clear any failure counts
                if circuit:
                    circuit.clear_failure(self.provider_name)
                    
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ OpenAI Error (Attempt {attempt+1}/{max_retries+1}): {str(e)}")
                
                # Check for rate limits or quota issues
                if "rate limit" in error_msg or "quota" in error_msg or "429" in str(e):
                    if circuit:
                        circuit.mark_failure(self.provider_name)
                    print(f"🛑 Critical OpenAI error. Opening circuit breaker and falling back.")
                    return DummyClient().generate_text(prompt, system_prompt)
                
                # If last attempt failed, fallback
                if attempt == max_retries:
                    print("❌ All retries failed. Falling back to Dummy Client.")
                    return DummyClient().generate_text(prompt, system_prompt)
                
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
        
        return DummyClient().generate_text(prompt, system_prompt)

def get_llm_client() -> LLMClient:
    """Factory to get the configured LLM client."""
    
    # 1. Check for forced dummy mode
    if os.getenv("USE_DUMMY_LLM", "false").lower() == "true":
        print("🤖 USE_DUMMY_LLM is set. Using Dummy Client.")
        return DummyClient()
        
    # 2. Check provider preference
    provider = os.getenv("LLM_PROVIDER", "auto").lower()
    
    # 3. Auto-detect or specific provider
    if provider == "openai" or (provider == "auto" and os.getenv("OPENAI_API_KEY")):
        try:
            # Check if circuit is already open before even trying to instantiate
            # (Though instantiation is cheap, good practice)
            if circuit and circuit.is_open("openai"):
                print("⚠️ OpenAI circuit is OPEN. Using Dummy Client.")
                return DummyClient()
                
            print("✅ Using OpenAI GPT-3.5-turbo")
            return OpenAIClient()
        except Exception as e:
            print(f"⚠️ Failed to initialize OpenAI client: {e}. Using Dummy.")
            return DummyClient()
            
    elif provider == "ollama":
        print("Ollama client requested but not enabled in code. Using Dummy.")
        return DummyClient()
        
    else:
        print("ℹ️ No valid API keys found or provider not configured. Using Dummy client.")
        return DummyClient()
