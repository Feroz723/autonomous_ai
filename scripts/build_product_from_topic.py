"""
Build Product from Topic

Generates a complete digital product from a topic.
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.product_generator.outline_builder import (
    build_guide_outline,
    build_prompt_pack_outline,
    build_checklist_outline,
    build_minicourse_outline
)
from src.product_generator.content_expander import ContentExpander
from src.product_generator.pdf_exporter import markdown_to_pdf

def sanitize_filename(name: str) -> str:
    """Convert title to safe filename."""
    return name.lower().replace(' ', '-').replace(':', '').replace('/', '-')

def main():
    parser = argparse.ArgumentParser(description="Generate a digital product from a topic")
    parser.add_argument("--topic", required=True, help="Product topic")
    parser.add_argument("--type", choices=['guide', 'prompts', 'checklist', 'minicourse'], 
                       default='guide', help="Product type")
    parser.add_argument("--days", type=int, default=30, help="Days for guide (if type=guide)")
    parser.add_argument("--count", type=int, default=100, help="Prompt count (if type=prompts)")
    args = parser.parse_args()
    
    print(f"🚀 Generating {args.type} product about: {args.topic}")
    
    # Step 1: Build outline
    print("\n📝 Step 1: Building outline...")
    if args.type == 'guide':
        outline = build_guide_outline(args.topic, args.days)
    elif args.type == 'prompts':
        outline = build_prompt_pack_outline(args.topic, args.count)
    elif args.type == 'checklist':
        outline = build_checklist_outline(args.topic)
    else:  # minicourse
        outline = build_minicourse_outline(args.topic)
    
    print(f"✅ Created outline: {outline.title}")
    
    # Step 2: Expand content
    print("\n✍️ Step 2: Expanding content with AI...")
    expander = ContentExpander()
    full_content = expander.expand_outline(outline, args.topic)
    
    # Step 3: Create output directory
    product_dir = os.path.join("products", sanitize_filename(outline.title))
    os.makedirs(product_dir, exist_ok=True)
    
    # Step 4: Save markdown
    md_path = os.path.join(product_dir, "content.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print(f"✅ Saved markdown: {md_path}")
    
    # Step 5: Generate PDF
    print("\n📄 Step 3: Generating PDF...")
    pdf_path = os.path.join(product_dir, "product.pdf")
    markdown_to_pdf(full_content, pdf_path, outline.title)
    
    # Step 6: Save metadata
    metadata = {
        'title': outline.title,
        'topic': args.topic,
        'type': args.type,
        'created_at': datetime.now().isoformat(),
        'files': {
            'markdown': md_path,
            'pdf': pdf_path
        }
    }
    
    metadata_path = os.path.join(product_dir, "product_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Saved metadata: {metadata_path}")
    
    print(f"\n✨ Product generated successfully!")
    print(f"📁 Location: {product_dir}")
    print(f"\nNext steps:")
    print(f"1. Review the content in {md_path}")
    print(f"2. Check the PDF: {pdf_path}")
    print(f"3. Run: python scripts/prepare_gumroad_listing.py --product {product_dir}")

if __name__ == "__main__":
    main()
