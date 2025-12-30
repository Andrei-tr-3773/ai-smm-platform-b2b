"""
Copy Formula Library - Proven copywriting frameworks for marketing.

Includes: PAS, AIDA, 4Ps, BAB, FAB and more.
"""

from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


# Copy Formula Templates
COPY_FORMULAS = {
    "PAS": {
        "name": "Problem-Agitate-Solve",
        "emoji": "🔥",
        "structure": [
            "Problem: Identify the pain point",
            "Agitate: Make the problem feel urgent/painful",
            "Solve: Present your solution"
        ],
        "example": "Tired of spending hours on social media? Every minute wasted is revenue lost. Our AI creates professional posts in 2 minutes. Start free today!",
        "best_for": "Sales pages, ads, landing pages",
        "conversion_lift": "+15-25%",
        "description": "Classic problem-focused framework. Highly effective for pain-aware audiences."
    },

    "AIDA": {
        "name": "Attention-Interest-Desire-Action",
        "emoji": "⚡",
        "structure": [
            "Attention: Grab attention with bold hook",
            "Interest: Build interest with benefits",
            "Desire: Create desire for the outcome",
            "Action: Clear call-to-action"
        ],
        "example": "AI-Powered Content in 2 Minutes! Generate professional social posts in 15+ languages. Imagine never worrying about content again. Try it free now!",
        "best_for": "Email marketing, sales letters, landing pages",
        "conversion_lift": "+10-20%",
        "description": "Timeless framework used in advertising for 100+ years. Works for any product."
    },

    "4Ps": {
        "name": "Promise-Picture-Proof-Push",
        "emoji": "🎯",
        "structure": [
            "Promise: State clear benefit upfront",
            "Picture: Paint vision of outcome",
            "Proof: Provide evidence (testimonials, data)",
            "Push: Drive to action with urgency"
        ],
        "example": "Create 50 social posts in 10 minutes. Imagine your content calendar filled for the entire month. Join 5,000+ businesses who doubled engagement. Limited time: 50% off!",
        "best_for": "Product launches, webinars, high-ticket offers",
        "conversion_lift": "+20-30%",
        "description": "Promise-first approach. Great when you have strong social proof."
    },

    "BAB": {
        "name": "Before-After-Bridge",
        "emoji": "🌉",
        "structure": [
            "Before: Current painful state",
            "After: Desired outcome/transformation",
            "Bridge: How your product gets them there"
        ],
        "example": "Before: Spending 3 hours per post, inconsistent branding. After: Professional content in 2 minutes, perfect brand consistency. Our AI bridges the gap. Start now!",
        "best_for": "Transformation stories, coaching, services",
        "conversion_lift": "+15-25%",
        "description": "Powerful for showing transformation. Works well with before/after visuals."
    },

    "FAB": {
        "name": "Features-Advantages-Benefits",
        "emoji": "💎",
        "structure": [
            "Features: What it has/does",
            "Advantages: Why it's better than alternatives",
            "Benefits: What the customer gets (outcome)"
        ],
        "example": "AI content generation in 15+ languages. Faster than competitors, more languages than Jasper. Save 10 hours/week, 3x your engagement. Try free!",
        "best_for": "Product descriptions, comparison pages, B2B",
        "conversion_lift": "+10-15%",
        "description": "Logical, feature-focused. Best for B2B and technical audiences."
    },

    "PASTOR": {
        "name": "Problem-Amplify-Story-Transformation-Offer-Response",
        "emoji": "📖",
        "structure": [
            "Problem: Identify the core issue",
            "Amplify: Make it worse, show consequences",
            "Story: Share relatable transformation story",
            "Transformation: Show the change possible",
            "Offer: Present your solution",
            "Response: Clear CTA with urgency"
        ],
        "example": "Struggling with social media? It gets worse: competitors are gaining while you fall behind. Sarah was the same - until she found AI content tools. She went from 200 to 2,000 views per post. Our platform made it possible. Limited spots: Join now!",
        "best_for": "Long-form sales pages, email sequences, VSLs",
        "conversion_lift": "+25-35%",
        "description": "Story-driven, empathy-focused. Highly effective for complex offers."
    },

    "QUEST": {
        "name": "Qualify-Understand-Educate-Stimulate-Transition",
        "emoji": "🎓",
        "structure": [
            "Qualify: Identify target audience",
            "Understand: Show you understand their problem",
            "Educate: Teach them something valuable",
            "Stimulate: Create desire for solution",
            "Transition: Smooth CTA"
        ],
        "example": "Are you a small business owner drowning in social media tasks? We know - 12 hours/week is unsustainable. Here's the secret: AI can do 80% of the work. Imagine reclaiming that time. See how it works →",
        "best_for": "Educational content, lead magnets, authority building",
        "conversion_lift": "+10-20%",
        "description": "Education-first approach. Builds trust before asking for sale."
    }
}


def get_formula(formula_key: str) -> Dict[str, Any]:
    """
    Get formula details by key.

    Args:
        formula_key: Formula identifier (PAS, AIDA, etc.)

    Returns:
        Formula configuration dict
    """
    return COPY_FORMULAS.get(formula_key)


def list_all_formulas() -> List[Dict[str, Any]]:
    """
    Get list of all available formulas.

    Returns:
        List of formula dicts with keys and names
    """
    return [
        {
            "key": key,
            "name": formula["name"],
            "emoji": formula["emoji"],
            "best_for": formula["best_for"]
        }
        for key, formula in COPY_FORMULAS.items()
    ]


def apply_formula_to_copy(
    original_copy: str,
    formula_key: str,
    model: ChatOpenAI
) -> str:
    """
    Apply a copy formula to existing copy.

    Args:
        original_copy: Original marketing copy
        formula_key: Formula to apply (PAS, AIDA, etc.)
        model: ChatOpenAI model instance

    Returns:
        Rewritten copy using the formula
    """
    formula = COPY_FORMULAS.get(formula_key)

    if not formula:
        raise ValueError(f"Unknown formula: {formula_key}")

    # Build prompt
    structure_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(formula["structure"])])

    prompt = f"""Rewrite this marketing copy using the {formula["name"]} formula:

Original Copy:
{original_copy}

{formula["name"]} Structure:
{structure_text}

Example of {formula["name"]}:
{formula["example"]}

Instructions:
- Follow the structure exactly
- Keep the same core message and value proposition
- Maintain similar length
- Make it persuasive and compelling
- Return ONLY the rewritten copy, no explanations

Rewritten copy:"""

    # System message
    system_message = SystemMessage(
        content=f"""You are an expert copywriter specializing in the {formula["name"]} framework.
Your rewrites are conversion-focused, persuasive, and follow the formula structure precisely."""
    )

    # Generate
    messages = [system_message, HumanMessage(content=prompt)]
    response = model.invoke(messages)

    # Clean response
    rewritten = response.content.strip()

    # Remove quotes if present
    if rewritten.startswith('"') and rewritten.endswith('"'):
        rewritten = rewritten[1:-1]

    logger.info(f"Applied {formula_key} formula to copy")

    return rewritten


def get_formula_recommendations(
    copy_length: int,
    audience_type: str = "general",
    goal: str = "conversion"
) -> List[Dict[str, Any]]:
    """
    Get formula recommendations based on context.

    Args:
        copy_length: Length of copy in words
        audience_type: Type of audience (B2B, B2C, cold, warm, etc.)
        goal: Marketing goal (awareness, conversion, education, etc.)

    Returns:
        List of recommended formulas with reasons
    """
    recommendations = []

    # Length-based recommendations
    if copy_length < 50:  # Short copy
        recommendations.extend([
            {
                "formula": "AIDA",
                "reason": "Perfect for short-form content (ads, social posts)",
                "score": 95
            },
            {
                "formula": "PAS",
                "reason": "Concise problem-solution format",
                "score": 90
            }
        ])
    elif copy_length > 200:  # Long copy
        recommendations.extend([
            {
                "formula": "PASTOR",
                "reason": "Story-driven, works well for long-form sales pages",
                "score": 95
            },
            {
                "formula": "QUEST",
                "reason": "Educational approach for detailed content",
                "score": 90
            }
        ])
    else:  # Medium length
        recommendations.extend([
            {
                "formula": "4Ps",
                "reason": "Versatile framework for medium-length copy",
                "score": 90
            },
            {
                "formula": "BAB",
                "reason": "Transformation-focused, works for any length",
                "score": 85
            }
        ])

    # Audience-based recommendations
    if audience_type.lower() in ["b2b", "business", "professional"]:
        recommendations.append({
            "formula": "FAB",
            "reason": "Logical, feature-focused approach for B2B",
            "score": 90
        })
    elif audience_type.lower() in ["cold", "new", "unaware"]:
        recommendations.append({
            "formula": "PAS",
            "reason": "Problem-first works well for cold traffic",
            "score": 95
        })

    # Goal-based recommendations
    if goal.lower() in ["conversion", "sales", "revenue"]:
        recommendations.append({
            "formula": "4Ps",
            "reason": "Proof-driven, high conversion rates",
            "score": 95
        })
    elif goal.lower() in ["awareness", "education", "trust"]:
        recommendations.append({
            "formula": "QUEST",
            "reason": "Education-first builds authority",
            "score": 90
        })

    # Sort by score and deduplicate
    seen = set()
    unique_recommendations = []
    for rec in sorted(recommendations, key=lambda x: x["score"], reverse=True):
        if rec["formula"] not in seen:
            seen.add(rec["formula"])
            unique_recommendations.append(rec)

    return unique_recommendations[:3]  # Top 3 recommendations


def explain_formula(formula_key: str) -> str:
    """
    Get detailed explanation of a formula.

    Args:
        formula_key: Formula identifier

    Returns:
        Markdown-formatted explanation
    """
    formula = COPY_FORMULAS.get(formula_key)

    if not formula:
        return "Formula not found"

    structure_list = "\n".join([f"- {step}" for step in formula["structure"]])

    return f"""
## {formula["emoji"]} {formula["name"]}

**Description:** {formula["description"]}

**Structure:**
{structure_list}

**Example:**
> {formula["example"]}

**Best Used For:** {formula["best_for"]}

**Expected Conversion Lift:** {formula["conversion_lift"]}
"""
