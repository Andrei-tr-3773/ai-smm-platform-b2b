"""
Analytics Agent for campaign performance analysis.

This agent uses a 4-node LangGraph workflow to analyze campaign metrics and generate
insights explaining WHY content performed the way it did - the killer feature!

Workflow:
1. analyze_performance - Compare with industry benchmarks
2. detect_patterns - Detect engagement patterns (spikes, declines, etc.)
3. generate_insights - Explain WHY content performed (KILLER FEATURE)
4. generate_recommendations - Generate actionable next steps
"""

import json
import logging
from datetime import date
from typing import TypedDict, List, Dict, Optional

from langgraph.graph import StateGraph, END
from openai import OpenAI

from analytics.analytics_models import (
    CampaignMetrics,
    BenchmarkData,
    EngagementPattern,
    ContentInsight,
)
from utils.openai_utils import get_openai_client

logger = logging.getLogger(__name__)


# State Schema
class AnalyticsState(TypedDict):
    """State for Analytics workflow."""
    campaign_id: str
    metrics: List[CampaignMetrics]  # 30 days of data
    benchmark: BenchmarkData

    # Analysis results
    performance_summary: Dict  # overall, above_average, etc.
    detected_patterns: List[EngagementPattern]
    content_insights: List[ContentInsight]
    recommendations: List[str]
    next_month_strategy: str

    error: str


# Node 1: Analyze Performance
def analyze_performance(state: AnalyticsState) -> AnalyticsState:
    """
    Compare campaign performance with benchmarks.

    Output:
    {
        "overall_rating": "excellent|good|average|below_average",
        "vs_benchmark": "+45% above industry average",
        "total_views": 125000,
        "total_engagement": 5625,
        "avg_engagement_rate": 0.045,
        "best_day": {"date": "2025-12-15", "views": 8500},
        "worst_day": {"date": "2025-12-22", "views": 450}
    }
    """
    metrics = state['metrics']
    benchmark = state['benchmark']

    # Calculate totals
    total_views = sum(m.views for m in metrics)
    total_engagement = sum(m.likes + m.comments + m.shares for m in metrics)
    avg_engagement_rate = total_engagement / total_views if total_views > 0 else 0

    # Find best/worst days
    best_day = max(metrics, key=lambda m: m.views)
    worst_day = min(metrics, key=lambda m: m.views)

    # Compare with benchmark
    vs_benchmark_pct = ((avg_engagement_rate / benchmark.avg_engagement_rate) - 1) * 100

    # Determine rating
    if avg_engagement_rate >= benchmark.p90_engagement:
        rating = "excellent"
    elif avg_engagement_rate >= benchmark.p75_engagement:
        rating = "good"
    elif avg_engagement_rate >= benchmark.p50_engagement:
        rating = "average"
    else:
        rating = "below_average"

    performance_summary = {
        "overall_rating": rating,
        "vs_benchmark": f"{vs_benchmark_pct:+.0f}% {'above' if vs_benchmark_pct > 0 else 'below'} industry average",
        "total_views": total_views,
        "total_engagement": total_engagement,
        "avg_engagement_rate": avg_engagement_rate,
        "best_day": {"date": str(best_day.date), "views": best_day.views},
        "worst_day": {"date": str(worst_day.date), "views": worst_day.views}
    }

    state['performance_summary'] = performance_summary
    logger.info(f"Performance analysis: {rating} ({vs_benchmark_pct:+.0f}% vs benchmark)")

    return state


# Node 2: Detect Patterns
def detect_patterns(state: AnalyticsState) -> AnalyticsState:
    """
    Detect engagement patterns using AI.

    Patterns to detect:
    - Viral spikes (sudden 3x+ increase)
    - Weekend drops (consistent Sat/Sun decrease)
    - Trending growth (increasing trend over time)
    - Steep decline (sharp drop after initial surge)
    - Consistent performance (stable engagement)
    """
    metrics = state['metrics']
    openai_client = get_openai_client()

    # Prepare data for AI analysis
    metrics_summary = [
        {
            "date": str(m.date),
            "views": m.views,
            "engagement_rate": f"{m.engagement_rate:.3f}",
            "weekday": m.date.strftime("%A")
        }
        for m in metrics
    ]

    prompt = f"""
Analyze these 30 days of campaign metrics and detect engagement patterns:

Metrics: {json.dumps(metrics_summary, indent=2)}

Detect patterns such as:
1. Viral Spike - Sudden 3x+ increase in views/engagement on specific day(s)
2. Weekend Drop - Consistent decrease on Saturdays/Sundays
3. Trending Growth - Steady increase over time
4. Steep Decline - Sharp drop after initial surge
5. Consistent Performance - Stable engagement throughout

Return JSON:
{{
    "patterns": [
        {{
            "pattern_type": "spike|decline|weekend_drop|consistent|trending",
            "description": "Spike on Dec 15 (+350% views)",
            "date_range": ["2025-12-15", "2025-12-17"],
            "impact": "high|medium|low"
        }},
        ...
    ]
}}

Only report patterns that are clearly visible in the data.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        # Clean JSON markers if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)
        patterns = [
            EngagementPattern(
                pattern_type=p["pattern_type"],
                description=p["description"],
                date_range=(date.fromisoformat(p["date_range"][0]), date.fromisoformat(p["date_range"][1])),
                impact=p["impact"]
            )
            for p in result.get("patterns", [])
        ]

        state['detected_patterns'] = patterns
        logger.info(f"Detected {len(patterns)} engagement patterns")

    except Exception as e:
        logger.error(f"Error detecting patterns: {e}")
        state['detected_patterns'] = []

    return state


# Node 3: Generate Insights (WHY)
def generate_insights(state: AnalyticsState) -> AnalyticsState:
    """
    Use AI to explain WHY content performed well or poorly.

    This is the KILLER FEATURE - explaining WHY.

    Example insights:
    - "Hook in first 3 seconds grabbed attention (spike on Dec 15)"
    - "Weekend posting hurt performance (-40% views Sat/Sun)"
    - "Platform timing was optimal (posted during peak hours 7-9 PM)"
    - "Video length (28 sec) matched platform sweet spot for Instagram Reels"
    """
    performance = state['performance_summary']
    patterns = state['detected_patterns']
    campaign_id = state['campaign_id']
    openai_client = get_openai_client()

    prompt = f"""
You are an expert social media analyst. Explain WHY this campaign performed the way it did.

Performance Summary:
{json.dumps(performance, indent=2)}

Detected Patterns:
{json.dumps([{"type": p.pattern_type, "desc": p.description, "impact": p.impact} for p in patterns], indent=2)}

Generate insights explaining WHY the content performed this way. Focus on actionable factors:
- Hook effectiveness (first 3 seconds)
- Posting timing (time of day, day of week)
- Platform optimization (video length, format, etc.)
- Audience targeting
- Visual appeal
- Trending audio/hashtags

Return JSON:
{{
    "insights": [
        {{
            "insight_type": "hook|timing|platform_fit|audience_match|visual_appeal",
            "explanation": "Hook in first 3 seconds grabbed attention (spike on Dec 15)",
            "confidence": 0.85,
            "evidence": ["Views spiked 350% on day of posting", "Engagement rate 2x higher than average"]
        }},
        ...
    ]
}}

Provide 3-5 specific, actionable insights.
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        # Clean JSON markers if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)
        insights = [
            ContentInsight(
                campaign_id=campaign_id,
                insight_type=i["insight_type"],
                explanation=i["explanation"],
                confidence=i["confidence"],
                evidence=i["evidence"]
            )
            for i in result.get("insights", [])
        ]

        state['content_insights'] = insights
        logger.info(f"Generated {len(insights)} content insights")

    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        state['content_insights'] = []

    return state


# Node 4: Generate Recommendations
def generate_recommendations(state: AnalyticsState) -> AnalyticsState:
    """
    Generate actionable recommendations for next campaigns.

    Example recommendations:
    - "Post on Wednesday-Thursday for best engagement (40% higher than weekend)"
    - "Keep video length under 30 seconds (current best performers: 25-28 sec)"
    - "Use strong hook in first 3 seconds (current spike content had direct eye contact)"
    - "Replicate 'fitness challenge' format (3 campaigns using this format outperformed by 2x)"
    """
    performance = state['performance_summary']
    insights = state['content_insights']
    patterns = state['detected_patterns']
    openai_client = get_openai_client()

    prompt = f"""
Based on this campaign analysis, generate 5-7 actionable recommendations for future campaigns.

Performance: {json.dumps(performance, indent=2)}
Insights: {json.dumps([i.explanation for i in insights], indent=2)}
Patterns: {json.dumps([p.description for p in patterns], indent=2)}

Recommendations should be:
1. Specific (not generic advice)
2. Actionable (user can implement immediately)
3. Data-driven (based on observed patterns)

Return JSON:
{{
    "recommendations": [
        "Post on Wednesday-Thursday for best engagement (40% higher than weekend)",
        "Keep video length under 30 seconds",
        ...
    ],
    "next_month_strategy": "Focus on mid-week posting with strong hooks in first 3 seconds. Replicate successful 'fitness challenge' format that drove 350% spike on Dec 15. Avoid weekend posting which consistently underperformed by 30%."
}}
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        # Clean JSON markers if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = json.loads(content)

        state['recommendations'] = result.get("recommendations", [])
        state['next_month_strategy'] = result.get("next_month_strategy", "")

        logger.info(f"Generated {len(state['recommendations'])} recommendations")

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        state['recommendations'] = []
        state['next_month_strategy'] = ""

    return state


# Build LangGraph
def create_analytics_workflow():
    """Create the Analytics LangGraph workflow."""
    workflow = StateGraph(AnalyticsState)

    workflow.add_node("analyze_performance", analyze_performance)
    workflow.add_node("detect_patterns", detect_patterns)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("generate_recommendations", generate_recommendations)

    workflow.set_entry_point("analyze_performance")
    workflow.add_edge("analyze_performance", "detect_patterns")
    workflow.add_edge("detect_patterns", "generate_insights")
    workflow.add_edge("generate_insights", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()


# Main function
def analyze_campaign(
    campaign_id: str,
    metrics: List[CampaignMetrics],
    benchmark: BenchmarkData
) -> Dict:
    """
    Analyze campaign performance and generate insights.

    Args:
        campaign_id: Campaign identifier
        metrics: 30 days of engagement metrics
        benchmark: Industry benchmark data

    Returns:
        Dict with performance_summary, patterns, insights, recommendations
    """
    workflow = create_analytics_workflow()

    initial_state = {
        "campaign_id": campaign_id,
        "metrics": metrics,
        "benchmark": benchmark,
        "performance_summary": {},
        "detected_patterns": [],
        "content_insights": [],
        "recommendations": [],
        "next_month_strategy": "",
        "error": ""
    }

    try:
        result = workflow.invoke(initial_state)

        return {
            "performance_summary": result['performance_summary'],
            "detected_patterns": result['detected_patterns'],
            "content_insights": result['content_insights'],
            "recommendations": result['recommendations'],
            "next_month_strategy": result['next_month_strategy'],
            "error": result.get('error', '')
        }
    except Exception as e:
        logger.error(f"Error analyzing campaign: {e}")
        return {
            "performance_summary": {},
            "detected_patterns": [],
            "content_insights": [],
            "recommendations": [],
            "next_month_strategy": "",
            "error": str(e)
        }
