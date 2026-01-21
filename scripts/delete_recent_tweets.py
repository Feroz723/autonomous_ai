import os
import sys
import time
import tweepy
from dotenv import load_dotenv

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def delete_tweets():
    print("🧹 Starting Emergency Tweet Deletion...")
    
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ Missing Twitter API credentials in .env")
        return

    try:
        # Use v2 Client for deletion
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        me = client.get_me()
        user_id = me.data.id
        username = me.data.username
        print(f"👤 Authenticated as: @{username} (ID: {user_id})")
        
        print("🔍 Fetching tweets to delete (using v2 API)...")
        
        count = 0
        # Fetching tweets using v2 (max_results 100 per request)
        # Note: Free tier has strict limits on fetching too
        pagination_token = None
        while True:
            response = client.get_users_tweets(
                id=user_id,
                max_results=100,
                pagination_token=pagination_token,
                tweet_fields=['id', 'text']
            )
            
            if not response.data:
                break
                
            for tweet in response.data:
                try:
                    print(f"🗑️ Deleting Tweet ID {tweet.id}: {tweet.text[:50].replace('\n', ' ')}...")
                    client.delete_tweet(tweet.id)
                    count += 1
                    time.sleep(1.0) # Be very gentle with rate limits
                except Exception as e:
                    print(f"⚠️ Failed to delete {tweet.id}: {e}")
                    if "429" in str(e):
                        print("🛑 Rate limit hit. Waiting 15 minutes (standard v2 window)...")
                        time.sleep(15 * 60)
            
            pagination_token = response.meta.get('next_token')
            if not pagination_token:
                break
        
        print(f"\n🎉 Successfully deleted {count} tweets.")
        
        print(f"\n🎉 Successfully deleted {count} tweets.")
        
    except Exception as e:
        print(f"\n❌ Error during deletion: {e}")

if __name__ == "__main__":
    delete_tweets()
