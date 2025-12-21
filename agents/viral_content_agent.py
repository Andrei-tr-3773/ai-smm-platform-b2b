"""Viral Content Agent - generates viral content using proven patterns."""

import json
import logging
from typing import TypedDict, Optional, List, Dict
from pathlib import Path
from langgraph.graph import StateGraph, END
from utils.openai_utils import get_openai_client

logger = logging.getLogger(__name__)

# Lazy initialization of OpenAI client
_openai_client = None

def get_client():
    """Get or create OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = get_openai_client()
    return _openai_client


class ViralContentState(TypedDict):
    """State for viral content generation workflow."""
    # Input
    user_query: str
    platform: str  # instagram, facebook, telegram, linkedin
    industry: str  # fitness, saas, ecommerce, education, consulting, all
    follower_count: int  # 0-10k, 10k-50k, 50k+
    account_type: str  # creator, brand_with_video, brand_static_only
    content_type: str  # video, static, carousel

    # Processing
    all_patterns: List[Dict]
    selected_patterns: List[Dict]  # Top 3 patterns based on criteria
    pattern_scores: Dict[str, float]  # pattern_id -> score
    generated_content: Dict  # pattern_id -> content

    # Output
    best_pattern: Dict
    final_content: str
    hook: str
    body: str
    cta: str
    pattern_name: str
    expected_performance: Dict  # success_rate, avg_views, engagement_boost
    optimization_tips: List[str]
    error: Optional[str]


def load_viral_patterns() -> List[Dict]:
    """Load viral patterns from JSON file."""
    patterns_file = Path(__file__).parent.parent / 'viral' / 'viral_patterns.json'
    try:
        with open(patterns_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
        logger.info(f"Loaded {len(patterns)} viral patterns")
        return patterns
    except Exception as e:
        logger.error(f"Failed to load viral patterns: {e}")
        return []


def select_patterns(state: ViralContentState) -> ViralContentState:
    """Select top 3 viral patterns based on platform, industry, and account type."""
    logger.info("Selecting viral patterns...")

    platform = state['platform']
    industry = state['industry']
    follower_count = state['follower_count']
    account_type = state['account_type']
    content_type = state['content_type']

    all_patterns = state['all_patterns']
    pattern_scores = {}

    # Determine follower tier
    if follower_count < 10000:
        follower_tier = "0-10k"
    elif follower_count < 50000:
        follower_tier = "10k-50k"
    else:
        follower_tier = "50k+"

    for pattern in all_patterns:
        score = 0.0

        # 1. Platform fit (40% weight)
        if platform in pattern.get('works_best_on', []):
            score += 40

        # Check platform caveats
        caveats = pattern.get('platforms_with_caveat', {})
        if platform in caveats and 'Avoid' in caveats[platform]:
            score -= 30  # Penalty for platform mismatch

        # 2. Industry fit (20% weight)
        industry_fit = pattern.get('industry_fit', [])
        if industry in industry_fit or 'all' in industry_fit:
            score += 20

        # 3. Content type match (20% weight)
        required_types = pattern.get('content_type_required', [])
        if content_type in required_types:
            score += 20
        elif required_types and content_type not in required_types:
            score -= 15  # Penalty for content type mismatch

        # 4. Success rate for account type (10% weight)
        success_rates = pattern.get('success_rate_by_account_type', {})
        if account_type in success_rates:
            success_rate = success_rates[account_type]
            score += success_rate * 10  # 0.7 success = 7 points

        # 5. Follower threshold (5% weight)
        threshold = pattern.get('follower_threshold', {})
        min_followers = threshold.get('min', 0)
        optimal_followers = threshold.get('optimal', 10000)

        if follower_count >= min_followers:
            score += 5
        if follower_count >= optimal_followers:
            score += 5  # Bonus for optimal threshold

        # 6. Execution difficulty (5% weight)
        difficulty = pattern.get('execution_difficulty', 'medium')
        if difficulty == 'easy':
            score += 5
        elif difficulty == 'hard':
            score -= 2

        pattern_scores[pattern['pattern_id']] = score

    # Sort patterns by score and select top 3
    sorted_patterns = sorted(
        all_patterns,
        key=lambda p: pattern_scores[p['pattern_id']],
        reverse=True
    )
    selected_patterns = sorted_patterns[:3]

    logger.info(f"Selected patterns: {[p['name'] for p in selected_patterns]}")
    logger.info(f"Pattern scores: {[(p['pattern_id'], pattern_scores[p['pattern_id']]) for p in selected_patterns]}")

    state['selected_patterns'] = selected_patterns
    state['pattern_scores'] = pattern_scores

    return state


def generate_viral_content(state: ViralContentState) -> ViralContentState:
    """Generate content for each selected pattern using OpenAI."""
    logger.info("Generating viral content for selected patterns...")

    user_query = state['user_query']
    selected_patterns = state['selected_patterns']
    platform = state['platform']
    industry = state['industry']

    generated_content = {}

    for pattern in selected_patterns:
        pattern_id = pattern['pattern_id']
        pattern_name = pattern['name']

        # Build prompt
        hook_template = pattern.get('hook_template', '')
        hook_examples = pattern.get('hook_examples', [])
        body_template = pattern.get('body_template', '')
        cta_template = pattern.get('cta_template', '')
        cta_examples = pattern.get('cta_examples', [])

        prompt = f"""You are a viral content creator specializing in {platform} for {industry} businesses.

Generate viral content using the "{pattern_name}" pattern for this query:
"{user_query}"

Pattern Guidelines:
- Hook Template: {hook_template}
- Hook Examples: {', '.join(hook_examples[:2]) if hook_examples else 'N/A'}
- Body Template: {body_template}
- CTA Template: {cta_template}
- CTA Examples: {', '.join(cta_examples[:2]) if cta_examples else 'N/A'}

IMPORTANT:
1. Follow the pattern structure exactly (Hook → Body → CTA)
2. Make the hook SCROLL-STOPPING (first 0.5 seconds matter)
3. Use specific details, not generic templates
4. Drive engagement with the CTA (ask questions, encourage comments)

Return ONLY valid JSON with this structure:
{{
  "hook": "...",
  "body": "...",
  "cta": "..."
}}"""

        try:
            client = get_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.8  # Higher temperature for creativity
            )

            content_json = response.choices[0].message.content
            content_json = content_json.strip().replace('```json', '').replace('```', '')
            content = json.loads(content_json)

            generated_content[pattern_id] = {
                'pattern_name': pattern_name,
                'hook': content.get('hook', ''),
                'body': content.get('body', ''),
                'cta': content.get('cta', ''),
                'pattern': pattern
            }

            logger.info(f"Generated content for pattern: {pattern_name}")

        except Exception as e:
            logger.error(f"Failed to generate content for {pattern_name}: {e}")
            generated_content[pattern_id] = {
                'pattern_name': pattern_name,
                'hook': f"[Error generating hook]",
                'body': f"[Error generating body]",
                'cta': f"[Error generating CTA]",
                'pattern': pattern,
                'error': str(e)
            }

    state['generated_content'] = generated_content

    return state


def optimize_hooks(state: ViralContentState) -> ViralContentState:
    """Optimize hooks and CTAs for maximum engagement."""
    logger.info("Optimizing hooks and CTAs...")

    generated_content = state['generated_content']
    platform = state['platform']

    # For now, select the best pattern (highest score) and optimize it
    pattern_scores = state['pattern_scores']
    best_pattern_id = max(pattern_scores, key=pattern_scores.get)

    best_content = generated_content.get(best_pattern_id)
    if not best_content:
        state['error'] = "No content generated"
        return state

    hook = best_content['hook']
    body = best_content['body']
    cta = best_content['cta']
    pattern = best_content['pattern']

    # Optimization prompt
    prompt = f"""You are a viral content expert. Optimize this {platform} post for maximum engagement:

HOOK: {hook}
BODY: {body}
CTA: {cta}

Optimization criteria:
1. Hook must be SCROLL-STOPPING in first 0.5 seconds
2. Body must provide value or emotion
3. CTA must drive comments/shares (not just likes)

Return ONLY valid JSON:
{{
  "hook": "optimized hook",
  "body": "optimized body",
  "cta": "optimized CTA",
  "optimization_tips": ["tip 1", "tip 2", "tip 3"]
}}"""

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        optimized_json = response.choices[0].message.content
        optimized_json = optimized_json.strip().replace('```json', '').replace('```', '')
        optimized = json.loads(optimized_json)

        state['hook'] = optimized.get('hook', hook)
        state['body'] = optimized.get('body', body)
        state['cta'] = optimized.get('cta', cta)
        state['optimization_tips'] = optimized.get('optimization_tips', [])

    except Exception as e:
        logger.error(f"Optimization failed, using original: {e}")
        state['hook'] = hook
        state['body'] = body
        state['cta'] = cta
        state['optimization_tips'] = []
        state['error'] = f"Optimization error: {str(e)}"

    state['best_pattern'] = pattern
    state['pattern_name'] = pattern['name']

    # Calculate expected performance
    account_type = state['account_type']
    follower_count = state['follower_count']

    success_rates = pattern.get('success_rate_by_account_type', {})
    success_rate = success_rates.get(account_type, 0.5)

    # Determine follower tier
    if follower_count < 10000:
        follower_tier = "0-10k"
    elif follower_count < 50000:
        follower_tier = "10k-50k"
    else:
        follower_tier = "50k+"

    avg_views_by_tier = pattern.get('avg_views_by_follower_tier', {})
    avg_views = avg_views_by_tier.get(follower_tier, 5000)

    engagement_boost = pattern.get('avg_engagement_boost', 2.0)

    state['expected_performance'] = {
        'success_rate': success_rate,
        'avg_views': avg_views,
        'engagement_boost': engagement_boost
    }

    return state


def format_output(state: ViralContentState) -> ViralContentState:
    """Format final output for display."""
    logger.info("Formatting output...")

    hook = state.get('hook', '')
    body = state.get('body', '')
    cta = state.get('cta', '')
    pattern_name = state.get('pattern_name', 'Unknown Pattern')
    expected_perf = state.get('expected_performance', {})
    tips = state.get('optimization_tips', [])

    final_content = f"""🔥 VIRAL CONTENT ({pattern_name})

📍 HOOK:
{hook}

📝 BODY:
{body}

💬 CTA:
{cta}

---

📊 EXPECTED PERFORMANCE:
• Success Rate: {expected_perf.get('success_rate', 0)*100:.0f}%
• Avg Views: {expected_perf.get('avg_views', 0):,}
• Engagement Boost: {expected_perf.get('engagement_boost', 0):.1f}x

💡 OPTIMIZATION TIPS:
{chr(10).join(f'• {tip}' for tip in tips) if tips else '• No additional tips'}
"""

    state['final_content'] = final_content

    return state


def create_viral_content_workflow():
    """Create the viral content generation workflow."""
    workflow = StateGraph(ViralContentState)

    # Add nodes
    workflow.add_node("select_patterns", select_patterns)
    workflow.add_node("generate_viral_content", generate_viral_content)
    workflow.add_node("optimize_hooks", optimize_hooks)
    workflow.add_node("format_output", format_output)

    # Define edges
    workflow.set_entry_point("select_patterns")
    workflow.add_edge("select_patterns", "generate_viral_content")
    workflow.add_edge("generate_viral_content", "optimize_hooks")
    workflow.add_edge("optimize_hooks", "format_output")
    workflow.add_edge("format_output", END)

    return workflow.compile()


def generate_viral_content_for_query(
    user_query: str,
    platform: str = "instagram",
    industry: str = "saas",
    follower_count: int = 5000,
    account_type: str = "brand_static_only",
    content_type: str = "static"
) -> Dict:
    """
    Main function to generate viral content.

    Args:
        user_query: User's content request
        platform: Target platform (instagram, facebook, telegram, linkedin)
        industry: Business industry (fitness, saas, ecommerce, education, consulting, all)
        follower_count: Account follower count
        account_type: Account type (creator, brand_with_video, brand_static_only)
        content_type: Content type (video, static, carousel)

    Returns:
        Dict with final_content, hook, body, cta, pattern_name, expected_performance
    """
    logger.info(f"Generating viral content for: {user_query}")

    # Load patterns
    all_patterns = load_viral_patterns()
    if not all_patterns:
        return {
            'error': 'Failed to load viral patterns',
            'final_content': 'Error: Could not load viral patterns database'
        }

    # Initialize state
    initial_state = {
        'user_query': user_query,
        'platform': platform,
        'industry': industry,
        'follower_count': follower_count,
        'account_type': account_type,
        'content_type': content_type,
        'all_patterns': all_patterns,
        'selected_patterns': [],
        'pattern_scores': {},
        'generated_content': {},
        'best_pattern': {},
        'final_content': '',
        'hook': '',
        'body': '',
        'cta': '',
        'pattern_name': '',
        'expected_performance': {},
        'optimization_tips': [],
        'error': None
    }

    # Run workflow
    try:
        workflow = create_viral_content_workflow()
        result = workflow.invoke(initial_state)

        return {
            'final_content': result['final_content'],
            'hook': result['hook'],
            'body': result['body'],
            'cta': result['cta'],
            'pattern_name': result['pattern_name'],
            'expected_performance': result['expected_performance'],
            'optimization_tips': result['optimization_tips'],
            'selected_patterns': result['selected_patterns'],
            'error': result.get('error')
        }

    except Exception as e:
        logger.error(f"Viral content generation failed: {e}", exc_info=True)
        return {
            'error': str(e),
            'final_content': f'Error generating viral content: {str(e)}'
        }


if __name__ == "__main__":
    # Test the agent
    import os
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file
    logging.basicConfig(level=logging.INFO)

    result = generate_viral_content_for_query(
        user_query="Launch our new SaaS product that helps teams collaborate better",
        platform="linkedin",
        industry="saas",
        follower_count=8000,
        account_type="brand_static_only",
        content_type="static"
    )

    print("\n" + "="*60)
    print(result['final_content'])
    print("="*60)
