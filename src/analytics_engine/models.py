"""
Analytics Models

Data models for tracking tweet performance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PerformanceRecord:
    """Represents performance metrics for a single tweet."""
    tweet_id: str
    tweet_text: str
    topic: str = ""
    impressions: int = 0
    likes: int = 0
    reposts: int = 0
    bookmarks: int = 0
    replies: int = 0
    created_at: str = ""
    engagement_score: float = 0.0
    
    def calculate_engagement_score(self) -> float:
        """Calculate engagement score based on interactions."""
        if self.impressions == 0:
            return 0.0
        
        # Weighted engagement: reposts > bookmarks > likes
        weighted_engagement = (
            self.likes + 
            self.reposts * 2 + 
            self.bookmarks * 1.5 +
            self.replies * 1.2
        )
        
        return weighted_engagement / self.impressions

@dataclass
class TopicPerformance:
    """Aggregated performance metrics for a topic."""
    topic: str
    total_tweets: int = 0
    avg_impressions: float = 0.0
    avg_engagement_score: float = 0.0
    total_likes: int = 0
    total_reposts: int = 0
    best_tweet_id: Optional[str] = None
    worst_tweet_id: Optional[str] = None
    
    def get_recommendation(self) -> str:
        """Get recommendation based on performance."""
        if self.avg_engagement_score > 0.05:
            return "BOOST - High performer, create more content"
        elif self.avg_engagement_score > 0.02:
            return "MAINTAIN - Solid performer, keep current level"
        else:
            return "REDUCE - Underperforming, try different angles"
