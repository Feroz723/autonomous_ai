import sys
import os
from dotenv import load_dotenv

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def check_key(name, expected_min_len=20):
    value = os.getenv(name)
    if not value:
        print(f"❌ {name}: MISSING")
        return False
    
    # Check for common issues
    issues = []
    if value.strip() != value:
        issues.append("has leading/trailing spaces")
    if '"' in value or "'" in value:
        issues.append("has quotes (should be removed)")
    if len(value) < expected_min_len:
        issues.append(f"too short (only {len(value)} chars)")
    if ' ' in value:
        issues.append("contains spaces")
    
    if issues:
        print(f"⚠️  {name}: {len(value)} chars - ISSUES: {', '.join(issues)}")
        return False
    else:
        print(f"✅ {name}: {len(value)} chars - Format looks OK")
        return True

print("🔍 Checking .env file format...\n")

results = []
results.append(check_key("TWITTER_API_KEY", 25))
results.append(check_key("TWITTER_API_SECRET", 45))
results.append(check_key("TWITTER_ACCESS_TOKEN", 45))
results.append(check_key("TWITTER_ACCESS_SECRET", 40))
results.append(check_key("TWITTER_BEARER_TOKEN", 100))

print("\n" + "="*50)
if all(results):
    print("✅ All keys present and format looks good!")
    print("\nIf you're still getting 401 errors, the issue is:")
    print("1. Wrong keys copied from Twitter Developer Portal")
    print("2. App permissions not set to 'Read and Write'")
    print("3. Access Token generated BEFORE changing permissions")
else:
    print("❌ Please fix the issues above and try again")
