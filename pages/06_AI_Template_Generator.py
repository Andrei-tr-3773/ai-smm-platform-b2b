# 06_AI_Template_Generator.py
import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.template_generator_agent import TemplateGeneratorAgent
from repositories.template_repository import TemplateRepository
from utils.ui_components import init_page_settings, load_css
from liquid import Template, Environment
import logging

# Load environment variables
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

# Set page configuration
init_page_settings()
load_css("./static/ui/css/styles.css")

st.title("🤖 AI Template Generator")
st.markdown("""
Generate professional Liquid templates from plain English descriptions in **10 seconds**.

**How it works:**
1. Describe your desired template in plain English
2. AI analyzes your description and generates field schema
3. AI creates HTML/Liquid template with proper structure
4. Review, preview, and save to use in campaigns

**No HTML/Liquid knowledge needed!** ✨
""")

# Initialize session state
if 'generated_template' not in st.session_state:
    st.session_state.generated_template = None
if 'template_agent' not in st.session_state:
    # Initialize AI agent
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
    )
    st.session_state.template_agent = TemplateGeneratorAgent(model=model)

# Sidebar - Example Templates
with st.sidebar:
    st.header("📚 Example Templates")
    st.markdown("Click to use these descriptions:")

    examples = [
        {
            "name": "🏋️ Gym Class Announcement",
            "description": "I need template for gym class announcement with instructor photo, class name, date/time, and benefits. Include a registration button.",
            "industry": "Fitness"
        },
        {
            "name": "💻 SaaS Feature Update",
            "description": "Create a template for announcing new software features. Should have feature name, description, benefits, screenshot, and a 'Try Now' button.",
            "industry": "SaaS"
        },
        {
            "name": "🛍️ E-commerce Sale",
            "description": "Template for announcing a flash sale on dresses. Include product image, original price, sale price, discount percentage, and 'Shop Now' button.",
            "industry": "E-commerce"
        },
        {
            "name": "📚 Course Promotion",
            "description": "Template for promoting online courses with course title, instructor bio, video thumbnail, price, and enrollment button.",
            "industry": "Education"
        },
        {
            "name": "🍕 Restaurant Special",
            "description": "Template for restaurant daily special with dish name, photo, ingredients, chef name, and reservation link.",
            "industry": "Food & Beverage"
        },
        {
            "name": "⭐ Customer Testimonial",
            "description": "Customer testimonial template with customer name, photo, quote, rating stars, and company logo.",
            "industry": "Generic"
        },
        {
            "name": "📅 Event Invitation",
            "description": "Template for business event invitation with event title, speaker names, date/time, location, and RSVP button.",
            "industry": "Consulting"
        }
    ]

    for example in examples:
        if st.button(example['name'], key=f"example_{example['name']}", use_container_width=True):
            st.session_state.example_description = example['description']
            st.rerun()

# Main content area
st.header("1️⃣ Describe Your Template")

# Get description from example or user input
default_description = st.session_state.get('example_description', '')
if default_description:
    # Clear the example after using it
    del st.session_state.example_description

description = st.text_area(
    "Template Description",
    value=default_description,
    height=150,
    placeholder="Example: I need a template for announcing new product launches with product name, image, price, features list, and a 'Buy Now' button",
    help="Describe your template in plain English. Be specific about what fields you need (text, images, dates, prices, etc.)"
)

# Tips expander
with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    **Be specific about:**
    - **Content type**: Announcement, promotion, update, story, tutorial, event, sale
    - **Fields needed**: Names, photos, dates, prices, descriptions, buttons
    - **Layout preference**: Visual-focused (large images), text-focused, or balanced
    - **Call-to-action**: Buy, register, learn more, contact, etc.

    **Good example:**
    > "Template for fitness class announcement with instructor photo, class name, schedule, benefits list, and registration button"

    **Bad example:**
    > "Make a template for my business"
    """)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 Generate Template", type="primary", use_container_width=True)

# Generate template
if generate_button:
    if not description.strip():
        st.error("❌ Please enter a template description first.")
    else:
        with st.spinner("🤖 AI is generating your template..."):
            try:
                # Generate template
                result = st.session_state.template_agent.generate_template_from_description(description)

                # Check for errors
                if result.get('error'):
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.session_state.generated_template = result
                    st.success("✅ Template generated successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Exception: {str(e)}")
                logging.error(f"Template generation exception: {e}", exc_info=True)

# Display results
if st.session_state.generated_template:
    result = st.session_state.generated_template

    st.markdown("---")
    st.header("2️⃣ Generated Template")

    # Validation status
    validation = result['validation_result']
    if validation['valid']:
        st.success("✅ Template is valid and ready to use!")
    else:
        st.error("❌ Template validation failed")
        for error in validation['errors']:
            st.error(f"  • {error}")

    if validation['warnings']:
        st.warning("⚠️ Warnings:")
        for warning in validation['warnings']:
            st.warning(f"  • {warning}")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Field Schema", "🎨 Preview", "💾 Liquid Template", "🔍 Analysis"])

    # Tab 1: Field Schema
    with tab1:
        st.subheader("Field Schema")
        st.markdown("Fields that will be filled when creating campaigns:")

        field_schema = result['field_schema']

        # Display as table
        schema_data = []
        for field in field_schema:
            schema_data.append({
                "Field Name": field['name'],
                "Type": field['type'],
                "Label": field['label'],
                "Required": "✓" if field.get('required', False) else "○",
                "Placeholder": field.get('placeholder', '')
            })

        st.dataframe(schema_data, use_container_width=True, hide_index=True)

        st.info(f"📊 Total fields: {len(field_schema)}")

    # Tab 2: Preview
    with tab2:
        st.subheader("Template Preview")
        st.markdown("Preview with realistic sample data:")

        if result['preview_html']:
            # Check if preview is an error message
            if result['preview_html'].startswith("<p>Error"):
                st.error("Preview rendering failed")
                st.code(result['preview_html'], language='html')

                # Show raw template as fallback
                with st.expander("Show raw template"):
                    st.code(result['liquid_template'], language='liquid')
            else:
                # Display preview in a styled container
                st.markdown(
                    f"""
                    <div style="border: 2px solid #e0e0e0; padding: 20px; border-radius: 8px; background-color: #f9f9f9;">
                        {result['preview_html']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.caption("✨ Preview uses AI-generated realistic sample data based on your template's industry and content type")
        else:
            st.warning("Preview not available - template may have validation errors")

    # Tab 3: Liquid Template
    with tab3:
        st.subheader("Liquid Template Code")
        st.markdown("HTML template with Liquid syntax:")

        liquid_template = result['liquid_template']
        st.code(liquid_template, language='liquid')

        # Copy button
        st.download_button(
            label="📥 Download Template",
            data=liquid_template,
            file_name="template.liquid",
            mime="text/html"
        )

    # Tab 4: Analysis
    with tab4:
        st.subheader("AI Analysis")

        parsed_intent = result['parsed_intent']

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Content Type", parsed_intent.get('content_type', 'N/A'))
            st.metric("Industry", parsed_intent.get('industry', 'N/A'))
            st.metric("Layout", parsed_intent.get('layout', 'N/A'))

        with col2:
            st.metric("CTA Type", parsed_intent.get('cta', 'N/A'))
            st.metric("Tone", parsed_intent.get('tone', 'N/A'))
            st.metric("Fields Count", len(field_schema))

        st.markdown("**Key Elements Identified:**")
        key_elements = parsed_intent.get('key_elements', [])
        if key_elements:
            st.write(", ".join(key_elements))
        else:
            st.write("N/A")

        # Validation details
        st.markdown("**Validation Results:**")
        validation_cols = st.columns(3)
        with validation_cols[0]:
            status = "✅" if validation['syntax_pass'] else "❌"
            st.markdown(f"{status} **Syntax**")
        with validation_cols[1]:
            status = "✅" if validation['security_pass'] else "❌"
            st.markdown(f"{status} **Security**")
        with validation_cols[2]:
            status = "✅" if validation['consistency_pass'] else "❌"
            st.markdown(f"{status} **Consistency**")

    # Save template section
    st.markdown("---")
    st.header("3️⃣ Save Template")

    # Advanced Mode Toggle
    advanced_mode = st.checkbox(
        "🔧 Advanced Mode - Manually edit Liquid template",
        value=False,
        help="Enable this to manually edit the generated Liquid template before saving"
    )

    if advanced_mode:
        st.info("✏️ **Advanced Mode Enabled** - You can now manually edit the Liquid template below")

        # Editable Liquid template
        edited_liquid = st.text_area(
            "Liquid Template (Editable)",
            value=result['liquid_template'],
            height=300,
            help="Modify the Liquid template as needed. Make sure to keep field names consistent!"
        )

        # Validate button for edited template
        if st.button("🔍 Validate Edited Template"):
            try:
                # Re-validate the edited template
                env = Environment()
                template = env.from_string(edited_liquid)

                st.success("✅ Edited template syntax is valid!")

                # Update result with edited template
                result['liquid_template'] = edited_liquid

            except Exception as e:
                st.error(f"❌ Syntax error in edited template: {str(e)}")
    else:
        edited_liquid = result['liquid_template']

    if validation['valid'] or advanced_mode:
        col1, col2 = st.columns([2, 1])

        with col1:
            template_name = st.text_input(
                "Template Name",
                value=parsed_intent.get('content_type', 'custom') + "_template",
                help="Enter a unique name for this template"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            save_button = st.button("💾 Save to Templates", type="primary", use_container_width=True)

        if save_button:
            if not template_name.strip():
                st.error("❌ Please enter a template name")
            else:
                try:
                    # Use TemplateRepository for better data management
                    template_repo = TemplateRepository()

                    # Save AI-generated template
                    template_id = template_repo.save_ai_generated_template(
                        template_name=template_name,
                        description=description,
                        liquid_template=edited_liquid,  # Use edited version if in advanced mode
                        field_schema=result['field_schema'],
                        parsed_intent=parsed_intent,
                        workspace_id="default"  # TODO: Replace with actual workspace_id in Week 3
                    )

                    st.success(f"✅ Template '{template_name}' saved successfully!")
                    st.info(f"📋 Template ID: `{template_id}`")
                    st.info("You can now use this template in the **Home** tab to generate campaigns.")

                    # Show statistics
                    stats = template_repo.get_template_stats()
                    st.metric("Total Templates", stats['total_templates'])

                    # Clear generated template button
                    if st.button("🆕 Create Another Template"):
                        st.session_state.generated_template = None
                        st.rerun()

                except ValueError as e:
                    st.warning(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error saving template: {str(e)}")
                    logging.error(f"Template save error: {e}", exc_info=True)
    else:
        st.warning("⚠️ Template must be valid before saving. Please fix the validation errors above.")

# Footer
st.markdown("---")
st.caption("""
**AI Template Generator** - Powered by GPT-4o-mini

⏱️ Generates templates in ~10 seconds vs. 15-30 minutes manually
✨ No HTML/Liquid knowledge required
🔒 Security validated (XSS protection)
📊 Field consistency checked automatically
""")
