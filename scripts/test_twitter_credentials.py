import sys
import os
import tweepy
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_twitter():
    print("🔍 Testing Twitter Credentials...")
    
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    
    # Check if keys exist
    if not api_key: print("❌ Missing: TWITTER_API_KEY"); return
    if not api_secret: print("❌ Missing: TWITTER_API_SECRET"); return
    if not access_token: print("❌ Missing: TWITTER_ACCESS_TOKEN"); return
    if not access_secret: print("❌ Missing: TWITTER_ACCESS_SECRET"); return
    
    print("✅ All API Keys present in Environment")
    
    try:
        # Test v2 Client (for posting)
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        me = client.get_me()
        print(f"✅ Authenticated as: @{me.data.username} (ID: {me.data.id})")
        
        # Test v1.1 API (often needed for media)
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        user = api.verify_credentials()
        print(f"✅ v1.1 Verify verified: {user.screen_name}")
        
        print("\n🎉 SUCCESS! Your keys are valid.")
        print("NOTE: If this works locally but not on GitHub, you need to add these keys to GitHub Secrets.")
        
    except Exception as e:
        print(f"\n❌ Authentication Failed: {e}")
        print("Please double-check your API keys in .env")

if __name__ == "__main__":
    test_twitter()
