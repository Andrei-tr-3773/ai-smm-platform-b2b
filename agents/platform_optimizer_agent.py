"""Platform Optimizer Agent - LangGraph workflow for platform-specific content optimization.

This agent analyzes platform rules and optimizes content for maximum engagement
on Instagram, Facebook, Telegram, and LinkedIn.

Workflow (4 nodes):
1. analyze_platform - Load platform rules
2. optimize_content - Apply AI-powered optimization
3. add_timing - Add best posting time recommendations
4. format_output - Format final posting guide
"""

import json
import logging
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END

from platforms.platform_knowledge import get_platform_rules
from utils.openai_utils import get_openai_client

logger = logging.getLogger(__name__)


# ============================================================================
# State Definition
# ============================================================================

class PlatformOptimizerState(TypedDict):
    """State for Platform Optimizer workflow."""

    # Input
    platform: str  # instagram, facebook, telegram, linkedin
    original_content: str
    content_type: str  # feed_post, reel, story, carousel

    # Processing
    platform_rules: Dict
    optimized_content: str
    timing_recommendations: List[str]
    format_adjustments: List[str]

    # Output
    final_content: str
    posting_guide: str
    error: str


# ============================================================================
# Workflow Nodes
# ============================================================================

def analyze_platform(state: PlatformOptimizerState) -> PlatformOptimizerState:
    """
    Node 1: Load platform rules and analyze requirements.

    Args:
        state: Current workflow state

    Returns:
        Updated state with platform_rules populated
    """
    platform = state['platform']
    content_type = state['content_type']

    logger.info(f"Analyzing platform: {platform}, content_type: {content_type}")

    # Get platform rules
    rules = get_platform_rules(platform)

    if not rules:
        logger.error(f"Unknown platform: {platform}")
        state['error'] = f"Unknown platform: {platform}"
        state['platform_rules'] = {}
        return state

    # Extract relevant rules for this content type
    state['platform_rules'] = {
        "platform": rules.platform,
        "optimal_length": rules.optimal_length.get(content_type, 150),
        "recommended_hashtags": rules.recommended_hashtags,
        "max_hashtags": rules.max_hashtags,
        "best_times": [t.strftime("%I:%M %p") for t in rules.best_posting_times],
        "worst_days": rules.worst_posting_days,
        "link_penalty": rules.link_penalty,
        "emoji_usage": rules.emoji_usage,
        "hook_importance": rules.hook_importance,
        "video_boost": rules.video_boost,
        "carousel_boost": rules.carousel_boost,
    }

    logger.info(f"Platform rules loaded: {rules.recommended_hashtags} hashtags, "
                f"{len(rules.best_posting_times)} optimal times")

    return state


def optimize_content(state: PlatformOptimizerState) -> PlatformOptimizerState:
    """
    Node 2: Optimize content for platform using AI.

    Args:
        state: Current workflow state

    Returns:
        Updated state with optimized_content and format_adjustments
    """
    original = state['original_content']
    rules = state['platform_rules']
    platform = state['platform']

    logger.info(f"Optimizing content for {platform} (original length: {len(original)} chars)")

    openai_client = get_openai_client()

    prompt = f"""
You are a social media expert specializing in {platform}.

Optimize this content for {platform}:

Original Content:
{original}

Platform Rules:
- Optimal length: {rules['optimal_length']} characters
- Recommended hashtags: {rules['recommended_hashtags']}
- Max hashtags: {rules['max_hashtags']}
- Link penalty: {rules['link_penalty']}
- Emoji usage: {rules['emoji_usage']}
- Hook importance: {rules['hook_importance']}

Tasks:
1. Adjust length to optimal (currently: {len(original)} chars)
2. Add {rules['recommended_hashtags']} relevant, specific hashtags (not generic)
3. {'Add emojis strategically' if rules['emoji_usage'] == 'encouraged' else 'Use emojis sparingly' if rules['emoji_usage'] == 'neutral' else 'Avoid emojis - keep professional'}
4. Create strong hook if importance is "{rules['hook_importance']}"
5. {'Move links to end or suggest "link in bio"' if rules['link_penalty'] else 'Links are OK to include'}

Return optimized content in JSON:
{{
    "optimized_content": "...",
    "format_adjustments": ["Added 11 specific hashtags", "Moved link to end", ...],
    "hashtags": ["#hashtag1", "#hashtag2", ...]
}}
"""

    # ⚠️ TECH LEAD REQUIREMENT: Add error handling
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        # Parse response
        response_text = response.choices[0].message.content
        # Clean JSON markers if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]

        result = json.loads(response_text)

        state['optimized_content'] = result['optimized_content']
        state['format_adjustments'] = result.get('format_adjustments', [])

        logger.info(f"Content optimized: {len(state['optimized_content'])} chars, "
                    f"{len(state['format_adjustments'])} adjustments")

    except Exception as e:
        logger.error(f"OpenAI API error during optimization: {e}")
        # Fallback: return original content with basic optimization note
        state['optimized_content'] = original
        state['format_adjustments'] = [f"Error: Using original content - {str(e)[:100]}"]
        state['error'] = str(e)

    return state


def add_timing(state: PlatformOptimizerState) -> PlatformOptimizerState:
    """
    Node 3: Add timing recommendations based on platform rules.

    Args:
        state: Current workflow state

    Returns:
        Updated state with timing_recommendations
    """
    rules = state['platform_rules']
    platform = state['platform']

    logger.info(f"Adding timing recommendations for {platform}")

    best_times = rules.get('best_times', [])
    worst_days = rules.get('worst_days', [])

    recommendations = [
        f"📅 Best posting times for {platform.title()}:",
    ]

    # Add top 3 times
    for time_str in best_times[:3]:
        recommendations.append(f"  • {time_str}")

    # Add worst days warning
    if worst_days:
        recommendations.append(f"\n⚠️ Avoid posting on: {', '.join(worst_days)}")

    # Add platform-specific tips
    if platform == "instagram":
        recommendations.append("\n💡 Pro tip: Reels get 35% more reach than static posts")
        recommendations.append("💡 Use carousel format for 50% more engagement")
    elif platform == "linkedin":
        recommendations.append("\n💡 Pro tip: Put links in COMMENTS (not main post)")
        recommendations.append("💡 Carousel PDFs perform exceptionally well")
    elif platform == "telegram":
        recommendations.append("\n💡 Pro tip: No link penalty - include links freely")
        recommendations.append("💡 Consistent engagement all week (no bad days)")

    state['timing_recommendations'] = recommendations

    logger.info(f"Added {len(recommendations)} timing recommendations")

    return state


def format_output(state: PlatformOptimizerState) -> PlatformOptimizerState:
    """
    Node 4: Format final output with posting guide.

    Args:
        state: Current workflow state

    Returns:
        Updated state with final_content and posting_guide
    """
    optimized = state['optimized_content']
    timing = "\n".join(state['timing_recommendations'])
    adjustments = "\n".join([f"✓ {adj}" for adj in state['format_adjustments']])
    platform = state['platform']
    content_type = state['content_type']

    logger.info(f"Formatting final output for {platform}")

    # Build posting guide
    guide = f"""
🎯 Platform: {platform.title()}
📝 Content Type: {content_type.replace('_', ' ').title()}

⏰ Posting Time Recommendations:
{timing}

✨ Optimizations Applied:
{adjustments}

📊 Optimized Content:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{optimized}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Pro Tip: Test different posting times to find what works best for YOUR audience!
"""

    state['final_content'] = optimized
    state['posting_guide'] = guide

    logger.info("Posting guide formatted successfully")

    return state


# ============================================================================
# Workflow Construction
# ============================================================================

def create_platform_optimizer_workflow():
    """
    Create Platform Optimizer LangGraph workflow.

    Returns:
        Compiled StateGraph workflow
    """
    workflow = StateGraph(PlatformOptimizerState)

    # Add nodes
    workflow.add_node("analyze_platform", analyze_platform)
    workflow.add_node("optimize_content", optimize_content)
    workflow.add_node("add_timing", add_timing)
    workflow.add_node("format_output", format_output)

    # Define flow
    workflow.set_entry_point("analyze_platform")
    workflow.add_edge("analyze_platform", "optimize_content")
    workflow.add_edge("optimize_content", "add_timing")
    workflow.add_edge("add_timing", "format_output")
    workflow.add_edge("format_output", END)

    return workflow.compile()


# ============================================================================
# Main Function
# ============================================================================

def optimize_for_platform(
    content: str,
    platform: str,
    content_type: str = "feed_post"
) -> Dict:
    """
    Optimize content for specific social media platform.

    Args:
        content: Original content to optimize
        platform: Target platform (instagram, facebook, telegram, linkedin)
        content_type: Type of content (feed_post, reel, story, carousel)

    Returns:
        Dict with:
            - optimized_content: Platform-optimized content
            - posting_guide: Full posting guide with recommendations
            - format_adjustments: List of adjustments made
            - error: Error message if any (empty string if success)

    Example:
        >>> result = optimize_for_platform(
        ...     content="Check out our new product!",
        ...     platform="instagram",
        ...     content_type="feed_post"
        ... )
        >>> print(result['optimized_content'])
        "🚀 Stop scrolling! Our new product will change your life..."
    """
    logger.info(f"Starting platform optimization: {platform}, type: {content_type}")

    workflow = create_platform_optimizer_workflow()

    # Initial state
    initial_state = {
        "platform": platform,
        "original_content": content,
        "content_type": content_type,
        "platform_rules": {},
        "optimized_content": "",
        "timing_recommendations": [],
        "format_adjustments": [],
        "final_content": "",
        "posting_guide": "",
        "error": ""
    }

    # Run workflow
    try:
        result = workflow.invoke(initial_state)

        logger.info(f"Platform optimization complete: {platform}")

        return {
            "optimized_content": result['final_content'],
            "posting_guide": result['posting_guide'],
            "format_adjustments": result['format_adjustments'],
            "error": result.get('error', '')
        }

    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return {
            "optimized_content": content,  # Return original on error
            "posting_guide": f"Error: {str(e)}",
            "format_adjustments": [],
            "error": str(e)
        }


# ⚠️ TECH LEAD REQUIREMENT: Add caching for performance
# Recommended implementation for production:
#
# from functools import lru_cache
# import hashlib
#
# @lru_cache(maxsize=100)
# def optimize_for_platform_cached(content_hash: str, platform: str, content_type: str):
#     """Cached version of optimize_for_platform (24-hour TTL recommended)."""
#     # Use hashlib.md5(content.encode()).hexdigest() for content_hash
#     # This prevents re-optimizing identical content multiple times
#     pass
