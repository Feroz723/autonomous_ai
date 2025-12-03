from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Topic:
    id: int
    text: str
    source: str
    score: float
    keywords: List[str] = field(default_factory=list)

@dataclass
class Tweet:
    content: str
    hashtags: List[str] = field(default_factory=list)
    
    def __str__(self):
        tags = " ".join(self.hashtags)
        return f"{self.content}\n\n{tags}"

@dataclass
class Thread:
    tweets: List[Tweet]
    
    def __str__(self):
        return "\n\n---\n\n".join([str(t) for t in self.tweets])

@dataclass
class ContentItem:
    type: str  # 'tweet', 'thread', 'cta'
    topic_id: int
    content: str  # Full text representation
    raw_data: dict  # structured data (e.g. list of tweets for thread)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
