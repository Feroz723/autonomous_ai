import os
import time
import yaml
import tweepy
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'twitter_settings.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class TwitterPoster:
    def __init__(self):
        self.config = load_config()
        self.client = None
        self.api = None
        
        if self.config.get('enabled', False):
            self._authenticate()

    def _authenticate(self):
        try:
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_secret = os.getenv("TWITTER_ACCESS_SECRET")
            bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

            if not all([api_key, api_secret, access_token, access_secret]):
                logger.warning("Twitter credentials missing. Posting disabled.")
                return

            # Client for v2 API (posting tweets)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            
            # API for v1.1 (media upload if needed)
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            self.api = tweepy.API(auth)
            
            logger.info("Authenticated with Twitter API")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")

    def post_tweet(self, text: str) -> Optional[str]:
        """Post a single tweet. Returns Tweet ID if successful."""
        if not self.config.get('enabled', False):
            logger.info(f"[DRY RUN] Would post tweet: {text[:50]}...")
            return "dry_run_id"

        if self.config.get('dry_run', True):
            logger.info(f"[DRY RUN] Would post tweet: {text[:50]}...")
            return "dry_run_id"

        if not self.client:
            logger.error("Client not authenticated")
            return None

        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            logger.info(f"Posted tweet {tweet_id}")
            return tweet_id
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None

    def post_thread(self, tweets: List[str]) -> Optional[str]:
        """Post a thread of tweets. Returns ID of the first tweet."""
        if not tweets:
            return None

        first_id = self.post_tweet(tweets[0])
        if not first_id:
            return None

        reply_to_id = first_id
        
        # Post remaining tweets
        for text in tweets[1:]:
            # Wait delay
            delay = self.config['content'].get('thread_delay_seconds', 30)
            if not self.config.get('dry_run', True):
                time.sleep(delay)
            
            if self.config.get('enabled', False) and not self.config.get('dry_run', True):
                try:
                    response = self.client.create_tweet(
                        text=text,
                        in_reply_to_tweet_id=reply_to_id
                    )
                    reply_to_id = response.data['id']
                    logger.info(f"Posted thread reply {reply_to_id}")
                except Exception as e:
                    logger.error(f"Failed to post thread reply: {e}")
                    break
            else:
                logger.info(f"[DRY RUN] Would post reply: {text[:50]}...")

        return first_id
