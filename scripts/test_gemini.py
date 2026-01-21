import sys
import os
from dotenv import load_dotenv

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("🔍 Checking Gemini API Access...\n")

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API key found!")
    print("Please add GEMINI_API_KEY=your_key_here to .env file\n")
    print("Get a free key from: https://ai.google.dev/")
    sys.exit(1)

print(f"✅ API key found: {api_key[:10]}...{api_key[-5:]}\n")

try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    print("📋 Listing available models...\n")
    
    available_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f"✅ {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Description: {model.description[:80]}...")
            print()
    
    if not available_models:
        print("❌ No models available for generateContent!")
        print("This might mean:")
        print("1. Your API key is invalid") 
        print("2. Your API key hasn't been activated yet")
        print("3. The Gemini API has changed")
    else:
        print(f"\n🎉 Found {len(available_models)} models that support text generation!")
        print("\nℹ️  The bot will try these models in order:")
        print("1. gemini-1.5-flash-latest")
        print("2. gemini-pro")
        print("3. gemini-1.5-flash")
        
except ImportError:
    print("❌ google-generativeai not installed!")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is correct")
    print("2. Visit https://ai.google.dev/ to verify your account")
    print("3. Make sure you copied the full API key (starts with 'AIzaSy')")
