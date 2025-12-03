"""
Prepare Gumroad Listing

Generates copy-paste ready Gumroad listing text.
"""

import sys
import os
import json
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.content_generator.llm_client import get_llm_client

def generate_gumroad_listing(title: str, topic: str, product_type: str) -> dict:
    """Generate Gumroad listing copy."""
    
    llm_client = get_llm_client()
    
    # Generate description
    desc_prompt = f"""Write a compelling product description for a digital product:

Title: {title}
Topic: {topic}
Type: {product_type}

Write a 2-3 paragraph description that:
- Hooks the reader immediately
- Explains the transformation/benefit
- Creates urgency
- Sounds authentic (not salesy)

Keep it under 200 words."""

    description = llm_client.generate_text(desc_prompt)
    
    # Generate benefits
    benefits = [
        f"✅ Master {topic} in record time",
        "✅ Save 10+ hours per week",
        "✅ Actionable, not theoretical",
        "✅ Lifetime access & updates",
        "✅ Money-back guarantee"
    ]
    
    # Suggest price based on type
    price_map = {
        'guide': 29,
        'prompts': 19,
        'checklist': 9,
        'minicourse': 49
    }
    
    suggested_price = price_map.get(product_type, 29)
    
    return {
        'title': title,
        'description': description,
        'benefits': benefits,
        'suggested_price': suggested_price
    }

def main():
    parser = argparse.ArgumentParser(description="Generate Gumroad listing")
    parser.add_argument("--product", required=True, help="Path to product directory")
    args = parser.parse_args()
    
    # Load metadata
    metadata_path = os.path.join(args.product, "product_metadata.json")
    
    if not os.path.exists(metadata_path):
        print(f"❌ Metadata not found: {metadata_path}")
        print("Run build_product_from_topic.py first.")
        return
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"📦 Preparing Gumroad listing for: {metadata['title']}")
    
    # Generate listing
    listing = generate_gumroad_listing(
        metadata['title'],
        metadata['topic'],
        metadata['type']
    )
    
    # Format output
    output = f"""
{'='*60}
GUMROAD LISTING - COPY & PASTE
{'='*60}

TITLE:
{listing['title']}

{'='*60}

DESCRIPTION:
{listing['description']}

{'='*60}

BENEFITS:
{chr(10).join(listing['benefits'])}

{'='*60}

SUGGESTED PRICE: ${listing['suggested_price']}

{'='*60}

TAGS (suggested):
{metadata['topic']}, solopreneur, automation, productivity, AI

{'='*60}
"""
    
    # Save to file
    output_path = os.path.join(args.product, "gumroad_listing.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✅ Gumroad listing saved: {output_path}")
    print("\n" + output)
    
    print("\n📋 Next steps:")
    print("1. Go to gumroad.com/products/new")
    print("2. Copy-paste the content above")
    print(f"3. Upload the PDF from: {metadata['files']['pdf']}")
    print("4. Set your price and publish!")

if __name__ == "__main__":
    main()
