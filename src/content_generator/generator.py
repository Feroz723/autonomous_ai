from typing import List
from .models import Topic, Tweet, Thread, ContentItem
from .llm_client import get_llm_client

class ContentGenerator:
    def __init__(self):
        self.client = get_llm_client()

    def generate_tweet(self, topic: Topic) -> ContentItem:
        prompt = (
            f"Topic: {topic.text}\n"
            f"Keywords: {', '.join(topic.keywords)}\n\n"
            "Write a viral tweet about this topic for solopreneurs.\n"
            "Rules:\n"
            "- Start with a strong hook\n"
            "- Be contrarian or insightful\n"
            "- Max 280 chars\n"
            "- Include 2 relevant hashtags"
        )
        
        content_text = self.client.generate_text(prompt)
        
        # Basic parsing (assuming LLM returns just the text)
        # In a real scenario, we might want structured JSON output
        
        return ContentItem(
            type="tweet",
            topic_id=topic.id,
            content=content_text,
            raw_data={"text": content_text}
        )

    def generate_thread(self, topic: Topic) -> ContentItem:
        prompt = (
            f"Topic: {topic.text}\n\n"
            "Write a 5-tweet thread about this topic.\n"
            "Structure:\n"
            "1. Hook\n"
            "2. Problem/Context\n"
            "3. Solution/Insight\n"
            "4. Example/Proof\n"
            "5. Summary + CTA\n\n"
            "Separate tweets with '---'"
        )
        
        content_text = self.client.generate_text(prompt)
        tweets_text = content_text.split("---")
        tweets = [Tweet(content=t.strip()) for t in tweets_text if t.strip()]
        
        return ContentItem(
            type="thread",
            topic_id=topic.id,
            content=content_text,
            raw_data={"tweets": [t.content for t in tweets]}
        )

    def generate_cta(self, topic: Topic) -> ContentItem:
        prompt = (
            f"Topic: {topic.text}\n\n"
            "Write a short, punchy Call-to-Action (CTA) related to this topic.\n"
            "Examples: 'DM me for...', 'Check the link in bio...', 'Reply with...'"
        )
        
        content_text = self.client.generate_text(prompt)
        
        return ContentItem(
            type="cta",
            topic_id=topic.id,
            content=content_text,
            raw_data={"text": content_text}
        )
