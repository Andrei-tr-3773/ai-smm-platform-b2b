"""
Copy Variations Agent - Generate multiple copy variations with different angles.

Uses 5 proven copywriting angles:
1. Problem-Solution - Address pain point + offer solution
2. Curiosity - Create intrigue and curiosity gap
3. Social Proof - Leverage numbers and testimonials
4. FOMO - Create urgency and scarcity
5. Benefit-Focused - Focus on outcomes and results
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)


class CopyVariationsAgent:
    """Generate 5 copy variations with different angles."""

    ANGLES = {
        "problem_solution": {
            "name": "Problem-Solution",
            "emoji": "🔧",
            "description": "Address pain point + offer solution",
            "prompt_template": """Rewrite this marketing copy using the Problem-Solution angle:

Original Copy:
{original_copy}

Rules:
1. Start with a relatable problem that the target audience faces
2. Agitate the pain (explain why it's frustrating or costly)
3. Present the solution (product/service)
4. End with clear call-to-action

Format Example:
"Tired of [problem]? [Agitation]. [Product] helps you [benefit] in [timeframe]. [CTA]"

Keep the same tone and length as the original. Return ONLY the rewritten copy, no explanations.""",
            "example": "Tired of spending 3 hours creating social posts? Every minute wasted is revenue lost. Our AI generates professional content in 2 minutes. Start free today!"
        },

        "curiosity": {
            "name": "Curiosity",
            "emoji": "🤔",
            "description": "Create intrigue and curiosity gap",
            "prompt_template": """Rewrite this marketing copy using the Curiosity angle:

Original Copy:
{original_copy}

Rules:
1. Start with a surprising fact or intriguing question
2. Create an information gap (tease value without revealing everything)
3. Make the reader want to know more
4. End with CTA that promises to reveal the answer

Format Example:
"The secret to [outcome] that nobody talks about... [Tease benefit]. Find out how. [CTA]"

Keep the same tone and length as the original. Return ONLY the rewritten copy, no explanations.""",
            "example": "The #1 mistake fitness studios make with social media (and how to fix it in 5 minutes). Discover what 97% of competitors are doing wrong. See the solution →"
        },

        "social_proof": {
            "name": "Social Proof",
            "emoji": "⭐",
            "description": "Leverage numbers and testimonials",
            "prompt_template": """Rewrite this marketing copy using the Social Proof angle:

Original Copy:
{original_copy}

Rules:
1. Start with an impressive number (users, results, testimonials)
2. Build credibility through social validation
3. Show transformation or results
4. End with CTA to join the community

Format Example:
"Join 10,000+ [audience] who achieved [result]. [Specific outcome]. Become part of the movement. [CTA]"

Keep the same tone and length as the original. Return ONLY the rewritten copy, no explanations.""",
            "example": "Join 5,000+ small businesses who doubled their engagement in 30 days. From 200 to 2,000 views per post. See how they did it →"
        },

        "fomo": {
            "name": "FOMO (Urgency)",
            "emoji": "⏰",
            "description": "Create urgency and scarcity",
            "prompt_template": """Rewrite this marketing copy using the FOMO (Fear of Missing Out) angle:

Original Copy:
{original_copy}

Rules:
1. Add time constraint (limited time, ending soon, deadline)
2. Add scarcity element (limited spots, while supplies last, exclusive offer)
3. Emphasize what they'll miss if they don't act now
4. Urgent call-to-action

Format Example:
"Last chance: Only [number] spots left for [offer]. [Consequence of missing out]. Act now before it's gone. [CTA]"

Keep the same tone and length as the original. Return ONLY the rewritten copy, no explanations.""",
            "example": "Only 3 days left: Lock in 50% off before prices increase. After Friday, this deal is gone forever. Don't miss out - start now!"
        },

        "benefit_focused": {
            "name": "Benefit-Focused",
            "emoji": "🎯",
            "description": "Focus on outcomes and results",
            "prompt_template": """Rewrite this marketing copy using the Benefit-Focused angle:

Original Copy:
{original_copy}

Rules:
1. Start with a specific, measurable outcome
2. Add timeframe for achieving the result (fast results)
3. List 2-3 key benefits (not features)
4. Clear action-oriented CTA that emphasizes the benefit

Format Example:
"Get [specific result] in [timeframe]. No [objection]. [Benefit 1]. [Benefit 2]. [Benefit 3]. [CTA]"

Keep the same tone and length as the original. Return ONLY the rewritten copy, no explanations.""",
            "example": "Create 20 professional social posts in 10 minutes. No design skills needed. Multilingual support. Analytics included. Start creating now!"
        }
    }

    def __init__(self, model: ChatOpenAI):
        """
        Initialize Copy Variations Agent.

        Args:
            model: ChatOpenAI model instance
        """
        self.model = model

    def generate_variations(
        self,
        original_copy: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Generate 5 copy variations with different angles.

        Args:
            original_copy: Original marketing copy to rewrite
            context: Optional context (product name, audience, etc.)

        Returns:
            Dict of variations:
            {
                "problem_solution": {
                    "name": "Problem-Solution",
                    "emoji": "🔧",
                    "description": "...",
                    "copy": "...",
                    "example": "..."
                },
                ...
            }
        """
        variations = {}

        logger.info(f"Generating copy variations for: {original_copy[:50]}...")

        for angle_key, angle_config in self.ANGLES.items():
            try:
                # Generate variation for this angle
                variation_copy = self._generate_single_variation(
                    original_copy,
                    angle_config
                )

                variations[angle_key] = {
                    "name": angle_config["name"],
                    "emoji": angle_config["emoji"],
                    "description": angle_config["description"],
                    "copy": variation_copy,
                    "example": angle_config["example"]
                }

                logger.debug(f"Generated {angle_key} variation: {variation_copy[:50]}...")

            except Exception as e:
                logger.error(f"Error generating {angle_key} variation: {str(e)}")
                variations[angle_key] = {
                    "name": angle_config["name"],
                    "emoji": angle_config["emoji"],
                    "description": angle_config["description"],
                    "copy": f"Error generating variation: {str(e)}",
                    "example": angle_config["example"]
                }

        logger.info(f"Generated {len(variations)} copy variations")

        return variations

    def _generate_single_variation(
        self,
        original_copy: str,
        angle_config: Dict[str, str]
    ) -> str:
        """
        Generate a single copy variation for one angle.

        Args:
            original_copy: Original copy to rewrite
            angle_config: Angle configuration (prompt template, etc.)

        Returns:
            Rewritten copy as string
        """
        # Format prompt with original copy
        prompt = angle_config["prompt_template"].format(
            original_copy=original_copy
        )

        # System message for context
        system_message = SystemMessage(
            content="""You are an expert copywriter specializing in conversion-focused marketing copy.
Your rewrites should be persuasive, engaging, and tailored to the specified copywriting angle.
Maintain the original tone and approximate length."""
        )

        # Generate variation
        messages = [system_message, HumanMessage(content=prompt)]
        response = self.model.invoke(messages)

        # Extract copy from response
        variation = response.content.strip()

        # Clean up any quotes or markdown
        if variation.startswith('"') and variation.endswith('"'):
            variation = variation[1:-1]

        return variation

    def compare_variations(
        self,
        variations: Dict[str, Dict[str, str]],
        criteria: str = "engagement"
    ) -> Dict[str, Any]:
        """
        Compare variations and provide recommendations for A/B testing.

        Args:
            variations: Dict of generated variations
            criteria: Comparison criteria (engagement, conversion, etc.)

        Returns:
            Dict with comparison and recommendations
        """
        recommendations = {
            "best_for_awareness": "curiosity",
            "best_for_conversion": "fomo",
            "best_for_trust": "social_proof",
            "best_for_cold_traffic": "problem_solution",
            "best_for_warm_traffic": "benefit_focused",
            "suggested_tests": [
                {
                    "test_name": "Problem vs Benefit",
                    "variant_a": "problem_solution",
                    "variant_b": "benefit_focused",
                    "hypothesis": "Problem-focused copy may resonate more with users experiencing pain points",
                    "metric": "Click-through rate"
                },
                {
                    "test_name": "Urgency vs Social Proof",
                    "variant_a": "fomo",
                    "variant_b": "social_proof",
                    "hypothesis": "FOMO drives faster action, social proof builds trust",
                    "metric": "Conversion rate"
                },
                {
                    "test_name": "Curiosity Hook",
                    "variant_a": "curiosity",
                    "variant_b": "benefit_focused",
                    "hypothesis": "Curiosity increases engagement, benefits show clear value",
                    "metric": "Time on page + CTR"
                }
            ]
        }

        return recommendations


def format_copy_for_display(copy_text: str, max_length: int = 280) -> str:
    """
    Format copy for display (truncate if needed).

    Args:
        copy_text: Copy to format
        max_length: Maximum length (default 280 chars like Twitter)

    Returns:
        Formatted copy
    """
    if len(copy_text) <= max_length:
        return copy_text

    return copy_text[:max_length - 3] + "..."


def estimate_copy_performance(
    copy_text: str,
    angle: str
) -> Dict[str, Any]:
    """
    Estimate copy performance based on best practices.

    Args:
        copy_text: Copy text to analyze
        angle: Copywriting angle used

    Returns:
        Dict with performance estimates
    """
    word_count = len(copy_text.split())
    char_count = len(copy_text)

    # Basic scoring
    score = {
        "length_score": 100 if 10 <= word_count <= 30 else 70,
        "clarity_score": 90,  # Placeholder - could use sentiment analysis
        "cta_present": "!" in copy_text or "now" in copy_text.lower() or "today" in copy_text.lower(),
        "word_count": word_count,
        "char_count": char_count,
        "estimated_ctr": None,  # Placeholder - would need historical data
    }

    # Angle-specific estimates
    angle_multipliers = {
        "fomo": 1.3,  # FOMO typically performs 30% better
        "social_proof": 1.2,
        "curiosity": 1.15,
        "problem_solution": 1.1,
        "benefit_focused": 1.0
    }

    score["angle_multiplier"] = angle_multipliers.get(angle, 1.0)

    return score
