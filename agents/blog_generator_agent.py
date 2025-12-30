"""
Simple Blog Generator Agent - Generate blog posts with basic SEO.

Week 7 MVP Approach:
- Single-step generation (no complex LangGraph workflow)
- Basic meta tags (title, description)
- Markdown output
- Defers advanced SEO features to Week 8+
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


class BlogGeneratorAgent:
    """Simple blog generator without complex workflow."""

    def __init__(self, model: ChatOpenAI):
        """
        Initialize Blog Generator Agent.

        Args:
            model: ChatOpenAI model instance
        """
        self.model = model

    def generate_blog(
        self,
        topic: str,
        target_audience: str = "General",
        tone: str = "Professional",
        word_count: int = 1500
    ) -> Dict[str, Any]:
        """
        Generate blog post in single step.

        Args:
            topic: Blog topic/title
            target_audience: Target reader (Small Business Owners, Marketing Managers, etc.)
            tone: Writing tone (Professional, Casual, Educational, Persuasive)
            word_count: Target word count (1000-2500)

        Returns:
            Dict with content, meta_title, meta_description, word_count
        """
        logger.info(f"Generating blog post: {topic} ({word_count} words, {tone} tone)")

        # Build prompt
        prompt = self._build_blog_prompt(topic, target_audience, tone, word_count)

        # System message
        system_message = SystemMessage(
            content="""You are an expert B2B content writer specializing in marketing and business topics.
Your blog posts are informative, engaging, and SEO-friendly.
You write in Markdown format with clear structure and compelling narratives."""
        )

        # Generate content
        messages = [system_message, HumanMessage(content=prompt)]

        try:
            response = self.model.invoke(messages)
            content = response.content.strip()

            # Generate meta tags
            meta = self._generate_meta_tags(content, topic)

            # Calculate word count
            actual_word_count = len(content.split())

            logger.info(f"Blog post generated: {actual_word_count} words")

            return {
                "content": content,
                "meta_title": meta["title"],
                "meta_description": meta["description"],
                "word_count": actual_word_count,
                "topic": topic,
                "tone": tone,
                "target_audience": target_audience
            }

        except Exception as e:
            logger.error(f"Error generating blog: {str(e)}")
            raise

    def _build_blog_prompt(
        self,
        topic: str,
        target_audience: str,
        tone: str,
        word_count: int
    ) -> str:
        """
        Build blog generation prompt.

        Args:
            topic: Blog topic
            target_audience: Target audience
            tone: Writing tone
            word_count: Target word count

        Returns:
            Formatted prompt string
        """
        # Tone guidelines
        tone_guidelines = {
            "Professional": "Use professional language, data-driven insights, and industry terminology. Maintain authority and credibility.",
            "Casual": "Use conversational language, contractions, and relatable examples. Make it friendly and approachable.",
            "Educational": "Focus on teaching and explaining. Use clear definitions, step-by-step instructions, and practical examples.",
            "Persuasive": "Use compelling arguments, social proof, and calls-to-action. Focus on benefits and transformation."
        }

        tone_guide = tone_guidelines.get(tone, tone_guidelines["Professional"])

        # Audience-specific guidance
        audience_context = ""
        if target_audience == "Small Business Owners":
            audience_context = "Focus on practical, actionable advice that saves time and money. Use real-world examples from small businesses."
        elif target_audience == "Marketing Managers":
            audience_context = "Focus on strategy, metrics, and ROI. Include industry trends and data-driven insights."
        elif target_audience == "Digital Agencies":
            audience_context = "Focus on scalability, client results, and process optimization. Use technical details and case studies."

        prompt = f"""Write a comprehensive blog post about: **{topic}**

**Target Audience:** {target_audience}
{audience_context}

**Tone:** {tone}
{tone_guide}

**Target Length:** {word_count} words (approximately)

**Structure Requirements:**

1. **Compelling Introduction (150-200 words)**
   - Start with a hook (surprising statistic, question, or bold statement)
   - Clearly state the problem or topic
   - Preview what readers will learn
   - Make it engaging and relevant to {target_audience}

2. **Main Content (3-5 Sections with H2 Headings)**
   - Each section: 250-400 words
   - Use descriptive H2 headings (not generic like "Section 1")
   - Include concrete examples, data, or case studies
   - Add actionable tips or takeaways
   - Use bullet points or numbered lists where appropriate
   - Consider adding H3 subheadings for complex sections

3. **Conclusion with Clear CTA (100-150 words)**
   - Summarize key points
   - Reinforce the main value proposition
   - Include a clear call-to-action (try a tool, download a resource, etc.)
   - End with a thought-provoking question or statement

**Writing Guidelines:**
- Write in Markdown format
- Use **bold** for emphasis on key points
- Include bullet points for lists
- Keep paragraphs short (2-4 sentences)
- Use transition words between sections
- Include at least 2-3 specific examples or data points
- Avoid jargon unless explaining it
- Write for {target_audience} specifically

**SEO Considerations:**
- Use the topic/keywords naturally throughout
- Create engaging, benefit-driven H2 headings
- Front-load important information
- Make it scannable with formatting

Begin writing the blog post now in Markdown format:"""

        return prompt

    def _generate_meta_tags(self, content: str, topic: str) -> Dict[str, str]:
        """
        Generate basic SEO meta tags from content.

        Args:
            content: Generated blog content (Markdown)
            topic: Blog topic

        Returns:
            Dict with title and description
        """
        # Extract first H1 heading as title
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Find first H1 (# heading)
        title = topic  # Default to topic
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Truncate to 60 chars for SEO
        meta_title = title[:60]

        # Extract first paragraph (not heading) as description
        description = ""
        for line in lines:
            # Skip headings and empty lines
            if line.startswith('#') or not line:
                continue
            # Skip markdown formatting
            clean_line = line.replace('**', '').replace('*', '').replace('[', '').replace(']', '')
            if len(clean_line) > 50:  # Must be substantial
                description = clean_line
                break

        # Truncate to 160 chars for SEO
        if len(description) > 160:
            description = description[:157] + "..."

        # Fallback if no description found
        if not description:
            description = f"Learn about {topic}. Read our comprehensive guide."[:160]

        return {
            "title": meta_title,
            "description": description
        }

    def format_for_export(
        self,
        blog_data: Dict[str, Any],
        format_type: str = "markdown"
    ) -> str:
        """
        Format blog post for different export types.

        Args:
            blog_data: Blog data dict from generate_blog()
            format_type: Export format (markdown, html)

        Returns:
            Formatted content string
        """
        content = blog_data["content"]
        meta_title = blog_data["meta_title"]
        meta_description = blog_data["meta_description"]

        if format_type == "markdown":
            # Add frontmatter
            return f"""---
title: {meta_title}
description: {meta_description}
date: {self._get_current_date()}
---

{content}
"""

        elif format_type == "html":
            # Convert markdown to HTML (basic conversion)
            html_content = self._markdown_to_html(content)

            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_title}</title>
    <meta name="description" content="{meta_description}">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 0.5em; color: #1a1a1a; }}
        h2 {{ font-size: 1.8em; margin-top: 1.5em; color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.4em; margin-top: 1.2em; color: #34495e; }}
        p {{ margin: 1em 0; }}
        ul, ol {{ margin: 1em 0; padding-left: 2em; }}
        li {{ margin: 0.5em 0; }}
        strong {{ color: #2c3e50; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 1em; margin: 1.5em 0; color: #555; font-style: italic; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

        else:
            return content

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Simple Markdown to HTML conversion.

        Args:
            markdown_text: Markdown content

        Returns:
            HTML content
        """
        # Simple conversion (basic support)
        # In production, use a proper markdown library like 'markdown' or 'mistune'

        html = markdown_text

        # Headings
        html = html.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')

        # Add closing tags (simple approach)
        lines = html.split('\n')
        converted_lines = []

        for line in lines:
            if line.startswith('<h1>'):
                line = line + '</h1>'
            elif line.startswith('<h2>'):
                line = line + '</h2>'
            elif line.startswith('<h3>'):
                line = line + '</h3>'
            elif line.strip() and not line.startswith('<'):
                # Wrap paragraphs
                line = f'<p>{line}</p>'

            converted_lines.append(line)

        html = '\n'.join(converted_lines)

        # Bold and italic
        html = html.replace('**', '<strong>').replace('**', '</strong>')

        return html

    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
