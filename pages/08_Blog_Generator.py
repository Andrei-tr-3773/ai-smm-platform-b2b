"""
Blog Generator Tool - AI-powered blog post creation with SEO optimization.

Week 7 MVP: Basic blog generation with simple meta tags.
Advanced SEO features deferred to Week 8+.
"""

import streamlit as st
from agents.blog_generator_agent import BlogGeneratorAgent
from utils.openai_utils import get_openai_model
from utils.auth import get_current_user
from repositories.workspace_repository import WorkspaceRepository
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Blog Generator", page_icon="📝", layout="wide")

st.title("📝 AI Blog Generator")

st.markdown("""
Generate professional, SEO-friendly blog posts in minutes. Perfect for content marketing,
thought leadership, and driving organic traffic.

**What You Get:**
- 1500-2500 word blog posts
- SEO-optimized meta tags
- Well-structured content with headings
- Export as Markdown or HTML
""")

# MVP Notice
with st.expander("ℹ️ About This Tool (MVP)", expanded=False):
    st.info("""
    **Week 7 MVP Features:**
    ✅ Professional blog post generation
    ✅ Multiple audience and tone options
    ✅ Basic SEO meta tags (title, description)
    ✅ Markdown & HTML export

    **Coming in Week 8+:**
    - Advanced SEO (keyword density, readability scoring)
    - WordPress & Medium export formats
    - Keyword research tools
    - Multi-language blog generation
    """)

st.markdown("---")

# Get current user (optional)
user = get_current_user()

# Input Section
st.header("📋 Blog Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input(
        "Blog Topic / Title",
        placeholder="e.g., How to Use AI for Social Media Marketing in 2024",
        help="Enter the main topic or working title for your blog post"
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options", expanded=True):
        col_adv1, col_adv2, col_adv3 = st.columns(3)

        with col_adv1:
            target_audience = st.selectbox(
                "Target Audience",
                [
                    "General",
                    "Small Business Owners",
                    "Marketing Managers",
                    "Digital Agencies",
                    "E-commerce",
                    "SaaS Companies"
                ],
                index=1,  # Default to Small Business Owners
                help="Who is this blog post for? Influences content style and examples."
            )

        with col_adv2:
            tone = st.selectbox(
                "Writing Tone",
                ["Professional", "Casual", "Educational", "Persuasive"],
                index=0,
                help="The tone and style of writing"
            )

        with col_adv3:
            word_count = st.slider(
                "Target Word Count",
                min_value=1000,
                max_value=2500,
                value=1500,
                step=250,
                help="Approximate target length (actual may vary)"
            )

with col2:
    st.markdown("### 💡 Tips for Best Results")
    st.info("""
    **Topic Examples:**
    - How to [achieve goal]
    - The Ultimate Guide to [topic]
    - 7 Ways to [solve problem]
    - [Topic] for Beginners
    - Why [statement] in 2024

    **Best Practices:**
    - Be specific with your topic
    - Include target keywords naturally
    - Choose audience carefully
    - Longer posts rank better (1500+ words)
    """)

# Generate Button
st.markdown("---")

generate_clicked = st.button(
    "✨ Generate Blog Post",
    type="primary",
    use_container_width=True,
    disabled=not topic
)

if generate_clicked and topic:
    with st.spinner(f"Generating {word_count}-word blog post... This may take 60-90 seconds"):
        try:
            # Initialize agent
            model = get_openai_model()
            agent = BlogGeneratorAgent(model)

            # Generate blog
            blog_data = agent.generate_blog(
                topic=topic,
                target_audience=target_audience,
                tone=tone,
                word_count=word_count
            )

            # Store in session state
            st.session_state['blog_data'] = blog_data

            st.success(f"✅ Blog post generated successfully! ({blog_data['word_count']} words)")

        except Exception as e:
            logger.error(f"Error generating blog: {str(e)}")
            st.error(f"❌ Error generating blog: {str(e)}")
            st.info("Please try again or contact support if the issue persists.")

# Display Generated Blog
if 'blog_data' in st.session_state:
    blog_data = st.session_state['blog_data']

    st.markdown("---")
    st.header("📄 Generated Blog Post")

    # Meta Tags Section
    with st.expander("🔍 SEO Meta Tags", expanded=False):
        col_meta1, col_meta2 = st.columns(2)

        with col_meta1:
            st.text_input(
                "Meta Title (60 chars max)",
                value=blog_data['meta_title'],
                disabled=True,
                help="Title that appears in search results"
            )

        with col_meta2:
            chars_used = len(blog_data['meta_title'])
            color = "🟢" if chars_used <= 60 else "🔴"
            st.metric("Title Length", f"{color} {chars_used}/60")

        st.text_area(
            "Meta Description (160 chars max)",
            value=blog_data['meta_description'],
            disabled=True,
            height=80,
            help="Description that appears in search results"
        )

        desc_chars = len(blog_data['meta_description'])
        desc_color = "🟢" if desc_chars <= 160 else "🔴"
        st.metric("Description Length", f"{desc_color} {desc_chars}/160")

        st.info("💡 **Advanced SEO features** (keyword density, readability) coming in Week 8+")

    # Blog Stats
    st.markdown("### 📊 Blog Statistics")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        st.metric("Word Count", blog_data['word_count'])

    with col_stat2:
        st.metric("Tone", blog_data['tone'])

    with col_stat3:
        st.metric("Audience", blog_data['target_audience'])

    with col_stat4:
        estimated_read_time = round(blog_data['word_count'] / 200)  # 200 words/min
        st.metric("Read Time", f"{estimated_read_time} min")

    # Content Display
    st.markdown("---")
    st.markdown("### 📝 Content Preview")

    # Tabs for different views
    preview_tab, markdown_tab, html_tab = st.tabs(["📖 Preview", "📄 Markdown", "🌐 HTML"])

    with preview_tab:
        # Render markdown
        st.markdown(blog_data['content'])

    with markdown_tab:
        st.code(blog_data['content'], language='markdown', line_numbers=True)

    with html_tab:
        # Show HTML preview
        html_content = agent.format_for_export(blog_data, format_type="html")
        st.code(html_content, language='html')

    # Export Section
    st.markdown("---")
    st.header("💾 Export Blog Post")

    col_export1, col_export2, col_export3 = st.columns(3)

    with col_export1:
        # Markdown with frontmatter
        markdown_export = agent.format_for_export(blog_data, format_type="markdown")

        st.download_button(
            "📄 Download Markdown",
            data=markdown_export,
            file_name=f"blog_{blog_data['topic'][:30].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
            help="Markdown format with frontmatter (compatible with most CMS)"
        )

    with col_export2:
        # HTML with styling
        html_export = agent.format_for_export(blog_data, format_type="html")

        st.download_button(
            "🌐 Download HTML",
            data=html_export,
            file_name=f"blog_{blog_data['topic'][:30].replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True,
            help="Standalone HTML file with CSS styling"
        )

    with col_export3:
        st.button(
            "📋 Copy to Clipboard",
            use_container_width=True,
            help="Copy markdown content to clipboard",
            disabled=True  # Placeholder for future implementation
        )

        st.caption("⏳ Coming soon: WordPress & Medium formats")

    # Usage tips
    with st.expander("💡 How to Use Your Blog Post", expanded=False):
        st.markdown("""
        ### Publishing Options:

        **1. Markdown File (.md)**
        - Upload to GitHub Pages, Jekyll, Hugo, or Ghost
        - Edit in any text editor
        - Version control friendly

        **2. HTML File (.html)**
        - Upload directly to your website
        - Works as standalone page
        - Includes responsive CSS

        **3. Manual Copy-Paste**
        - Use Preview tab to copy content
        - Paste into WordPress, Medium, LinkedIn Articles
        - Format will be preserved

        ### SEO Tips:
        - Use the meta title and description in your CMS
        - Add internal links to other blog posts
        - Include relevant images with alt text
        - Promote on social media after publishing
        - Update and republish periodically
        """)

# Usage tracking
if user and generate_clicked and topic:
    try:
        workspace_repo = WorkspaceRepository()
        logger.info(f"Blog post generated by user {user.email}: {topic}")
    except Exception as e:
        logger.warning(f"Could not track usage: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
### 📚 Blog Writing Resources

**Blog Post Structure:**
- Hook in first 100 words (grab attention)
- Clear H2 sections (3-5 main points)
- Examples and data in each section
- Strong conclusion with CTA
- Scannable formatting (bullets, short paragraphs)

**SEO Best Practices:**
- Target one main keyword per post
- Use keyword in title, headings, and naturally in content
- Write for humans first, search engines second
- Aim for 1500+ words for competitive topics
- Add internal and external links

**Content Ideas:**
- How-to guides (evergreen content)
- Industry trends and analysis
- Case studies and success stories
- Problem-solving posts
- Comparison and review posts

**Need help?** Check out our [Content Marketing Guide](/Content_Guide) or contact support@example.com
""")

st.caption("""
💡 **Pro Tip:** Publish consistently (1-2x per week) for best SEO results. Quality > Quantity.
""")
