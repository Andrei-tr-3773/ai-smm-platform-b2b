# video_script_agent.py
"""
Video Script Generator Agent

Generates shot-by-shot viral video scripts based on campaign content and viral patterns.

Workflow:
1. analyze_campaign: Extract campaign intent and metadata
2. select_viral_pattern: Choose best pattern from database
3. generate_script: Create shot-by-shot script sections
4. add_production_notes: Add camera, lighting, audio guidance
5. predict_virality: Score viral potential (0-100)
"""
import json
import logging
from typing import TypedDict, List, Dict, Optional
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from utils.viral_patterns import ViralPatternsDB
from utils.api_cost_tracker import track_openai_request
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoScriptState(TypedDict):
    """State schema for Video Script Generator workflow."""
    # Inputs
    campaign_content: str  # Campaign text/idea from user
    platform: str  # instagram_reels, tiktok, youtube_shorts, facebook_video, linkedin
    target_audience: str  # e.g., "small business owners", "fitness enthusiasts"
    content_goal: str  # e.g., "announce new class", "promote discount"

    # Intermediate states
    campaign_analysis: Dict  # Parsed campaign intent (content_type, industry, etc.)
    selected_pattern: Dict  # Chosen viral pattern
    script_sections: List[Dict]  # Generated script sections
    production_notes: Dict  # Camera angles, lighting, audio
    virality_prediction: Dict  # Viral potential score and analysis

    # Outputs
    full_script: str  # Complete formatted script
    error: str  # Error message if any


class VideoScriptAgent:
    """
    Video Script Generator Agent

    Converts marketing campaigns into shot-by-shot viral video scripts
    using scientifically-validated viral patterns.
    """

    def __init__(self, model):
        self.model = model
        self.patterns_db = ViralPatternsDB()
        self.graph = self._initialize_graph()
        logger.info("VideoScriptAgent initialized.")

    def _initialize_graph(self):
        """Initialize LangGraph state machine with 5-node workflow."""
        try:
            graph = StateGraph(VideoScriptState)

            # Add nodes
            graph.add_node("analyze_campaign", self.analyze_campaign)
            graph.add_node("select_viral_pattern", self.select_viral_pattern)
            graph.add_node("generate_script", self.generate_script)
            graph.add_node("add_production_notes", self.add_production_notes)
            graph.add_node("predict_virality", self.predict_virality)

            # Connect nodes sequentially
            graph.add_edge("analyze_campaign", "select_viral_pattern")
            graph.add_edge("select_viral_pattern", "generate_script")
            graph.add_edge("generate_script", "add_production_notes")
            graph.add_edge("add_production_notes", "predict_virality")
            graph.add_edge("predict_virality", END)

            # Set entry point
            graph.set_entry_point("analyze_campaign")

            logger.info("VideoScriptAgent StateGraph initialized and compiled.")
            return graph.compile()
        except Exception as e:
            logger.error(f"Error initializing VideoScriptAgent StateGraph: {e}")
            raise

    def analyze_campaign(self, state: VideoScriptState) -> VideoScriptState:
        """
        Node 1: Analyze campaign content and extract structured intent.

        Example:
        Input: "Announce new HIIT class with Sarah on Saturday at 10 AM"
        Output: {
            "content_type": "announcement",
            "industry": "fitness",
            "key_message": "new class availability",
            "urgency": "time-sensitive",
            "emotion": "exciting"
        }
        """
        try:
            campaign = state['campaign_content']
            target_audience = state.get('target_audience', 'general audience')
            content_goal = state.get('content_goal', 'engage')

            logger.info(f"Analyzing campaign: {campaign[:100]}...")

            prompt = f"""Analyze this marketing campaign for video script generation:

Campaign: "{campaign}"
Target Audience: "{target_audience}"
Goal: "{content_goal}"

Extract the core intent and characteristics. Return JSON:
{{
    "content_type": "announcement|tutorial|promotion|story|transformation|testimonial|event",
    "industry": "fitness|ecommerce|saas|consulting|education|food|generic",
    "key_message": "main message in 5-10 words",
    "urgency": "immediate|time-sensitive|evergreen",
    "emotion": "exciting|helpful|inspiring|urgent|surprising|educational",
    "hook_opportunity": "what makes this scroll-stopping (one sentence)"
}}

IMPORTANT: Be specific about content_type and industry for pattern matching.
"""

            # Use JSON mode for reliable output
            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "video_script", "step": "analyze_campaign"}
            )

            # Parse JSON
            campaign_analysis = json.loads(response.content.strip())
            logger.info(f"Campaign analyzed: {campaign_analysis.get('content_type')} / {campaign_analysis.get('industry')}")

            return {
                'campaign_analysis': campaign_analysis,
                'script_sections': [],
                'production_notes': {},
                'virality_prediction': {},
                'full_script': '',
                'error': ''
            }
        except Exception as e:
            logger.error(f"Error analyzing campaign: {e}")
            return {'error': f"Campaign analysis failed: {str(e)}"}

    def select_viral_pattern(self, state: VideoScriptState) -> VideoScriptState:
        """
        Node 2: Select best viral pattern based on campaign analysis.

        Uses ViralPatternsDB to find top 3 matches, then AI selects the best.
        """
        try:
            campaign_analysis = state['campaign_analysis']
            platform = state['platform']
            content_type = campaign_analysis.get('content_type', 'generic')

            logger.info(f"Selecting viral pattern for {content_type} on {platform}")

            # Find top 3 matching patterns from database
            candidate_patterns = self.patterns_db.find_best_patterns(
                content_type=content_type,
                platform=platform,
                top_n=3
            )

            if not candidate_patterns:
                # Fallback: get any patterns for this platform
                logger.warning(f"No specific patterns for {content_type}, using platform defaults")
                candidate_patterns = self.patterns_db.find_patterns_by_platform(platform)[:3]

            if not candidate_patterns:
                return {'error': f"No viral patterns found for platform: {platform}"}

            # Use AI to select the best pattern
            prompt = f"""Select the best viral pattern for this campaign:

Campaign Analysis: {json.dumps(campaign_analysis, indent=2)}
Platform: {platform}

Available Patterns:
{json.dumps([
    {
        'id': p['id'],
        'name': p['name'],
        'success_rate': f"{p['success_rate']:.0%}",
        'avg_views': f"{p['avg_views']:,}",
        'best_for': p['best_for']
    } for p in candidate_patterns
], indent=2)}

Which pattern fits best? Consider:
- Content type match
- Emotional tone alignment
- Platform optimization
- Success rate

Return JSON:
{{
    "selected_pattern_id": "pattern_id",
    "reason": "2-3 sentence explanation of why this pattern is optimal"
}}
"""

            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "video_script", "step": "select_pattern"}
            )

            # Parse selection
            selection = json.loads(response.content.strip())
            pattern_id = selection.get('selected_pattern_id')
            reason = selection.get('reason', 'Best match')

            # Get full pattern details
            selected_pattern = self.patterns_db.get_pattern_by_id(pattern_id)

            if not selected_pattern:
                # Fallback to first candidate
                logger.warning(f"Pattern {pattern_id} not found, using first candidate")
                selected_pattern = candidate_patterns[0]

            logger.info(f"Selected pattern: {selected_pattern['name']} - {reason}")

            return {
                'selected_pattern': selected_pattern
            }
        except Exception as e:
            logger.error(f"Error selecting viral pattern: {e}")
            return {'error': f"Pattern selection failed: {str(e)}"}

    def generate_script(self, state: VideoScriptState) -> VideoScriptState:
        """
        Node 3: Generate shot-by-shot video script based on selected pattern.

        Output: List of script sections with timing, text, shot, and action.
        """
        try:
            campaign = state['campaign_content']
            campaign_analysis = state['campaign_analysis']
            pattern = state['selected_pattern']
            platform = state['platform']

            logger.info(f"Generating script using pattern: {pattern['name']}")

            # Platform duration limits
            duration_limits = {
                "instagram_reels": "15-30 seconds",
                "tiktok": "15-60 seconds",
                "youtube_shorts": "15-60 seconds",
                "facebook_video": "30-90 seconds",
                "linkedin": "30-60 seconds"
            }
            max_duration = duration_limits.get(platform, "30 seconds")

            prompt = f"""Generate a shot-by-shot video script for this campaign:

Campaign: "{campaign}"
Campaign Analysis: {json.dumps(campaign_analysis, indent=2)}
Platform: {platform} (max duration: {max_duration})

Viral Pattern: {pattern['name']}
Pattern Structure: {json.dumps(pattern['pattern'], indent=2)}

Create a detailed script following the pattern structure. For each section:
- timing: exact seconds (e.g., "0-3 seconds")
- text: what is said or shown on screen (text overlay or voiceover)
- shot: camera angle and framing (e.g., "close-up face", "overhead shot")
- action: what happens visually (e.g., "trainer demonstrates exercise")

Return JSON with "sections" array:
{{
    "sections": [
        {{
            "section": "hook",
            "timing": "0-3 seconds",
            "text": "compelling hook text",
            "shot": "camera angle description",
            "action": "visual action description"
        }},
        ... (continue for all pattern sections)
    ]
}}

CRITICAL VIRAL ELEMENTS:
- Hook MUST grab attention in first 3 seconds (use surprise, curiosity, or transformation)
- Include pattern interrupt (something unexpected)
- Make it shareable (emotional resonance)
- Authentic tone (not overly scripted)
- Mobile-first framing (vertical 9:16)
"""

            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "video_script", "step": "generate_script"}
            )

            # Parse script
            result = json.loads(response.content.strip())
            script_sections = result.get('sections', [])

            if not script_sections:
                logger.warning("No script sections generated, creating fallback")
                script_sections = [{
                    "section": "hook",
                    "timing": "0-3 seconds",
                    "text": campaign[:100],
                    "shot": "Medium shot",
                    "action": "Person speaking to camera"
                }]

            logger.info(f"Script generated: {len(script_sections)} sections")

            return {
                'script_sections': script_sections
            }
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return {'error': f"Script generation failed: {str(e)}"}

    def add_production_notes(self, state: VideoScriptState) -> VideoScriptState:
        """
        Node 4: Add practical production guidance (camera, lighting, audio, editing).

        Output: Production notes dict with achievable recommendations for non-professionals.
        """
        try:
            script_sections = state['script_sections']
            platform = state['platform']
            campaign_analysis = state['campaign_analysis']
            industry = campaign_analysis.get('industry', 'generic')

            logger.info("Adding production notes")

            prompt = f"""Create practical, easy-to-follow production notes for shooting this video:

Script: {json.dumps(script_sections, indent=2)}
Platform: {platform}
Industry: {industry}

Provide step-by-step guidance that a non-professional can follow using just a smartphone.

Return JSON:
{{
    "camera_setup": ["setup instruction 1", "setup instruction 2"],
    "lighting": "lighting recommendation (natural or simple)",
    "audio": {{
        "music": "music style or where to find trending audio",
        "voiceover": "voice style and tone",
        "sound_effects": ["effect 1", "effect 2"]
    }},
    "editing": ["editing tip 1", "editing tip 2"],
    "props": ["prop 1", "prop 2"],
    "location": "where to shoot (specific to industry)",
    "smartphone_tips": ["tip 1", "tip 2"]
}}

KEEP IT SIMPLE:
- Smartphone camera on tripod (or friend holding)
- Natural window light or ring light ($30)
- Free editing apps (CapCut, InShot, VN)
- Props from their existing business
- No expensive equipment needed
"""

            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "video_script", "step": "production_notes"}
            )

            # Parse production notes
            production_notes = json.loads(response.content.strip())

            logger.info("Production notes added successfully")

            return {
                'production_notes': production_notes
            }
        except Exception as e:
            logger.error(f"Error adding production notes: {e}")
            return {'error': f"Production notes failed: {str(e)}"}

    def predict_virality(self, state: VideoScriptState) -> VideoScriptState:
        """
        Node 5: Predict viral potential (0-100 score) based on script quality.

        Analyzes: Hook strength, pattern interrupt, emotional appeal, shareability, platform fit.
        """
        try:
            script_sections = state['script_sections']
            pattern = state['selected_pattern']
            campaign_analysis = state['campaign_analysis']

            logger.info("Predicting virality score")

            prompt = f"""Predict the viral potential of this video script:

Script: {json.dumps(script_sections, indent=2)}
Pattern: {pattern['name']} (historical success rate: {pattern['success_rate']:.0%})
Campaign Type: {campaign_analysis.get('content_type', 'unknown')}

Evaluate on these factors (score each 0-100):
1. **Hook Strength**: Does the first 3 seconds grab attention?
2. **Pattern Interrupt**: Is there something unexpected that breaks scrolling?
3. **Emotional Appeal**: Does it trigger emotion (excitement, curiosity, inspiration)?
4. **Shareability**: Will people want to share this with friends?
5. **Platform Optimization**: Is it optimized for the target platform?

Return JSON:
{{
    "virality_score": 0-100,
    "expected_views": "estimate (e.g., '50k-100k views')",
    "factor_scores": {{
        "hook": 0-100,
        "pattern_interrupt": 0-100,
        "emotional_appeal": 0-100,
        "shareability": 0-100,
        "platform_fit": 0-100
    }},
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "improvements": ["improvement 1", "improvement 2"],
    "viral_probability": "low|medium|high"
}}

SCORING GUIDE:
- 90-100: Viral potential (500k+ views)
- 70-89: High-performing (100k-500k views)
- 50-69: Good engagement (20k-100k views)
- 30-49: Average (5k-20k views)
- 0-29: Needs work (<5k views)
"""

            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "video_script", "step": "predict_virality"}
            )

            # Parse prediction
            virality_prediction = json.loads(response.content.strip())
            virality_score = virality_prediction.get('virality_score', 50)

            logger.info(f"Virality predicted: {virality_score}/100")

            # Format full script
            full_script = self._format_full_script(script_sections, state['production_notes'], virality_prediction)

            return {
                'virality_prediction': virality_prediction,
                'full_script': full_script
            }
        except Exception as e:
            logger.error(f"Error predicting virality: {e}")
            return {'error': f"Virality prediction failed: {str(e)}"}

    def _format_full_script(self, sections: List[Dict], production: Dict, prediction: Dict) -> str:
        """Format complete script as readable markdown."""
        script = f"""# VIDEO SCRIPT
## Viral Score: {prediction.get('virality_score', 0)}/100
**Expected Views:** {prediction.get('expected_views', 'N/A')}
**Viral Probability:** {prediction.get('viral_probability', 'medium').upper()}

---

## SCRIPT SECTIONS

"""
        for i, section in enumerate(sections, 1):
            script += f"""### {i}. {section.get('section', 'Section').upper()} ({section.get('timing', 'N/A')})
**Text/Overlay:** {section.get('text', '')}
**Shot:** {section.get('shot', '')}
**Action:** {section.get('action', '')}

"""

        script += f"""---

## PRODUCTION NOTES

**Camera Setup:**
{chr(10).join(f"- {item}" for item in production.get('camera_setup', []))}

**Lighting:** {production.get('lighting', 'Natural light')}

**Audio:**
- Music: {production.get('audio', {}).get('music', 'Trending audio')}
- Voiceover: {production.get('audio', {}).get('voiceover', 'Clear voice')}
- Sound Effects: {', '.join(production.get('audio', {}).get('sound_effects', []))}

**Editing Tips:**
{chr(10).join(f"- {item}" for item in production.get('editing', []))}

**Props:** {', '.join(production.get('props', []))}
**Location:** {production.get('location', 'Business location')}

**Smartphone Tips:**
{chr(10).join(f"- {item}" for item in production.get('smartphone_tips', []))}

---

## VIRAL ANALYSIS

**Strengths:**
{chr(10).join(f"✅ {item}" for item in prediction.get('strengths', []))}

**Suggested Improvements:**
{chr(10).join(f"⚠️ {item}" for item in prediction.get('improvements', []))}

**Factor Scores:**
{chr(10).join(f"- {k.replace('_', ' ').title()}: {v}/100" for k, v in prediction.get('factor_scores', {}).items())}
"""
        return script

    def generate_video_script_from_campaign(
        self,
        campaign_content: str,
        platform: str,
        target_audience: str = "general audience",
        content_goal: str = "engage and convert"
    ) -> Dict:
        """
        Main entry point: Generate video script from campaign content.

        Args:
            campaign_content: Marketing campaign text or idea
            platform: Target platform (instagram_reels, tiktok, youtube_shorts, etc.)
            target_audience: Target audience description
            content_goal: Goal of the video

        Returns:
            Dict with script_sections, production_notes, virality_prediction, full_script
        """
        try:
            logger.info(f"Starting video script generation for {platform}")

            # Initialize state
            initial_state = {
                'campaign_content': campaign_content,
                'platform': platform,
                'target_audience': target_audience,
                'content_goal': content_goal,
                'campaign_analysis': {},
                'selected_pattern': {},
                'script_sections': [],
                'production_notes': {},
                'virality_prediction': {},
                'full_script': '',
                'error': ''
            }

            # Run workflow
            final_state = self.graph.invoke(initial_state)

            # Check for errors
            if final_state.get('error'):
                logger.error(f"Video script generation failed: {final_state['error']}")
                return final_state

            # Return results
            result = {
                'campaign_analysis': final_state['campaign_analysis'],
                'selected_pattern': final_state['selected_pattern'],
                'script_sections': final_state['script_sections'],
                'production_notes': final_state['production_notes'],
                'virality_prediction': final_state['virality_prediction'],
                'full_script': final_state['full_script'],
                'error': final_state.get('error', '')
            }

            logger.info(f"Video script generation complete: {result['virality_prediction'].get('virality_score', 0)}/100")
            return result
        except Exception as e:
            logger.error(f"Error in generate_video_script_from_campaign: {e}", exc_info=True)
            return {
                'campaign_analysis': {},
                'selected_pattern': {},
                'script_sections': [],
                'production_notes': {},
                'virality_prediction': {},
                'full_script': '',
                'error': f"Video script generation failed: {str(e)}"
            }
