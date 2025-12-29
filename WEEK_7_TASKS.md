# Week 7: Content Tools (Blog/SEO & Enhanced Copywriting)

**Duration:** 20 hours
**Priority:** VALUE-ADD
**Business Impact:** Enable blog content creation + improve copy quality
**ROI:** Content marketing channel + higher conversion rates

---

## 📋 Overview

**From REVISED_DEVELOPMENT_PLAN.md:**
> **Goal:** Blog/SEO and enhanced copywriting
>
> Enable users to:
> - Generate SEO-optimized blog posts for content marketing
> - Create multiple copy variations to test what works
> - Improve copywriting quality with consistency checks

**What We're Building:**
1. **Blog & SEO Generator** - AI-powered blog post creation with SEO optimization
2. **Copywriting Improvements** - Generate 5 variations per campaign with different angles

---

## 🎯 Business Value

### Why Blog/SEO Generator?

**Current Pain:** Users have no way to create blog content for SEO/content marketing
- Can't drive organic traffic
- No top-of-funnel content
- Competitors rank higher on Google

**Solution:** AI-powered blog generator
- SEO keyword research
- Optimized article structure
- Meta tags generation
- Readability optimization

**Expected Impact:**
- +30% organic traffic in 6 months
- +15% inbound leads
- Better brand authority

### Why Copy Variations?

**Current Pain:** Users get 1 version of copy, don't know what works
- No A/B testing
- Miss better angles
- Lower conversion rates

**Solution:** Generate 5 variations with different approaches
- Problem-solution angle
- Curiosity-driven angle
- Social proof angle
- FOMO (urgency) angle
- Benefit-focused angle

**Expected Impact:**
- +20% click-through rates
- +15% conversion rates
- Users learn what resonates

---

## 📅 Week 7 Tasks

### Task 7.1: Blog & SEO Generator (12 hours)

**Goal:** Enable AI blog post generation with SEO optimization

#### 7.1.1: Blog Post Agent (LangGraph) (4 hours)

**Architecture:**
```python
# agents/blog_generator_agent.py

StateGraph workflow:
1. analyze_topic (understand user topic + target keywords)
2. research_keywords (suggest SEO keywords using heuristics)
3. generate_outline (create article structure with H2/H3 headings)
4. generate_content (write full blog post sections)
5. optimize_seo (add meta tags, keyword density check)
6. check_readability (Flesch score, sentence length, paragraph length)
```

**State Schema:**
```python
@dataclass
class BlogGeneratorState:
    messages: List[BaseMessage]
    topic: str
    target_keywords: List[str]  # e.g., ["AI social media", "content marketing"]
    outline: dict  # {h2: [h3 headings]}
    content: str  # Full blog post markdown
    meta_title: str  # SEO title (60 chars)
    meta_description: str  # SEO description (160 chars)
    readability_score: float  # Flesch Reading Ease (60-70 target)
    word_count: int
    keyword_density: dict  # {keyword: percentage}
```

**Implementation:**
```python
class BlogGeneratorAgent:
    def __init__(self, model):
        self.model = model
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(BlogGeneratorState)

        # Nodes
        workflow.add_node("analyze_topic", self.analyze_topic)
        workflow.add_node("research_keywords", self.research_keywords)
        workflow.add_node("generate_outline", self.generate_outline)
        workflow.add_node("generate_content", self.generate_content)
        workflow.add_node("optimize_seo", self.optimize_seo)
        workflow.add_node("check_readability", self.check_readability)

        # Edges
        workflow.set_entry_point("analyze_topic")
        workflow.add_edge("analyze_topic", "research_keywords")
        workflow.add_edge("research_keywords", "generate_outline")
        workflow.add_edge("generate_outline", "generate_content")
        workflow.add_edge("generate_content", "optimize_seo")
        workflow.add_edge("optimize_seo", "check_readability")
        workflow.add_edge("check_readability", END)

        return workflow.compile()

    def analyze_topic(self, state: BlogGeneratorState):
        """Analyze user topic and extract intent."""
        # Prompt LLM to understand topic + identify industry
        pass

    def research_keywords(self, state: BlogGeneratorState):
        """Suggest SEO keywords (heuristic-based, not Google API)."""
        # Generate related keywords based on topic
        # E.g., "AI social media" -> ["AI content generation", "automated social posts"]
        pass

    def generate_outline(self, state: BlogGeneratorState):
        """Create article outline with headings."""
        # Prompt LLM to generate:
        # - Introduction hook
        # - 5-7 H2 headings
        # - 2-3 H3 subheadings per H2
        # - Conclusion with CTA
        pass

    def generate_content(self, state: BlogGeneratorState):
        """Write full blog post based on outline."""
        # For each section in outline, generate 200-400 words
        # Include examples, statistics, actionable tips
        pass

    def optimize_seo(self, state: BlogGeneratorState):
        """Add meta tags and check keyword density."""
        # Generate meta_title (60 chars, keyword-rich)
        # Generate meta_description (160 chars, CTA)
        # Check keyword density (2-3% target)
        pass

    def check_readability(self, state: BlogGeneratorState):
        """Calculate readability score."""
        # Flesch Reading Ease formula
        # Target: 60-70 (8th-9th grade level)
        # Suggest improvements if too complex
        pass
```

**Deliverable:**
- ✅ BlogGeneratorAgent with 6-node workflow
- ✅ Keyword research (heuristic)
- ✅ SEO meta tags generated
- ✅ Readability score calculated

---

#### 7.1.2: Blog UI & Export (4 hours)

**UI Features:**
```python
# In Home.py or new pages/07_Blog_Generator.py

st.title("📝 Blog & SEO Generator")

# Input
topic = st.text_input(
    "Blog Topic",
    placeholder="E.g., 'How to use AI for social media marketing'",
    help="What do you want to write about?"
)

target_audience = st.selectbox(
    "Target Audience",
    ["Small business owners", "Marketing managers", "Digital agencies", "General public"]
)

tone = st.selectbox(
    "Tone",
    ["Professional", "Casual", "Educational", "Persuasive"]
)

word_count_target = st.slider("Target Word Count", 800, 3000, 1500, 200)

if st.button("Generate Blog Post", type="primary"):
    with st.spinner("Generating blog post..."):
        # Call BlogGeneratorAgent
        result = blog_agent.generate(topic, target_audience, tone, word_count_target)

    # Display results
    st.success("✅ Blog post generated!")

    # Meta tags (collapsible)
    with st.expander("🔍 SEO Meta Tags", expanded=False):
        st.text_input("Meta Title", value=result['meta_title'], disabled=True)
        st.text_area("Meta Description", value=result['meta_description'], disabled=True)

        # Keyword density
        st.markdown("**Keyword Density:**")
        for keyword, density in result['keyword_density'].items():
            st.metric(keyword, f"{density:.1f}%")

    # Readability score
    with st.expander("📊 Readability Analysis", expanded=False):
        score = result['readability_score']
        if score >= 60:
            st.success(f"✅ Readability Score: {score:.1f} (Good)")
        else:
            st.warning(f"⚠️ Readability Score: {score:.1f} (Too complex)")

        st.info(f"Word Count: {result['word_count']} words")

    # Main content
    st.markdown("---")
    st.markdown("### Generated Blog Post")

    # Show outline first
    with st.expander("📋 Article Outline", expanded=True):
        st.json(result['outline'])

    # Show full content
    st.markdown(result['content'])

    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        # Markdown export
        st.download_button(
            "💾 Download Markdown",
            data=result['content'],
            file_name=f"blog_{topic[:30]}.md",
            mime="text/markdown"
        )

    with col2:
        # HTML export
        html_content = markdown.markdown(result['content'])
        st.download_button(
            "🌐 Download HTML",
            data=html_content,
            file_name=f"blog_{topic[:30]}.html",
            mime="text/html"
        )

    with col3:
        # WordPress-ready format (HTML with meta tags)
        wordpress_content = f"""
<!-- SEO Meta Tags -->
<!-- Title: {result['meta_title']} -->
<!-- Description: {result['meta_description']} -->

{html_content}
        """
        st.download_button(
            "📄 Download WordPress",
            data=wordpress_content,
            file_name=f"blog_{topic[:30]}_wordpress.html",
            mime="text/html"
        )
```

**Deliverable:**
- ✅ Blog generator UI in Streamlit
- ✅ SEO meta tags display
- ✅ Readability score visualization
- ✅ Export as Markdown/HTML/WordPress

---

#### 7.1.3: SEO Keyword Utilities (2 hours)

**Keyword Research Module:**
```python
# utils/seo_utils.py

def suggest_keywords(topic: str, count: int = 10) -> List[str]:
    """
    Suggest SEO keywords based on topic (heuristic-based).

    Note: NOT using Google Keyword Planner API (requires billing).
    Using LLM to suggest related keywords.
    """
    prompt = f"""
    Given the blog topic: "{topic}"

    Suggest {count} SEO keywords that people might search for.
    Include:
    - Long-tail keywords (3-5 words)
    - Question-based keywords ("how to...", "what is...")
    - Comparison keywords ("vs", "best...")

    Return as JSON array: ["keyword1", "keyword2", ...]
    """
    # Call LLM
    response = llm.invoke(prompt)
    keywords = json.loads(response)
    return keywords


def calculate_keyword_density(content: str, keywords: List[str]) -> dict:
    """Calculate keyword density as percentage."""
    word_count = len(content.split())
    density = {}

    for keyword in keywords:
        count = content.lower().count(keyword.lower())
        density[keyword] = (count / word_count) * 100

    return density


def calculate_readability(text: str) -> float:
    """
    Calculate Flesch Reading Ease score.

    Formula:
    206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)

    Score interpretation:
    - 90-100: Very easy (5th grade)
    - 60-70: Standard (8th-9th grade) <- TARGET
    - 30-50: Difficult (college)
    - 0-30: Very difficult (graduate)
    """
    sentences = text.count('.') + text.count('!') + text.count('?')
    words = len(text.split())
    syllables = sum([count_syllables(word) for word in text.split()])

    if sentences == 0 or words == 0:
        return 0

    score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    return max(0, min(100, score))


def count_syllables(word: str) -> int:
    """Count syllables in a word (approximation)."""
    vowels = 'aeiouy'
    word = word.lower()
    count = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        count -= 1

    return max(1, count)


def optimize_meta_tags(content: str, keywords: List[str]) -> dict:
    """Generate SEO-optimized meta tags."""
    # Extract first heading as base
    lines = content.split('\n')
    title_base = lines[0].replace('#', '').strip()

    # Meta title (60 chars max, include primary keyword)
    primary_keyword = keywords[0] if keywords else ""
    meta_title = f"{title_base} - {primary_keyword}"[:60]

    # Meta description (160 chars max, include CTA)
    first_paragraph = lines[2] if len(lines) > 2 else content[:200]
    meta_description = f"{first_paragraph[:140]}... Read more."[:160]

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "canonical_url": f"/blog/{title_base.lower().replace(' ', '-')}",
        "og_image": "https://example.com/blog-image.jpg"  # placeholder
    }
```

**Deliverable:**
- ✅ Keyword suggestion (LLM-based)
- ✅ Keyword density calculator
- ✅ Readability score (Flesch formula)
- ✅ Meta tags generator

---

#### 7.1.4: Export Formats (2 hours)

**Export Options:**
1. **Markdown** - Plain text with formatting
2. **HTML** - Styled with CSS
3. **WordPress-ready** - HTML with meta tags comments
4. **Medium-ready** - Special formatting for Medium import

```python
# utils/blog_export.py

def export_as_markdown(content: str, meta: dict) -> str:
    """Export blog post as Markdown."""
    return f"""---
title: {meta['meta_title']}
description: {meta['meta_description']}
date: {datetime.now().strftime('%Y-%m-%d')}
keywords: {', '.join(meta.get('keywords', []))}
---

{content}
"""


def export_as_html(content: str, meta: dict) -> str:
    """Export blog post as styled HTML."""
    html_content = markdown.markdown(content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['meta_title']}</title>
    <meta name="description" content="{meta['meta_description']}">
    <meta name="keywords" content="{', '.join(meta.get('keywords', []))}">

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 0.5em; }}
        h2 {{ font-size: 2em; margin-top: 1.5em; color: #2c3e50; }}
        h3 {{ font-size: 1.5em; margin-top: 1.2em; color: #34495e; }}
        p {{ margin: 1em 0; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""


def export_for_wordpress(content: str, meta: dict) -> str:
    """Export blog post for WordPress (HTML with meta comments)."""
    html_content = markdown.markdown(content)

    return f"""<!-- wp:paragraph -->
<!-- SEO Title: {meta['meta_title']} -->
<!-- SEO Description: {meta['meta_description']} -->
<!-- Keywords: {', '.join(meta.get('keywords', []))} -->
<!-- /wp:paragraph -->

{html_content}"""


def export_for_medium(content: str, meta: dict) -> str:
    """Export blog post for Medium (special formatting)."""
    # Medium uses simplified markdown
    # Convert headings, remove complex HTML
    medium_content = content.replace('###', '##')  # Medium only supports H1-H2

    return f"""# {meta['meta_title']}

> {meta['meta_description']}

{medium_content}

---

*Originally published at [your-site.com]*
"""
```

**Deliverable:**
- ✅ Markdown export
- ✅ HTML export with CSS
- ✅ WordPress-ready format
- ✅ Medium-ready format

---

### Task 7.2: Copywriting Improvements (8 hours)

**Goal:** Generate multiple copy variations with different angles

#### 7.2.1: Copy Variation Generator (4 hours)

**Angles to Generate:**
1. **Problem-Solution** - "Struggling with X? Here's how to fix it."
2. **Curiosity** - "You won't believe what happened when..."
3. **Social Proof** - "Join 10,000+ businesses who..."
4. **FOMO** - "Limited time: Don't miss out on..."
5. **Benefit-Focused** - "Get X results in Y days"

**Implementation:**
```python
# agents/copy_variations_agent.py

class CopyVariationsAgent:
    """Generate 5 copy variations with different angles."""

    ANGLES = {
        "problem_solution": {
            "description": "Address pain point + offer solution",
            "prompt_template": """
            Rewrite this campaign copy using Problem-Solution angle:

            Original: {original_copy}

            Rules:
            1. Start with a relatable problem
            2. Agitate the pain (why it's frustrating)
            3. Present solution (product/service)
            4. Clear CTA

            Example format:
            "Tired of [problem]? [Product] helps you [benefit] in [timeframe]."
            """,
            "emoji": "🔧"
        },
        "curiosity": {
            "description": "Create intrigue and curiosity gap",
            "prompt_template": """
            Rewrite this campaign copy using Curiosity angle:

            Original: {original_copy}

            Rules:
            1. Start with surprising fact or question
            2. Create information gap
            3. Tease benefit without revealing all
            4. CTA that promises answer

            Example format:
            "The secret to [outcome] that nobody talks about..."
            """,
            "emoji": "🤔"
        },
        "social_proof": {
            "description": "Leverage numbers and testimonials",
            "prompt_template": """
            Rewrite this campaign copy using Social Proof angle:

            Original: {original_copy}

            Rules:
            1. Start with impressive number (users, results)
            2. Build credibility
            3. Show transformation
            4. CTA to join community

            Example format:
            "Join 10,000+ [audience] who achieved [result]..."
            """,
            "emoji": "⭐"
        },
        "fomo": {
            "description": "Create urgency and scarcity",
            "prompt_template": """
            Rewrite this campaign copy using FOMO angle:

            Original: {original_copy}

            Rules:
            1. Add time constraint (limited time, ending soon)
            2. Add scarcity (limited spots, while supplies last)
            3. Emphasize what they'll miss
            4. Urgent CTA

            Example format:
            "Last chance: Only 3 spots left for [offer]..."
            """,
            "emoji": "⏰"
        },
        "benefit_focused": {
            "description": "Focus on outcomes and results",
            "prompt_template": """
            Rewrite this campaign copy using Benefit-Focused angle:

            Original: {original_copy}

            Rules:
            1. Start with specific outcome
            2. Add timeframe (fast results)
            3. List 3 key benefits
            4. Clear action-oriented CTA

            Example format:
            "Get [specific result] in [timeframe]. No [objection]."
            """,
            "emoji": "🎯"
        }
    }

    def generate_variations(self, original_copy: str) -> dict:
        """Generate 5 variations with different angles."""
        variations = {}

        for angle_name, angle_config in self.ANGLES.items():
            prompt = angle_config["prompt_template"].format(
                original_copy=original_copy
            )

            # Call LLM
            variation = self.model.invoke(prompt)

            variations[angle_name] = {
                "copy": variation,
                "angle": angle_config["description"],
                "emoji": angle_config["emoji"]
            }

        return variations
```

**UI Integration:**
```python
# In Home.py after content generation

if st.checkbox("🎨 Generate Copy Variations (5 different angles)", value=False):
    with st.spinner("Generating variations..."):
        variations = copy_variations_agent.generate_variations(english_content)

    st.markdown("---")
    st.markdown("### 🎨 Copy Variations")

    # Show each variation
    for angle, data in variations.items():
        with st.expander(f"{data['emoji']} {data['angle']}", expanded=False):
            st.markdown(data['copy'])

            # Copy to clipboard button
            st.button(
                "📋 Use This Version",
                key=f"use_{angle}",
                help="Replace original copy with this variation"
            )
```

**Deliverable:**
- ✅ 5 copy variation angles implemented
- ✅ Angle-specific prompts
- ✅ UI to display variations
- ✅ Easy copy/paste or replace original

---

#### 7.2.2: Copy Quality Checks (2 hours)

**Quality Checkers:**
```python
# utils/copy_quality.py

def check_tone_consistency(text: str, target_tone: str) -> dict:
    """
    Check if text matches target tone.

    Args:
        text: Copy text
        target_tone: "professional", "casual", "persuasive", "educational"

    Returns:
        {
            "score": 0-100,
            "issues": ["Too formal for casual tone", ...],
            "suggestions": ["Use contractions", ...]
        }
    """
    prompt = f"""
    Analyze this text for tone consistency:

    Text: {text}
    Target Tone: {target_tone}

    Check:
    1. Word choice matches tone
    2. Sentence structure appropriate
    3. Level of formality correct

    Return JSON:
    {{
        "score": 85,
        "issues": ["Too formal in paragraph 2"],
        "suggestions": ["Use 'you' instead of 'one'"]
    }}
    """
    # Call LLM
    result = llm.invoke(prompt)
    return json.loads(result)


def detect_repetition(text: str) -> dict:
    """Detect repeated words/phrases."""
    words = text.lower().split()
    word_counts = {}

    for word in words:
        if len(word) > 3:  # Ignore short words
            word_counts[word] = word_counts.get(word, 0) + 1

    # Find words used more than 3 times
    repetitive = {word: count for word, count in word_counts.items() if count > 3}

    return {
        "repetitive_words": repetitive,
        "score": 100 - (len(repetitive) * 10),  # Penalty for each repetitive word
        "suggestions": [f"Consider synonyms for '{word}' (used {count}x)"
                       for word, count in repetitive.items()]
    }


def suggest_ab_tests(original_copy: str, variations: dict) -> list:
    """Suggest which variations to A/B test."""
    suggestions = [
        {
            "test_name": "Problem vs Benefit",
            "variant_a": "problem_solution",
            "variant_b": "benefit_focused",
            "hypothesis": "Problem-focused copy may resonate more with users experiencing pain",
            "metric": "Click-through rate"
        },
        {
            "test_name": "Urgency vs Social Proof",
            "variant_a": "fomo",
            "variant_b": "social_proof",
            "hypothesis": "FOMO may drive faster action, social proof builds trust",
            "metric": "Conversion rate"
        },
        {
            "test_name": "Curiosity Hook",
            "variant_a": "curiosity",
            "variant_b": "benefit_focused",
            "hypothesis": "Curiosity may increase engagement, benefits show value",
            "metric": "Time on page"
        }
    ]

    return suggestions
```

**UI Integration:**
```python
# Add to copy variations section

st.markdown("---")
st.markdown("### ✅ Copy Quality Checks")

# Tone consistency
tone_result = check_tone_consistency(english_content, target_tone)
st.metric("Tone Consistency", f"{tone_result['score']}/100")

if tone_result['issues']:
    with st.expander("⚠️ Tone Issues", expanded=False):
        for issue in tone_result['issues']:
            st.warning(issue)
        for suggestion in tone_result['suggestions']:
            st.info(f"💡 {suggestion}")

# Repetition detection
repetition_result = detect_repetition(english_content)
st.metric("Repetition Score", f"{repetition_result['score']}/100")

if repetition_result['repetitive_words']:
    with st.expander("🔁 Repetitive Words", expanded=False):
        for word, count in repetition_result['repetitive_words'].items():
            st.text(f"'{word}' used {count} times")

# A/B test suggestions
with st.expander("🧪 A/B Test Suggestions", expanded=False):
    ab_tests = suggest_ab_tests(english_content, variations)

    for test in ab_tests:
        st.markdown(f"**{test['test_name']}**")
        st.markdown(f"- Variant A: {test['variant_a']}")
        st.markdown(f"- Variant B: {test['variant_b']}")
        st.markdown(f"- Hypothesis: {test['hypothesis']}")
        st.markdown(f"- Metric to track: {test['metric']}")
        st.markdown("---")
```

**Deliverable:**
- ✅ Tone consistency checker
- ✅ Repetition detector
- ✅ A/B test suggestions
- ✅ Quality scores displayed

---

#### 7.2.3: Copy Templates Library (2 hours)

**Pre-built Copy Formulas:**
```python
# utils/copy_templates.py

COPY_FORMULAS = {
    "PAS": {
        "name": "Problem-Agitate-Solve",
        "structure": [
            "Problem: Identify pain point",
            "Agitate: Make it worse",
            "Solve: Present solution"
        ],
        "example": "Tired of [problem]? It gets worse: [agitate]. Here's how [product] solves it.",
        "use_case": "Sales pages, ads"
    },
    "AIDA": {
        "name": "Attention-Interest-Desire-Action",
        "structure": [
            "Attention: Grab attention with hook",
            "Interest: Build interest",
            "Desire: Create desire",
            "Action: Clear CTA"
        ],
        "example": "[Hook]. Here's why it matters: [benefit]. Imagine [outcome]. [CTA].",
        "use_case": "Email marketing, landing pages"
    },
    "4Ps": {
        "name": "Promise-Picture-Proof-Push",
        "structure": [
            "Promise: State benefit",
            "Picture: Paint vision of outcome",
            "Proof: Provide evidence",
            "Push: Drive to action"
        ],
        "example": "[Benefit]. Imagine [outcome]. See what [testimonial]. [CTA].",
        "use_case": "Product launches"
    },
    "BAB": {
        "name": "Before-After-Bridge",
        "structure": [
            "Before: Current pain state",
            "After: Desired outcome",
            "Bridge: How to get there"
        ],
        "example": "Before: [pain]. After: [outcome]. [Product] is the bridge.",
        "use_case": "Transformation stories"
    },
    "FAB": {
        "name": "Features-Advantages-Benefits",
        "structure": [
            "Features: What it has",
            "Advantages: Why it's better",
            "Benefits: What you get"
        ],
        "example": "[Feature] means [advantage], so you get [benefit].",
        "use_case": "Product descriptions"
    }
}


def apply_copy_formula(content: str, formula_name: str) -> str:
    """Apply copy formula to existing content."""
    formula = COPY_FORMULAS.get(formula_name)

    if not formula:
        return content

    prompt = f"""
    Rewrite this content using the {formula['name']} formula:

    Original: {content}

    Structure:
    {chr(10).join(formula['structure'])}

    Example: {formula['example']}
    """

    # Call LLM
    result = llm.invoke(prompt)
    return result
```

**UI Integration:**
```python
# Add copy formula selector

st.markdown("---")
st.markdown("### 📐 Apply Copy Formula")

formula_name = st.selectbox(
    "Choose Formula",
    list(COPY_FORMULAS.keys()),
    format_func=lambda x: f"{x} - {COPY_FORMULAS[x]['name']}"
)

if formula_name:
    formula = COPY_FORMULAS[formula_name]

    with st.expander("ℹ️ About This Formula", expanded=False):
        st.markdown(f"**{formula['name']}**")
        st.markdown("**Structure:**")
        for step in formula['structure']:
            st.markdown(f"- {step}")
        st.markdown(f"**Example:** {formula['example']}")
        st.markdown(f"**Best for:** {formula['use_case']}")

    if st.button("Apply Formula", type="secondary"):
        with st.spinner("Rewriting..."):
            rewritten = apply_copy_formula(english_content, formula_name)

        st.markdown("### ✨ Rewritten Copy")
        st.markdown(rewritten)
```

**Deliverable:**
- ✅ 5 copy formulas (PAS, AIDA, 4Ps, BAB, FAB)
- ✅ Formula explainer
- ✅ Apply formula to existing copy
- ✅ UI integration

---

## 📦 Week 7 Summary

**Total Time:** 20 hours

**Breakdown:**
- Task 7.1: Blog & SEO Generator (12h)
  - 7.1.1: Blog Post Agent (4h)
  - 7.1.2: Blog UI & Export (4h)
  - 7.1.3: SEO Keyword Utilities (2h)
  - 7.1.4: Export Formats (2h)
- Task 7.2: Copywriting Improvements (8h)
  - 7.2.1: Copy Variation Generator (4h)
  - 7.2.2: Copy Quality Checks (2h)
  - 7.2.3: Copy Templates Library (2h)

**Deliverables:**
- ✅ Blog post generation (1500-3000 words)
- ✅ SEO keyword research (LLM-based)
- ✅ Meta tags generation
- ✅ Readability score (Flesch formula)
- ✅ Export as Markdown/HTML/WordPress/Medium
- ✅ 5 copy variations (problem-solution, curiosity, social proof, FOMO, benefit)
- ✅ Tone consistency checker
- ✅ Repetition detector
- ✅ A/B test suggestions
- ✅ 5 copy formulas (PAS, AIDA, 4Ps, BAB, FAB)

**Success Criteria:**
1. Users can generate SEO-optimized blog posts in 2 minutes
2. Blog posts have 60+ readability score (8th-9th grade level)
3. Meta tags are keyword-rich and within character limits
4. Copy variations offer meaningfully different angles
5. Quality checks catch tone/repetition issues
6. Copy formulas are easy to apply

---

## 🚀 Deferred Features (From Week 6)

These features were planned for Week 6 but deferred:

### Stripe Integration (6 hours)
- Setup Stripe account
- Create payment links per tier
- Handle webhooks for subscription events
- Upgrade/downgrade flow
- Invoice generation

**Status:** ⏳ Deferred to Week 8 or later

### OAuth Integration (4 hours)
- Google OAuth (Sign in with Google)
- LinkedIn OAuth (Sign in with LinkedIn)
- Merge accounts flow
- OAuth callback handling

**Status:** ⏳ Deferred to Week 8 or later

### Email Service (4 hours)
- SendGrid setup
- Welcome email on signup
- Email verification flow
- Password reset email
- Usage reminder emails

**Status:** ⏳ Deferred to Week 8 or later

**Reason for Deferral:**
Week 7 focuses on content tools (blog/SEO) per REVISED_DEVELOPMENT_PLAN. Payment integration and OAuth are important but not blocking core functionality. We can validate demand with current free/manual upgrade flow first.

---

## 📋 Testing Checklist

```bash
# 1. Test blog generation
# - Enter topic: "How to use AI for social media"
# - Select target audience: Small business owners
# - Generate blog post
# - Verify: 1500+ words, 5+ H2 headings, readability 60+

# 2. Test SEO features
# - Check meta title (60 chars)
# - Check meta description (160 chars)
# - Check keyword density (2-3%)

# 3. Test export formats
# - Download Markdown
# - Download HTML (verify CSS styling)
# - Download WordPress format (verify meta comments)

# 4. Test copy variations
# - Generate campaign
# - Enable copy variations
# - Verify 5 different angles generated
# - Check each variation is unique

# 5. Test copy quality checks
# - Generate copy with repetitive words
# - Verify repetition detector catches it
# - Check tone consistency for different tones

# 6. Test copy formulas
# - Apply PAS formula
# - Apply AIDA formula
# - Verify structure matches formula
```

---

## 🎯 Business Impact

**Blog & SEO Generator:**
- Enable content marketing channel
- Drive organic traffic (+30% in 6 months)
- Establish thought leadership
- Support SEO strategy

**Copy Variations:**
- Improve conversion rates (+15-20%)
- Enable A/B testing
- Users learn what resonates
- Higher engagement

**Expected Revenue Impact:**
- More features = higher perceived value
- Differentiation from competitors
- Blog feature requested by 40% of beta users
- Supports higher pricing tiers

---

## 📈 Next Steps (Week 8)

After Week 7 completion:

**Week 8 Options:**
1. **Polish & Beta Launch** (from original plan)
   - End-to-end testing
   - Bug fixes
   - Documentation
   - Beta launch materials

2. **Stripe Integration** (monetization priority)
   - Payment processing
   - Subscription management
   - Invoicing

3. **Analytics Dashboard** (if not yet implemented)
   - Campaign performance tracking
   - "Why it worked" explanations

**Decision:** Review with user after Week 7 completion.

---

**Week 7 Status:** Ready to start! 🚀
**Estimated Completion:** 2.5 working days (8h/day)
