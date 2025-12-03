from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Lead:
    """Represents a potential customer/lead from social media engagement."""
    id: Optional[int] = None
    handle: str = ""
    source: str = ""  # tweet_reply, dm, mention, etc.
    status: str = "new"  # new, contacted, qualified, converted, cold
    last_message: Optional[str] = None
    engagement_score: int = 0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'handle': self.handle,
            'source': self.source,
            'status': self.status,
            'last_message': self.last_message,
            'engagement_score': self.engagement_score,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
