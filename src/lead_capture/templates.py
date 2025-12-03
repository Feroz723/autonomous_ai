"""
DM Template Generator

Provides functions to generate personalized DM templates for different outreach scenarios.
"""

from typing import Dict

def generate_audit_offer(name: str, context: str, link: str = "") -> str:
    """Generate a DM offering a free automation audit."""
    template = f"""Hey {name}! 👋

I noticed you're interested in {context}. I've been helping solopreneurs automate their workflows and thought you might benefit from a quick (free) automation audit.

I can show you:
• Where you're losing time to manual tasks
• Quick wins you can implement today
• Tools that actually work (not the overhyped ones)

No strings attached. Just want to help fellow builders.

Interested? Just reply "YES" and I'll send you a quick form."""

    if link:
        template += f"\n\nOr check this out: {link}"
    
    return template

def generate_resource_offer(name: str, context: str, resource_name: str = "guide", link: str = "") -> str:
    """Generate a DM offering a free resource."""
    template = f"""Hey {name}!

Saw your comment about {context}. I actually just created a free {resource_name} on exactly this topic.

It covers:
✅ The framework I use daily
✅ Real examples (not theory)
✅ Tools & templates you can steal

Want me to send it over? It's completely free."""

    if link:
        template += f"\n\nGrab it here: {link}"
    
    return template

def generate_product_pitch(name: str, context: str, product_name: str, product_link: str) -> str:
    """Generate a soft pitch for a product."""
    template = f"""Hey {name},

I've been following your journey with {context} - really impressive stuff!

I recently launched {product_name} which helps with exactly this. It's designed for solopreneurs who want to [benefit].

No pressure at all, but thought it might be useful for you.

Check it out: {product_link}

Happy to answer any questions!"""
    
    return template

def generate_engagement_followup(name: str, tweet_context: str) -> str:
    """Generate a follow-up DM after someone engages with your content."""
    template = f"""Hey {name}!

Thanks for engaging with my post about {tweet_context}! 🙏

I'm always looking to connect with people who are interested in this space.

What are you currently working on? Would love to hear more about your journey."""
    
    return template

def get_template_suggestions(context: str, goal: str = "engagement") -> Dict[str, str]:
    """
    Get multiple template suggestions based on context and goal.
    
    Args:
        context: What the person is interested in
        goal: 'engagement', 'resource', 'audit', or 'product'
    
    Returns:
        Dictionary with template_type as key and template as value
    """
    name = "{name}"  # Placeholder
    
    suggestions = {}
    
    if goal == "engagement":
        suggestions["followup"] = generate_engagement_followup(name, context)
        suggestions["resource"] = generate_resource_offer(name, context)
    elif goal == "resource":
        suggestions["resource"] = generate_resource_offer(name, context)
        suggestions["audit"] = generate_audit_offer(name, context)
    elif goal == "audit":
        suggestions["audit"] = generate_audit_offer(name, context)
    elif goal == "product":
        suggestions["product"] = generate_product_pitch(name, context, "AI Automation Kit", "https://example.com")
    else:
        # Default: offer multiple options
        suggestions["followup"] = generate_engagement_followup(name, context)
        suggestions["resource"] = generate_resource_offer(name, context)
    
    return suggestions
