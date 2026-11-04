import logging
import os
import time
from typing import List, Optional

import tweepy
import yaml


logger = logging.getLogger(__name__)


def load_config():
    """Load Twitter settings, falling back to safe defaults for missing YAML."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "twitter_settings.yaml"
    )
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except (OSError, yaml.YAMLError) as exc:
        logger.warning("Could not load Twitter settings from %s: %s", config_path, exc)
        config = {}

    if not isinstance(config, dict):
        config = {}
    content = config.get("content")
    if not isinstance(content, dict):
        content = {}
    config["content"] = content
    config.setdefault("enabled", False)
    config.setdefault("dry_run", True)
    return config


class TwitterPoster:
    def __init__(self):
        self.config = load_config()
        self.client = None
        self.api = None

        if self.config.get("enabled", False):
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

            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_secret
            )
            self.api = tweepy.API(auth)
            logger.info("Authenticated with Twitter API")
        except Exception as exc:
            logger.error("Authentication failed: %s", exc)

    def post_tweet(self, text: str) -> Optional[str]:
        """Post one tweet and return its ID, or None if posting failed."""
        if not self.config.get("enabled", False) or self.config.get("dry_run", True):
            logger.info("[DRY RUN] Would post tweet: %s...", text[:50])
            return "dry_run_id"

        if not self.client:
            logger.error("Client not authenticated")
            return None

        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data.get("id") if response.data else None
            if not tweet_id:
                logger.error("Twitter API returned no tweet ID")
                return None
            logger.info("Posted tweet %s", tweet_id)
            return str(tweet_id)
        except Exception as exc:
            logger.error("Failed to post tweet: %s", exc)
            return None

    def post_thread(self, tweets: List[str]) -> Optional[str]:
        """Post a thread and return the first tweet's ID."""
        if not tweets:
            return None

        first_id = self.post_tweet(tweets[0])
        if not first_id:
            return None

        reply_to_id = first_id
        is_live = self.config.get("enabled", False) and not self.config.get(
            "dry_run", True
        )
        delay = self.config.get("content", {}).get("thread_delay_seconds", 30)

        for text in tweets[1:]:
            if is_live:
                try:
                    if delay:
                        time.sleep(max(0, delay))
                    if not self.client:
                        logger.error("Client not authenticated; stopping thread")
                        break
                    response = self.client.create_tweet(
                        text=text, in_reply_to_tweet_id=reply_to_id
                    )
                    reply_to_id = response.data.get("id") if response.data else None
                    if not reply_to_id:
                        logger.error("Twitter API returned no ID for thread reply")
                        break
                    logger.info("Posted thread reply %s", reply_to_id)
                except Exception as exc:
                    logger.error("Failed to post thread reply: %s", exc)
                    break
            else:
                logger.info("[DRY RUN] Would post reply: %s...", text[:50])

        return first_id
