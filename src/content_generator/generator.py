from typing import List
from .models import Topic, Tweet, Thread, ContentItem
from .llm_client import get_llm_client

class ContentGenerator:
    def __init__(self):
        self.client = get_llm_client()

    def generate_tweet(self, topic: Topic) -> ContentItem:
        prompt = (
            f"You are a viral content creator for solopreneurs and AI enthusiasts.\\n\\n"
            f"TRENDING TOPIC: {topic.text}\\n"
            f"CONTEXT/KEYWORDS: {', '.join(topic.keywords)}\\n\\n"
            "TASK: Write ONE viral tweet about this SPECIFIC trending topic.\\n\\n"
            "REQUIREMENTS:\\n"
            "1. START with a STRONG hook (question, bold statement, or shocking stat)\\n"
            "2. MENTION the specific trend/news/event - don't be generic!\\n"
            "3. Add YOUR unique insight or contrarian take\\n"
            "4.Make it ACTION-ORIENTED (what should readers do?)\\n"
            "5. Include 1-2 relevant hashtags\\n"
            "6. Max 280 characters\\n"
            "7. Use emojis sparingly (1-2 max)\\n\\n"
            "STYLE: Confident, insightful, slightly provocative\\n"
            "AVOID: Generic advice, vague statements, boring facts\\n\\n"
            "BAD: 'AI is changing the world. Are you ready?'\\n"
            "GOOD: 'OpenAI just released GPT-5 with 10x reasoning power. Every solopreneur who ignores this will be obsolete by Q2. Here's what to do NOW: 🧵'\\n\\n"
            "Write the tweet:"
        )
        
        content_text = self.client.generate_text(prompt)
        
        return ContentItem(
            type="tweet",
            topic_id=topic.id,
            content=content_text,
            raw_data={"text": content_text}
        )

    def generate_thread(self, topic: Topic) -> ContentItem:
        prompt = (
            f"You are an expert content creator. Topic: {topic.text}\\n\\n"
            f"TRENDING CONTEXT: {', '.join(topic.keywords)}\\n\\n"
            "Write a 5-tweet thread about this SPECIFIC trending topic.\\n\\n"
            "STRUCTURE:\\n"
            "Tweet 1: HOOK - Start with shocking stat, question, or bold claim about THIS trend\\n"
            "Tweet 2: PROBLEM/CONTEXT - Why this trend matters NOW\\n"
            "Tweet 3: INSIGHT - Your unique perspective or analysis\\n"
            "Tweet 4: ACTIONABLE ADVICE - 3 concrete steps readers can take\\n"
            "Tweet 5: SUMMARY + CTA - Recap + invite engagement\\n\\n"
            "REQUIREMENTS:\\n"
            "- Reference the ACTUAL trending topic/event\\n"
            "- Include specific data, examples, or quotes when possible\\n"
            "- Each tweet should stand alone AND flow together\\n"
            "- Use line breaks for readability\\n"
            "- End with a question or call to action\\n\\n"
            "FORMAT: Separate tweets with '---'\\n"
            "Write the thread:"
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
            f"Topic: {topic.text}\\n\\n"
            "Write a short, punchy Call-to-Action (CTA) tweet that drives engagement.\\n\\n"
            "OPTIONS:\\n"
            "- Ask for opinions: 'What's your take on [topic]? Reply below'\\n"
            "- Offer value: 'DM me \"GUIDE\" for my free [topic] cheat sheet'\\n"
            "- Create urgency: 'This [topic] opportunity closes Friday. Don't miss it.'\\n"
            "- Build community: 'Tag a solopreneur who needs to see this'\\n\\n"
            "Make it specific to the topic and compelling.\\n"
            "Max 280 chars. Write the CTA:"
        )
        
        content_text = self.client.generate_text(prompt)
        
        return ContentItem(
            type="cta",
            topic_id=topic.id,
            content=content_text,
            raw_data={"text": content_text}
        )
