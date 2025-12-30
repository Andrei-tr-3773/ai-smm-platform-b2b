# Home.py
import os
import json
import logging
import traceback
from pathlib import Path
from dotenv import load_dotenv
from liquid import Template
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from agents.content_generation_agent import ContentGenerationAgent
from agents.translation_agent import TranslationAgent
from agents.evaluation_agent import EvaluationAgent
from agents.platform_optimizer_agent import optimize_for_platform
from agents.viral_content_agent import generate_viral_content_for_query
from agents.agent_state import AgentState
from audience import Audience
from repositories.audience_repository import AudienceRepository
from repositories.campaign_repository import CampaignRepository
from utils.ui_components import init_page_settings, load_css
from utils.llm_queries import predefined_query, DefaultPrompts
from utils.mongodb_utils import MongoDBClient
from campaign import Campaign
from components import CampaignWizard
import streamlit as st
from utils.deepeval_openai import DeepEvalOpenAI
from utils.openai_utils import get_openai_model
from utils.analytics_tracker import get_analytics_tracker
from weasyprint import HTML
from html2docx import html2docx
from pdf2docx import Converter
import pypandoc
import ssl
import io

# Monitoring and compliance
from utils.monitoring import track_execution_time, track_metric
from utils.api_cost_tracker import get_tracker
from utils.compliance import show_first_time_disclaimer, show_content_disclaimer

# Week 6: Authentication
from utils.auth import get_current_user, clear_session
from repositories.workspace_repository import WorkspaceRepository

ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

# Set Streamlit page configuration
init_page_settings()
load_css("./static/ui/css/styles.css")

def apply_template(content_dict, html_template):
    try:
        template = Template(html_template)
        return {lang: template.render(**content) for lang, content in content_dict.items()}
    except Exception as e:
        logging.error(f"Error applying template: {e}")
        return {}

def generate_content(user_query, template_name, state, prompts, add_context, selected_audience_name, selected_audience_description, selected_platform=None):
    try:
        model = get_openai_model()
        mongodb_client = MongoDBClient("content_templates")
        content_template = mongodb_client.get_template_by_name(template_name)

        if not content_template:
            logging.warning(f"Template '{template_name}' not found.")
            return f"Template '{template_name}' not found.", state

        repository = CampaignRepository("campaigns", "campaign_embedding_collection")
        content_agent = ContentGenerationAgent(model, repository, prompts['system_prompt'], add_context=add_context)
        user_query_template = ChatPromptTemplate.from_template(
            "{user_query}\nTemplate: ```{html_template}```\nTemplate items: ```{template_items}```"
        )

        formatted_user_query = user_query_template.format(
            html_template=content_template['liquid_template'],
            template_items=json.dumps(content_template['items']),
            user_query=user_query
        )

        state['messages'].append(HumanMessage(content=formatted_user_query))
        agent_state = AgentState(
            messages=state['messages'],
            content_template=content_template,
            selected_audience_name=selected_audience_name,
            selected_audience_description=selected_audience_description,
            selected_platform=selected_platform
        )

        interim_state = content_agent.graph.invoke(agent_state)
        state.update(interim_state)

        # Log generated JSON content
        generated_json = json.loads(interim_state['initial_english_content'])
        logging.info(f"Generated JSON content: {json.dumps(generated_json, indent=2)}")

        content_dict = {'en-US': generated_json}
        translated_htmls = apply_template(content_dict, content_template['liquid_template'])

        english_html = translated_htmls['en-US']
        logging.info(f"english_html: {english_html}")

        # Week 4: Platform optimization (if platform selected)
        if selected_platform:
            logging.info(f"Optimizing content for platform: {selected_platform}")
            try:
                # Extract text content from HTML for optimization
                import re
                text_content = re.sub('<[^<]+?>', '', english_html)  # Strip HTML tags

                optimization_result = optimize_for_platform(
                    content=text_content,
                    platform=selected_platform,
                    content_type="feed_post"
                )

                # Store optimization results in state
                state['optimized_content'] = optimization_result['optimized_content']
                state['posting_guide'] = optimization_result['posting_guide']

                # Add posting guide to output
                formatted_html = f"<h3>Generated Content (en-US)</h3>\n{english_html}"
                formatted_html += f"\n\n<div style='background-color: #f0f0f0; padding: 15px; margin-top: 20px; border-left: 4px solid #4CAF50;'>"
                formatted_html += f"<h4>📱 {selected_platform.title()} Optimization</h4>"
                formatted_html += f"<pre style='white-space: pre-wrap;'>{optimization_result['posting_guide']}</pre>"
                formatted_html += "</div>"

                logging.info(f"Platform optimization complete for {selected_platform}")
            except Exception as e:
                logging.error(f"Platform optimization error: {e}")
                formatted_html = f"<h3>Generated Content (en-US)</h3>\n{english_html}"
                formatted_html += f"\n<p style='color: orange;'>⚠️ Platform optimization failed: {str(e)}</p>"
        else:
            # Return HTML with language header (no optimization)
            formatted_html = f"<h3>Generated Content (en-US)</h3>\n{english_html}"

        return formatted_html, state
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return "An error occurred during content generation.", state

def translate_content(state, selected_languages, prompts):
    try:
        model = get_openai_model()
        translation_agent = TranslationAgent(
            model=model,
            translate_prompt=prompts['translate_prompt'],
            criticize_prompt=prompts['criticize_prompt'],
            reflection_prompt=prompts['reflection_prompt']
        )

        state['selected_languages'] = selected_languages
        final_state = translation_agent.graph.invoke(state)
        state.update(final_state)

        translations = {lang: final_state['translations'][lang] for lang in selected_languages}
        content_dict = {'en-US': json.loads(final_state['initial_english_content']), **translations}
        translated_htmls = apply_template(content_dict, state['content_template']['liquid_template'])

        collapsible_html = "".join(f"<details><summary>{lang}</summary>{html}</details>\n" for lang, html in translated_htmls.items())
        return collapsible_html, state
    except Exception as e:
        logging.error(f"Error translating content: {e}")
        return "An error occurred during translation.", state

def evaluate_translations(state, eval_model, selected_metrics):
    try:
        evaluation_agent = EvaluationAgent(eval_model=eval_model)
        eval_state = evaluation_agent.evaluate_translation(AgentState(**state), selected_metrics)
        state['evaluation'] = eval_state['evaluation']
        return state
    except Exception as e:
        logging.error(f"Error evaluating translations: {e}")
        return state

def update_query():
    try:
        template_name = st.session_state.template_name
        mongodb_client = MongoDBClient("content_templates")
        content_template = mongodb_client.get_template_by_name(template_name)
        st.session_state.user_query = content_template['example_query']
    except Exception as e:
        logging.error(f"Error updating query: {e}")

def display_evaluation_results(evaluation_results):
    try:
        if isinstance(evaluation_results, str):
            return f"<p>{evaluation_results}</p>"

        evaluation_html = "<h3>Evaluation Results</h3>"
        for lang, metrics in evaluation_results.items():
            total_score = sum(metric['score'] for metric in metrics) / len(metrics)
            score_color = "green" if total_score >= 0.9 else "green" if total_score >= 0.7 else "red"
            
            evaluation_html += f"<details><summary>{lang} - Total Score: <span style='color: {score_color};'>{total_score:.2f}</span></summary>"
            
            for metric in metrics:
                metric_score_color = "green" if metric['score'] >= 0.9 else "green" if metric['score'] >= 0.7 else "red"
                evaluation_html += f"""
                    <p><strong>{metric['name']}:</strong> 
                    <span style="color: {metric_score_color};">Score: {metric['score']}</span>, 
                    Reason: {metric['reason']}</p>"""
            
            if total_score < 0.9:
                evaluation_html += "<button>Send for review</button>"
            
            evaluation_html += "</details>"
        
        return evaluation_html
    except Exception as e:
        logging.error(f"Error displaying evaluation results: {e}")
        return "<p>An error occurred while displaying evaluation results.</p>"

@st.dialog("Save Campaign")
def save_campaign_dialog(state):
    try:
        campaign_name = st.text_input("Enter Campaign Name")
        if st.button("Save"):
            if campaign_name:
                localized_content = {'en-US': json.loads(state['initial_english_content']), **state['translations']}
                campaign = Campaign(name=campaign_name, localized_content=localized_content, liquid_template=state['content_template']['liquid_template'])
                repository = CampaignRepository("campaigns", "campaign_embedding_collection")
                repository.save_campaign(campaign)
                st.success(f"Campaign '{campaign_name}' saved successfully!")
            else:
                st.error("Campaign name cannot be empty.")
    except Exception as e:
        logging.error(f"Error saving campaign: {e}")
        logging.error(f"Traceback object: {e.__traceback__}")  # Это объект трассировки
        # Получаем трассировку с помощью traceback
        trace = traceback.format_exception(type(e), e, e.__traceback__)

        # Логируем трассировку
        logging.error(f"Traceback details: {''.join(trace)}")
        st.error("An error occurred while saving the campaign.")


# Функция для сохранения HTML в PDF и DOCX
def generate_pdf(html_content):
    pdf = HTML(string=html_content).write_pdf()
    return io.BytesIO(pdf)


def generate_docx(html_content):
    # Конвертируем HTML в PDF в памяти
    pdf_io = generate_pdf(html_content)

    # Конвертируем PDF в DOCX
    docx_io = io.BytesIO()
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(pdf_io.getvalue())

    cv = Converter("temp.pdf")
    cv.convert(docx_io, start=0, end=None)
    cv.close()

    return docx_io

@st.cache_resource(ttl=10)  # Cache for 10 seconds
def get_cached_tracker():
    """Get cached API usage tracker to avoid file I/O on every rerun"""
    return get_tracker()

def main():
    # Show disclaimer on first load
    if 'disclaimer_shown' not in st.session_state:
        show_first_time_disclaimer()
        if st.button("I Understand", key="accept_disclaimer"):
            st.session_state.disclaimer_shown = True
            st.rerun()
        st.stop()

    st.title("AI SMM Platform for B2B")

    # Sidebar with API usage tracking
    with st.sidebar:
        # Week 6: User session management
        user = get_current_user()

        # Week 6: Initialize workspace repo for usage tracking
        if user:
            workspace_repo = WorkspaceRepository()

        if user:
            st.markdown("### 👤 Account")
            st.markdown(f"**{user.name}**")
            st.caption(f"📧 {user.email}")

            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                clear_session()
                st.success("✅ Logged out successfully")
                st.rerun()

            # Week 6: Usage tracking for logged-in users
            workspace = workspace_repo.get_workspace(user.workspace_id)
            limits = workspace.get_plan_limits()

            st.markdown(f"**Plan:** {workspace.plan_tier.title()}")

            # Campaigns usage
            if limits["campaigns"] == -1:
                st.success(f"✅ {workspace.campaigns_this_month} campaigns (Unlimited)")
            else:
                remaining = limits["campaigns"] - workspace.campaigns_this_month
                st.metric("Campaigns Remaining", remaining)

                progress = workspace.campaigns_this_month / limits["campaigns"]
                st.progress(min(progress, 1.0))

                if remaining <= 0:
                    st.error("⚠️ Limit reached!")
                    if st.button("💎 Upgrade", type="primary", use_container_width=True, key="sidebar_upgrade"):
                        st.switch_page("pages/06_Pricing.py")
                elif remaining <= 2:
                    st.warning(f"⚠️ Only {remaining} left")

            # Link to workspace settings
            if st.button("⚙️ Workspace Settings", use_container_width=True, key="workspace_settings_btn"):
                st.switch_page("pages/05_Workspace_Settings.py")

            st.markdown("---")
        else:
            st.markdown("### 👋 Welcome")
            st.info("Sign up to track your usage and unlock premium features!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔐 Login", use_container_width=True):
                    st.switch_page("pages/02_Login.py")
            with col2:
                if st.button("📝 Sign Up", use_container_width=True):
                    st.switch_page("pages/03_Signup.py")

            st.markdown("---")

        st.markdown("### 📊 API Usage")
        tracker = get_cached_tracker()
        summary = tracker.get_summary()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cost", f"${summary['total_cost']:.2f}")
        with col2:
            st.metric("This Month", f"${summary['current_month_cost']:.2f}")

        st.metric("Total Tokens", f"{summary['total_tokens']:,}")

        if summary['total_cost'] > 80:
            st.warning("⚠️ Approaching budget limit!")

        # Examples section
        with st.expander("💡 Examples", expanded=False):
            st.markdown("**🏋️ Fitness:**")
            st.markdown("- Launch 30-day transformation challenge")
            st.markdown("- Announce new HIIT class")
            st.markdown("- Promote personal training packages")

            st.markdown("**💼 SaaS:**")
            st.markdown("- Announce new AI feature")
            st.markdown("- Share customer success story")
            st.markdown("- Launch product update")

            st.markdown("**🛍️ E-commerce:**")
            st.markdown("- Black Friday sale")
            st.markdown("- New product collection")
            st.markdown("- Limited-time discount")

            st.markdown("**📚 Education:**")
            st.markdown("- New course launch")
            st.markdown("- Student testimonials")
            st.markdown("- Webinar announcement")

        with st.expander("📋 Content Guidelines", expanded=False):
            show_content_disclaimer()

        # Wizard toggle
        st.markdown("---")

        # Use checkbox with on_change callback instead of manual check
        def toggle_wizard():
            st.session_state.wizard_active = st.session_state.wizard_toggle

        st.checkbox(
            "🧙‍♂️ Use Setup Wizard",
            value=st.session_state.get('wizard_active', False),
            key='wizard_toggle',
            on_change=toggle_wizard,
            help="Step-by-step guide for creating your first campaign (recommended for new users)"
        )

    # Define top-level tabs
    main_tabs = st.tabs(["Create New", "Campaigns", "Audiences", "Prompts"])

    with ((main_tabs[0])):  # "Create New" tab
        try:
            mongodb_client = MongoDBClient("content_templates")
            templates = mongodb_client.get_templates()
            template_names = [template['name'] for template in templates]
            default_template = template_names[0] if template_names else ""
            # "Game Features Promotion"
            default_query = templates[0]['example_query'] if templates else""
            # "Promote our new game releases with a 50% discount. Highlight the immersive worlds, global community, seamless gameplay, and team challenges. Include a call to action to shop now."
            languages = os.getenv("LANGUAGES").split(',')
            default_languages = os.getenv("DEFAULT_LANGUAGES").split(',')

            default_prompts = {
                'system_prompt': DefaultPrompts.system_prompt,
                'translate_prompt': DefaultPrompts.translate_prompt,
                'criticize_prompt': DefaultPrompts.criticize_prompt,
                'reflection_prompt': DefaultPrompts.reflection_prompt
            }

            state = st.session_state.get('state', {'messages': [], 'evaluation': {}, 'translations': {}, 'initial_english_content': '', 'selected_languages': [], 'content_template': None, 'criticisms': '', 'selected_audience_name': '', 'selected_audience_description': ''})
            prompts = st.session_state.get('prompts', default_prompts)
            history = st.session_state.get('history', [])
            campaigns = st.session_state.get('campaigns', [])
            campaigns_client = MongoDBClient("campaigns")

            # Audience repository and fetching audiences
            audience_repository = AudienceRepository("audiences")
            audiences = audience_repository.get_audiences()
            audience_names = [audience.name for audience in audiences]

            # Week 6: Workspace repository for usage tracking
            workspace_repo = WorkspaceRepository()

            if not campaigns:
                campaigns = campaigns_client.get_campaigns()
                st.session_state['campaigns'] = campaigns

            # Check for demo data loaded from Getting Started page
            if st.session_state.get('demo_loaded', False):
                st.session_state['user_query'] = st.session_state.get('demo_query', default_query)
                st.session_state['template_name'] = st.session_state.get('demo_template', default_template)

                # Set platform if specified
                demo_platform = st.session_state.get('demo_platform', 'None')
                st.session_state['selected_platform'] = demo_platform.lower() if demo_platform != 'None' else 'None'

                # Enable viral patterns by default for demos
                st.session_state['use_viral_patterns'] = True
                st.session_state['viral_industry'] = st.session_state.get('demo_industry', 'saas')
                st.session_state['viral_account_type'] = 'brand_static_only'
                st.session_state['viral_content_type'] = 'static'
                st.session_state['viral_follower_count'] = 5000

                # Clear demo flag and show success message
                st.session_state['demo_loaded'] = False
                st.success("✅ Demo campaign loaded! Review settings below and click 'Generate' to create content.")

            # Check if wizard is active
            if st.session_state.get('wizard_active', False):
                # Show wizard instead of regular form
                wizard = CampaignWizard(audiences, template_names)
                wizard.run()
                # Stop here - don't show the regular form
                return

            col1, col2 = st.columns([1, 2])

            with col1:
                tabs = st.tabs(["Generate", "Translate"])

                with tabs[0]:
                    st.markdown("### Generate Content")
                    user_query = st.text_area(
                        "Enter your query here...",
                        default_query,
                        key='user_query',
                        help="💡 Describe what you want to promote. Be specific about details, benefits, and call-to-action!"
                    )

                    if not template_names:
                        st.error("No content templates found. Please load templates into MongoDB.")
                        template_name = None
                    else:
                        # Initialize recently used templates
                        if 'recent_templates' not in st.session_state:
                            st.session_state.recent_templates = []

                        # Show recently used templates
                        if st.session_state.recent_templates:
                            with st.expander("⏱️ Recently Used Templates", expanded=False):
                                for recent_tmpl in st.session_state.recent_templates[:5]:
                                    if st.button(f"📄 {recent_tmpl}", key=f"recent_{recent_tmpl}", use_container_width=True):
                                        st.session_state.template_name = recent_tmpl
                                        st.rerun()

                        default_index = template_names.index(default_template) if default_template in template_names else 0
                        template_name = st.selectbox(
                            "Select Content Template",
                            template_names,
                            index=default_index,
                            key='template_name',
                            on_change=update_query,
                            help="📝 Choose template based on your campaign type (sale, product launch, event, etc.)"
                        )

                        # Track template usage (add to recent if not already at top)
                        if template_name and (not st.session_state.recent_templates or st.session_state.recent_templates[0] != template_name):
                            # Remove if exists elsewhere in list
                            if template_name in st.session_state.recent_templates:
                                st.session_state.recent_templates.remove(template_name)
                            # Add to front
                            st.session_state.recent_templates.insert(0, template_name)
                            # Keep only last 5
                            st.session_state.recent_templates = st.session_state.recent_templates[:5]

                    # Move audience selection here
                    selected_audience_name = st.selectbox(
                        "Select Audience",
                        audience_names,
                        key='selected_audience_name',
                        help="👥 Target specific audience for better content personalization"
                    )
                    selected_audience_description = ""
                    if selected_audience_name:
                        selected_audience = next((audience for audience in audiences if audience.name == selected_audience_name), None)
                        if selected_audience:
                            selected_audience_description = selected_audience.description
                            st.session_state['selected_audience_description'] = selected_audience_description

                    # Week 4: Platform selection for optimization
                    platform_options = {
                        "instagram": "📷 Instagram",
                        "facebook": "📘 Facebook",
                        "telegram": "✈️ Telegram",
                        "linkedin": "💼 LinkedIn"
                    }
                    st.selectbox(
                        "Target Platform (Optional - for optimization)",
                        options=["None"] + list(platform_options.keys()),
                        format_func=lambda x: "No optimization" if x == "None" else platform_options.get(x, x),
                        key='selected_platform',
                        help="📱 Choose platform for optimized content (hashtags, formatting, timing recommendations)"
                    )

                    # Week 4: Viral content generation option
                    use_viral_patterns = st.checkbox(
                        "🔥 Use Viral Patterns",
                        value=False,
                        key='use_viral_patterns',
                        help="🚀 Generate viral content using proven patterns (2-3x more engagement). Powered by real data from 100+ successful campaigns!"
                    )

                    if use_viral_patterns:
                        with st.expander("Viral Pattern Settings", expanded=True):
                            # Industry selection
                            industry_options = ["fitness", "saas", "ecommerce", "education", "consulting", "all"]
                            st.selectbox(
                                "Industry",
                                options=industry_options,
                                index=1,  # Default to 'saas'
                                key='viral_industry',
                                help="🏢 Your business industry - patterns are optimized per industry"
                            )

                            # Account type
                            account_type_options = {
                                "creator": "👤 Creator/Influencer",
                                "brand_with_video": "🎥 Brand (with video)",
                                "brand_static_only": "📄 Brand (static only)"
                            }
                            st.selectbox(
                                "Account Type",
                                options=list(account_type_options.keys()),
                                format_func=lambda x: account_type_options[x],
                                index=2,  # Default to 'brand_static_only'
                                key='viral_account_type',
                                help="👤 Your account type affects which patterns work best"
                            )

                            # Content type
                            content_type_options = ["video", "static", "carousel"]
                            st.selectbox(
                                "Content Type",
                                options=content_type_options,
                                index=1,  # Default to 'static'
                                key='viral_content_type',
                                help="📸 Type of content you'll create (video performs best, but requires production)"
                            )

                            # Follower count
                            st.number_input(
                                "Follower Count",
                                min_value=0,
                                max_value=1000000,
                                value=5000,
                                step=1000,
                                key='viral_follower_count',
                                help="👥 Your current follower count - affects pattern selection and expected results"
                            )

                    add_context = st.checkbox(
                        "Add Context",
                        value=True,
                        key='add_context',
                        help="🔍 Use RAG to find similar campaigns and improve content quality"
                    )
                    col1_1, col1_2 = st.columns(2)
                    generate_button = col1_1.button("Generate", use_container_width=True)
                    show_template_button = col1_2.button("Show Template", use_container_width=True)

                with tabs[1]:
                    st.markdown("### Translate Content")
                    selected_languages = st.multiselect(
                        "Select Languages",
                        languages,
                        default=default_languages,
                        help="🌍 Choose target languages for translation (15+ languages supported). Uses AI with cultural adaptation!"
                    )
                    selected_metrics = st.multiselect(
                        "Select Evaluation Metrics",
                        list(EvaluationAgent.all_metrics.keys()),
                        default=EvaluationAgent.default_metrics,
                        help="📊 Choose quality metrics to evaluate translations (accuracy, fluency, cultural appropriateness, etc.)"
                    )
                    col1_3, col1_4 = st.columns(2)
                    translate_button = col1_3.button("Translate", use_container_width=True)
                    evaluate_button = col1_4.button("Evaluate", use_container_width=True)

                st.markdown("---")

                col1_5, col1_6 = st.columns(2)
                save_button = col1_5.button("Save Campaign", use_container_width=True)
                clear_button = col1_6.button("Clear", use_container_width=True)

            with col2:
                st.subheader("Chat History")
                spinner_placeholder = st.empty()
                chat_placeholder = st.container()

            if generate_button:
                # Week 6: Check campaign limits before generation
                if user:
                    workspace = workspace_repo.get_workspace(user.workspace_id)

                    if not workspace.can_create_campaign():
                        limits = workspace.get_plan_limits()

                        st.error("❌ Monthly campaign limit reached!")

                        if workspace.plan_tier == "free":
                            st.info("💎 Upgrade to Starter plan for 50 campaigns/month ($49/mo) or Professional for 200 campaigns/month ($99/mo).")
                        elif workspace.plan_tier == "starter":
                            st.info("💎 Upgrade to Professional plan for 200 campaigns/month ($99/mo).")
                        elif workspace.plan_tier == "professional":
                            st.info("💎 Upgrade to Team plan for unlimited campaigns ($199/mo).")

                        col1_upgrade, col2_upgrade = st.columns(2)
                        with col1_upgrade:
                            if st.button("📊 View Usage", type="secondary", use_container_width=True, key="view_usage_limit"):
                                st.switch_page("pages/05_Workspace_Settings.py")
                        with col2_upgrade:
                            if st.button("💎 View Plans", type="primary", use_container_width=True, key="upgrade_limit"):
                                st.switch_page("pages/06_Pricing.py")

                        st.stop()

                handle_generate(user_query, template_name, state, prompts, history, spinner_placeholder, add_context)

                # Week 6: Increment campaign count after successful generation
                if user:
                    workspace_repo.increment_campaign_count(user.workspace_id)

            if translate_button:
                handle_translate(state, selected_languages, prompts, history, spinner_placeholder)

            if clear_button:
                handle_clear(default_prompts)

            if evaluate_button:
                handle_evaluate(state, selected_metrics, history, spinner_placeholder)

            if save_button:
                save_campaign_dialog(state)

            if show_template_button:
                handle_show_template(template_name, mongodb_client, history)

            with chat_placeholder:
                for query, response in history:
                    with st.chat_message("user"):
                        st.markdown(query)
                    with st.chat_message("assistant"):
                        # Use st.html for proper HTML rendering
                        # st.html is better than st.markdown for complex HTML
                        try:
                            st.html(response)
                        except AttributeError:
                            # Fallback for older Streamlit versions
                            st.markdown(response, unsafe_allow_html=True)

        except Exception as e:
            logging.error(f"Error in 'Create New' tab: {e}")
            logging.error(f"Traceback object: {e.__traceback__}")  # Это объект трассировки
            # Получаем трассировку с помощью traceback
            trace = traceback.format_exception(type(e), e, e.__traceback__)

            # Логируем трассировку
            logging.error(f"Traceback details: {''.join(trace)}")
            st.error("An error occurred in the 'Create New' tab.")

    with main_tabs[1]:  # "Campaigns" tab
        try:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Saved Campaigns")
                campaign_names = [campaign.name for campaign in campaigns]
                selected_campaign_name = st.selectbox("Select Campaign", campaign_names)
                col1_7, col1_8 = st.columns(2)
                refresh_button = col1_7.button("Refresh", use_container_width=True)
                show_campaign_button = col1_8.button("Show Campaign", use_container_width=True)

            with col2:
                if show_campaign_button:
                    selected_campaign = next(
                        campaign for campaign in campaigns if campaign.name == selected_campaign_name)
                    content_dict = selected_campaign.localized_content
                    translated_htmls = apply_template(content_dict, selected_campaign.liquid_template)

                    st.markdown(f"### Campaign: {selected_campaign_name}")

                    for lang, html in translated_htmls.items():
                        with st.expander(f"Language: {lang}"):
                            st.components.v1.html(html, height=600, scrolling=True)

                            pdf_io = generate_pdf(html)
                            docx_io = generate_docx(html)

                            st.download_button(
                                label=f"Download {lang} as PDF",
                                data=pdf_io,
                                file_name=f"{selected_campaign_name}_{lang}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{selected_campaign_name}_{lang}"
                            )

                            st.download_button(
                                label=f"Download {lang} as DOCX",
                                data=docx_io,
                                file_name=f"{selected_campaign_name}_{lang}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"docx_{selected_campaign_name}_{lang}"
                            )

            if refresh_button:
                handle_refresh(campaigns_client, spinner_placeholder)

        except Exception as e:
            logging.error(f"Error in 'Campaigns' tab: {e}")
            st.error("An error occurred in the 'Campaigns' tab.")

    with main_tabs[2]:  # "Audiences" tab
        try:
            col1, col2 = st.columns([1, 2])
        
            with col1:
                # Create sub-tabs for "View Audiences" and "Create Audience"
                audience_tabs = st.tabs(["View Audiences", "Create Audience"])
        
                with audience_tabs[0]:  # "View Audiences" sub-tab
                    st.subheader("Manage Audiences")
                    audience_repository = AudienceRepository("audiences")
                    audiences = audience_repository.get_audiences()
                    audience_names = [audience.name for audience in audiences]
                    selected_audience_name = st.selectbox("Select Audience", audience_names)
                    col1_1, col1_2 = st.columns(2)
                    refresh_audiences_button = col1_1.button("Refresh Audiences", use_container_width=True)
                    show_audience_button = col1_2.button("Show Audience", use_container_width=True)
        
                with audience_tabs[1]:  # "Create Audience" sub-tab
                    st.markdown("### Create New Audience")
                    audience_name = st.text_input("Audience Name")
                    audience_description = st.text_area("Audience Description")
                    create_audience_button = st.button("Create Audience", use_container_width=True)
        
            with col2:
                if show_audience_button:
                    selected_audience = next(audience for audience in audiences if audience.name == selected_audience_name)
                    st.markdown(f"### Audience: {selected_audience_name}")
                    st.markdown(f"**Description:** {selected_audience.description}")
        
            if refresh_audiences_button:
                handle_refresh_audiences(audience_repository)
        
            if create_audience_button:
                handle_create_audience(audience_name, audience_description, audience_repository)

        except Exception as e:
            logging.error(f"Error in 'Audiences' tab: {e}")
            st.error("An error occurred in the 'Audiences' tab.")

    with main_tabs[3]:  # "Prompts" tab
        try:
            st.markdown("### Prompts")
            system_prompt = st.text_area("System Prompt", prompts['system_prompt'], key='system_prompt')
            translate_prompt = st.text_area("Translate Prompt", prompts['translate_prompt'], key='translate_prompt')
            criticize_prompt = st.text_area("Criticize Prompt", prompts['criticize_prompt'], key='criticize_prompt')
            reflection_prompt = st.text_area("Reflection Prompt", prompts['reflection_prompt'], key='reflection_prompt')
            update_prompts_button = st.button("Update Prompts", use_container_width=True)

            if update_prompts_button:
                handle_update_prompts(system_prompt, translate_prompt, criticize_prompt, reflection_prompt)

        except Exception as e:
            logging.error(f"Error in 'Prompts' tab: {e}")
            st.error("An error occurred in the 'Prompts' tab.")

def handle_generate(user_query, template_name, state, prompts, history, spinner_placeholder, add_context):
    try:
        # Retrieve the selected audience name and description from the session state
        selected_audience_name = st.session_state.get('selected_audience_name', '')
        selected_audience_description = st.session_state.get('selected_audience_description', '')
        # Week 4: Retrieve selected platform (convert "None" to None)
        selected_platform = st.session_state.get('selected_platform', 'None')
        if selected_platform == 'None':
            selected_platform = None
        # Week 4: Check if viral patterns are enabled
        use_viral_patterns = st.session_state.get('use_viral_patterns', False)

        # Add the original user query (without audience context) to the chat history
        history.append([user_query, "Generating content..."])
        st.session_state['history'] = history

        with spinner_placeholder:
            with st.spinner("Generating..."):
                # Week 4: If viral patterns are enabled, use viral content agent
                if use_viral_patterns:
                    platform = selected_platform if selected_platform else "instagram"

                    viral_result = generate_viral_content_for_query(
                        user_query=user_query,
                        platform=platform,
                        industry=st.session_state.get('viral_industry', 'saas'),
                        follower_count=st.session_state.get('viral_follower_count', 5000),
                        account_type=st.session_state.get('viral_account_type', 'brand_static_only'),
                        content_type=st.session_state.get('viral_content_type', 'static')
                    )

                    # Format viral content output
                    result = viral_result.get('final_content', 'Error generating viral content')

                    # Store viral content in state for potential translation
                    viral_content_json = {
                        "hook": viral_result.get('hook', ''),
                        "body": viral_result.get('body', ''),
                        "cta": viral_result.get('cta', ''),
                        "pattern": viral_result.get('pattern_name', '')
                    }
                    state['initial_english_content'] = json.dumps(viral_content_json)
                    new_state = state

                else:
                    # Original content generation workflow
                    result, new_state = generate_content(
                        user_query,
                        template_name,
                        state,
                        prompts,
                        add_context,
                        selected_audience_name,
                        selected_audience_description,
                        selected_platform  # Week 4: Platform optimization
                    )

        # Update the chat history with the generated content
        history[-1][1] = result
        st.session_state.update({'state': new_state, 'history': history})
        st.success("✅ Content generated successfully! Review it below or translate to other languages.")

        # Track campaign generation event (Week 8: Analytics)
        try:
            from utils.auth import get_current_user
            user = get_current_user()
            if user:
                analytics = get_analytics_tracker()
                analytics.track_campaign_generated(
                    user_id=str(user.id),
                    workspace_id=user.workspace_id,
                    platform=selected_platform or "instagram",
                    languages=["en-US"],  # Initial generation is English
                    template_id=template_name
                )
        except Exception as track_error:
            logging.error(f"Failed to track campaign generation: {track_error}")

    except Exception as e:
        logging.error(f"Error handling generate: {e}")
        logging.error(traceback.format_exc())
        st.error("An error occurred during content generation.")

def handle_translate(state, selected_languages, prompts, history, spinner_placeholder):
    try:
        if not state['initial_english_content']:
            st.error("Please generate content before translating.")
            return

        history.append(["Translating content...", "Loading..."])
        st.session_state['history'] = history
        with spinner_placeholder:
            with st.spinner("Translating..."):
                result, new_state = translate_content(state, selected_languages, prompts)
        history[-1][1] = result
        st.session_state.update({'state': new_state, 'history': history})
        st.success(f"✅ Content translated to {len(selected_languages)} language(s) successfully! Click 'Evaluate' to check translation quality.")
    except Exception as e:
        logging.error(f"Error handling translate: {e}")
        st.error("An error occurred during translation.")

def handle_clear(default_prompts):
    try:
        st.session_state.update({'state': {'messages': [], 'evaluation': {}, 'translations': {}, 'initial_english_content': '', 'selected_languages': [], 'content_template': None, 'criticisms': ''}, 'history': [], 'prompts': default_prompts})
        st.success("✅ Session cleared! Start with a new campaign.")
        st.rerun()
    except Exception as e:
        logging.error(f"Error handling clear: {e}")
        st.error("An error occurred while clearing the session.")

def handle_evaluate(state, selected_metrics, history, spinner_placeholder):
    try:
        eval_model = DeepEvalOpenAI(model=get_openai_model())
        with spinner_placeholder:
            with st.spinner("Evaluating..."):
                new_state = evaluate_translations(state, eval_model, selected_metrics)
        evaluation_results = new_state['evaluation']
        history.append(["Translation Evaluation Results:", display_evaluation_results(evaluation_results)])
        st.session_state.update({'state': new_state, 'history': history})
        st.success("✅ Translation evaluation complete! Check results below.")
    except Exception as e:
        logging.error(f"Error handling evaluate: {e}")
        st.error("An error occurred during evaluation.")

def handle_update_prompts(system_prompt, translate_prompt, criticize_prompt, reflection_prompt):
    try:
        st.session_state['prompts'] = {
            'system_prompt': system_prompt,
            'translate_prompt': translate_prompt,
            'criticize_prompt': criticize_prompt,
            'reflection_prompt': reflection_prompt
        }
        st.success("Prompts updated successfully!")
    except Exception as e:
        logging.error(f"Error updating prompts: {e}")
        st.error("An error occurred while updating prompts.")

def handle_refresh(campaigns_client, spinner_placeholder):
    try:
        with spinner_placeholder:
            with st.spinner("Refreshing..."):
                campaigns = campaigns_client.get_campaigns()
                st.session_state['campaigns'] = campaigns
    except Exception as e:
        logging.error(f"Error refreshing campaigns: {e}")
        st.error("An error occurred while refreshing campaigns.")

def handle_show_campaign(selected_campaign_name, campaigns, history, spinner_placeholder):
    try:
        if selected_campaign_name:
            with spinner_placeholder:
                with st.spinner("Loading..."):
                    selected_campaign = next(campaign for campaign in campaigns if campaign.name == selected_campaign_name)
                    content_dict = selected_campaign.localized_content
                    translated_htmls = apply_template(content_dict, selected_campaign.liquid_template)
                    st.markdown(f"### Campaign: {selected_campaign_name}")
                    for lang, html in translated_htmls.items():
                        st.markdown(f"<details><summary>{lang}</summary>{html}</details>", unsafe_allow_html=True)
    except Exception as e:
        logging.error(f"Error showing campaign: {e}")
        st.error("An error occurred while showing the campaign.")

def handle_show_template(template_name, mongodb_client, history):
    try:
        content_template = mongodb_client.get_template_by_name(template_name)
        template_content = content_template['liquid_template']

        # Support both old format (Name/Type/MaxLength) and new format (name/type/label)
        items_lines = []
        for item in content_template['items']:
            # Try new format first (AI-generated templates)
            if 'name' in item:
                name = item.get('name', 'Unknown')
                type_ = item.get('type', 'text')
                label = item.get('label', name)
                required = '(Required)' if item.get('required', False) else '(Optional)'
                items_lines.append(f"{label}: {type_} {required}")
            # Fallback to old format (manual templates)
            else:
                name = item.get('Name', 'Unknown')
                type_ = item.get('Type', 'text')
                max_length = item.get('MaxLength', 'N/A')
                items_lines.append(f"{name}: {type_} (Max length: {max_length})")

        items_content = "<br>".join(items_lines)

        # Show rendered HTML with Liquid variables ({{UserPhone}} etc) visible
        # Append the template HTML directly for rendering (not escaped)
        history.append((f"Template Preview for {template_name}:", template_content))

        # Also show template items info
        items_html = f"<div style='background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 10px;'><strong>Template Fields:</strong><br>{items_content}</div>"
        history.append(("", items_html))

        st.session_state['history'] = history
    except Exception as e:
        logging.error(f"Error showing template: {e}")
        logging.error(f"Traceback object: {e.__traceback__}")  # Это объект трассировки для template
        # Получаем трассировку с помощью traceback
        trace = traceback.format_exception(type(e), e, e.__traceback__)

        # Логируем трассировку
        logging.error(f"Traceback details: {''.join(trace)}")
        st.error("An error occurred while showing the template.")

def handle_refresh_audiences(audience_repository):
    try:
        audiences = audience_repository.get_audiences()
        st.session_state['audiences'] = audiences
    except Exception as e:
        logging.error(f"Error refreshing audiences: {e}")
        st.error("An error occurred while refreshing audiences.")

def handle_create_audience(audience_name, audience_description, audience_repository):
    try:
        if audience_name and audience_description:
            new_audience = Audience(id=None, name=audience_name, description=audience_description)
            audience_repository.save_audience(new_audience)
            st.success(f"Audience '{audience_name}' created successfully!")
        else:
            st.error("Audience name and description cannot be empty.")
    except Exception as e:
        logging.error(f"Error creating audience: {e}")
        st.error("An error occurred while creating the audience.")

if __name__ == "__main__":
    main()