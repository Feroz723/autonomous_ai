"""
Outline Builder

Generates structured outlines for different types of digital products.
"""

from typing import List, Dict

class ProductOutline:
    def __init__(self, title: str, product_type: str, sections: List[Dict]):
        self.title = title
        self.product_type = product_type
        self.sections = sections
    
    def to_markdown(self) -> str:
        """Convert outline to markdown format."""
        md = f"# {self.title}\n\n"
        
        for section in self.sections:
            md += f"## {section['title']}\n\n"
            if 'items' in section:
                for item in section['items']:
                    md += f"- {item}\n"
                md += "\n"
        
        return md

def build_guide_outline(topic: str, days: int = 30) -> ProductOutline:
    """Build outline for a multi-day guide."""
    title = f"{days}-Day {topic} Plan"
    
    sections = []
    weeks = days // 7
    
    for week in range(1, weeks + 1):
        week_title = f"Week {week}: " + ["Foundation", "Implementation", "Optimization", "Scaling"][min(week-1, 3)]
        items = []
        
        for day in range(1, 8):
            day_num = (week - 1) * 7 + day
            if day_num <= days:
                items.append(f"Day {day_num}: [Action item for {topic}]")
        
        sections.append({
            'title': week_title,
            'items': items
        })
    
    return ProductOutline(title, "guide", sections)

def build_prompt_pack_outline(topic: str, count: int = 100) -> ProductOutline:
    """Build outline for a prompt pack."""
    title = f"{count} {topic} Prompts"
    
    categories = [
        "Content Creation",
        "Strategy & Planning",
        "Analysis & Research",
        "Automation & Workflows",
        "Learning & Development"
    ]
    
    sections = []
    prompts_per_category = count // len(categories)
    
    for category in categories:
        items = [f"Prompt {i+1}: [Placeholder for {topic} prompt]" 
                for i in range(prompts_per_category)]
        sections.append({
            'title': category,
            'items': items
        })
    
    return ProductOutline(title, "prompts", sections)

def build_checklist_outline(topic: str) -> ProductOutline:
    """Build outline for a checklist/tool stack."""
    title = f"Complete {topic} Checklist"
    
    sections = [
        {
            'title': "Essential Tools",
            'items': ["Tool 1: [Description]", "Tool 2: [Description]", "Tool 3: [Description]"]
        },
        {
            'title': "Setup Steps",
            'items': ["Step 1: [Action]", "Step 2: [Action]", "Step 3: [Action]"]
        },
        {
            'title': "Best Practices",
            'items': ["Practice 1: [Tip]", "Practice 2: [Tip]", "Practice 3: [Tip]"]
        },
        {
            'title': "Common Pitfalls",
            'items': ["Pitfall 1: [Warning]", "Pitfall 2: [Warning]"]
        }
    ]
    
    return ProductOutline(title, "checklist", sections)

def build_minicourse_outline(topic: str) -> ProductOutline:
    """Build outline for a step-by-step mini-course."""
    title = f"Step-by-Step: {topic}"
    
    sections = [
        {
            'title': "Introduction",
            'items': ["What you'll learn", "Prerequisites", "Expected outcomes"]
        },
        {
            'title': "Module 1: Fundamentals",
            'items': ["Lesson 1.1: [Topic]", "Lesson 1.2: [Topic]", "Exercise 1"]
        },
        {
            'title': "Module 2: Implementation",
            'items': ["Lesson 2.1: [Topic]", "Lesson 2.2: [Topic]", "Exercise 2"]
        },
        {
            'title': "Module 3: Advanced Techniques",
            'items': ["Lesson 3.1: [Topic]", "Lesson 3.2: [Topic]", "Exercise 3"]
        },
        {
            'title': "Conclusion & Next Steps",
            'items': ["Summary", "Resources", "Community"]
        }
    ]
    
    return ProductOutline(title, "minicourse", sections)
