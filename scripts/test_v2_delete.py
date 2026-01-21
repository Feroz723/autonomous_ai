import os
import sys
import tweepy
from dotenv import load_dotenv

load_dotenv()

def test_v2_delete():
    print("Test v2 Delete...")
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )
    
    try:
        me = client.get_me()
        print(f"Authenticated as: @{me.data.username}")
        
        # Try to fetch just ONE tweet
        response = client.get_users_tweets(id=me.data.id, max_results=5)
        if response.data:
            tweet = response.data[0]
            print(f"Found tweet: {tweet.id} - {tweet.text[:50]}")
            # print(f"Deleting...")
            # client.delete_tweet(tweet.id)
            # print("Success!")
        else:
            print("No tweets found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_v2_delete()
