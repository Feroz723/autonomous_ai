import os
from dotenv import load_dotenv

load_dotenv()

gh_token = os.getenv("GH_TOKEN")
confirm_push = os.getenv("CONFIRM_AUTO_PUSH", "false").lower() == "true"

print(f"GH_TOKEN_PRESENT={'YES' if gh_token else 'NO'}")
print(f"CONFIRM_AUTO_PUSH={confirm_push}")
