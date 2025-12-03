import os
from dotenv import load_dotenv

load_dotenv()

required_keys = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_SECRET",
    "OPENAI_API_KEY"
]

missing = []
for key in required_keys:
    if not os.getenv(key):
        missing.append(key)

if missing:
    print(f"MISSING_KEYS: {','.join(missing)}")
else:
    print("ALL_KEYS_PRESENT")
