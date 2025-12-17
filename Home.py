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
from agents.agent_state import AgentState
from audience import Audience
from repositories.audience_repository import AudienceRepository
from repositories.campaign_repository import CampaignRepository
from utils.ui_components import init_page_settings, load_css
from utils.llm_queries import predefined_query, DefaultPrompts
from utils.mongodb_utils import MongoDBClient
from campaign import Campaign
import streamlit as st
from utils.deepeval_openai import DeepEvalOpenAI
from utils.openai_utils import get_openai_model
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

def generate_content(user_query, template_name, state, prompts, add_context, selected_audience_name, selected_audience_description):
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
            selected_audience_description=selected_audience_description
        )

        interim_state = content_agent.graph.invoke(agent_state)
        state.update(interim_state)

        content_dict = {'en-US': json.loads(interim_state['initial_english_content'])}
        translated_htmls = apply_template(content_dict, content_template['liquid_template'])

        english_html = translated_htmls['en-US']
        logging.info(f"english_html: {english_html}")

        # Return HTML with language header
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

        with st.expander("📋 Content Guidelines", expanded=False):
            show_content_disclaimer()

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

            if not campaigns:
                campaigns = campaigns_client.get_campaigns()
                st.session_state['campaigns'] = campaigns

            col1, col2 = st.columns([1, 2])

            with col1:
                tabs = st.tabs(["Generate", "Translate"])

                with tabs[0]:
                    st.markdown("### Generate Content")
                    user_query = st.text_area("Enter your query here...", default_query, key='user_query')

                    if not template_names:
                        st.error("No content templates found. Please load templates into MongoDB.")
                        template_name = None
                    else:
                        default_index = template_names.index(default_template) if default_template in template_names else 0
                        template_name = st.selectbox("Select Content Template", template_names, index=default_index, key='template_name', on_change=update_query)

                    # Move audience selection here
                    selected_audience_name = st.selectbox("Select Audience", audience_names, key='selected_audience_name')
                    selected_audience_description = ""
                    if selected_audience_name:
                        selected_audience = next((audience for audience in audiences if audience.name == selected_audience_name), None)
                        if selected_audience:
                            selected_audience_description = selected_audience.description
                            st.session_state['selected_audience_description'] = selected_audience_description

                    add_context = st.checkbox("Add Context", value=True, key='add_context')
                    col1_1, col1_2 = st.columns(2)
                    generate_button = col1_1.button("Generate", use_container_width=True)
                    show_template_button = col1_2.button("Show Template", use_container_width=True)

                with tabs[1]:
                    st.markdown("### Translate Content")
                    selected_languages = st.multiselect("Select Languages", languages, default=default_languages)
                    selected_metrics = st.multiselect("Select Evaluation Metrics", list(EvaluationAgent.all_metrics.keys()), default=EvaluationAgent.default_metrics)
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
                handle_generate(user_query, template_name, state, prompts, history, spinner_placeholder, add_context)

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
                        # Use st.components for HTML rendering
                        if "<html" in response.lower() or "<div" in response.lower() or "<details" in response.lower():
                            st.components.v1.html(response, height=600, scrolling=True)
                        else:
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

        # Add the original user query (without audience context) to the chat history
        history.append([user_query, "Generating content..."])
        st.session_state['history'] = history

        with spinner_placeholder:
            with st.spinner("Generating..."):
                # Pass the audience information to the generate_content function
                result, new_state = generate_content(user_query, template_name, state, prompts, add_context, selected_audience_name, selected_audience_description)

        # Update the chat history with the generated content
        history[-1][1] = result
        st.session_state.update({'state': new_state, 'history': history})
    except Exception as e:
        logging.error(f"Error handling generate: {e}")
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
    except Exception as e:
        logging.error(f"Error handling translate: {e}")
        st.error("An error occurred during translation.")

def handle_clear(default_prompts):
    try:
        st.session_state.update({'state': {'messages': [], 'evaluation': {}, 'translations': {}, 'initial_english_content': '', 'selected_languages': [], 'content_template': None, 'criticisms': ''}, 'history': [], 'prompts': default_prompts})
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

        # Combine the template HTML and items into a single message
        combined_content = (
            f"<details><summary>{template_name} HTML</summary>{template_content}</details>"
            f"<details><summary>Template items</summary>{items_content}</details>"
        )

        # Append the combined content as a single message to the history
        history.append((f"Template Details for {template_name}:", combined_content))

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