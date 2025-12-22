"""Campaign Setup Wizard - Guides new users through first campaign creation."""
import streamlit as st
from typing import List
from audience import Audience


class CampaignWizard:
    """4-step wizard for campaign setup to reduce new user churn."""

    def __init__(self, audiences: List[Audience], template_names: List[str]):
        """
        Initialize the wizard.

        Args:
            audiences: List of available audiences
            template_names: List of available template names
        """
        self.audiences = audiences
        self.template_names = template_names

        # Initialize wizard state
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 1
        if 'wizard_data' not in st.session_state:
            st.session_state.wizard_data = {}

    def run(self):
        """Run the wizard based on current step."""
        current_step = st.session_state.wizard_step

        # Progress bar
        st.progress(current_step / 4, text=f"Step {current_step} of 4")

        # Display current step
        if current_step == 1:
            self._step_1_audience()
        elif current_step == 2:
            self._step_2_platform()
        elif current_step == 3:
            self._step_3_template()
        elif current_step == 4:
            self._step_4_preview()

    def _step_1_audience(self):
        """Step 1: Select target audience."""
        st.markdown("### 👥 Step 1: Who is your target audience?")
        st.caption("Choose the audience you want to reach with your campaign")

        audience_names = [audience.name for audience in self.audiences]

        # Audience selection
        selected_audience = st.selectbox(
            "Select Audience",
            audience_names,
            key='wizard_audience',
            help="Choose your target audience for better content personalization"
        )

        # Show audience description
        if selected_audience:
            audience = next((a for a in self.audiences if a.name == selected_audience), None)
            if audience:
                st.info(f"📝 **Description:** {audience.description}")

        st.markdown("---")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Skip Wizard", key="skip_wizard_step1", use_container_width=True):
                st.session_state.wizard_active = False
                st.rerun()
        with col2:
            if st.button("Next →", key="next_step1", type="primary", use_container_width=True):
                # Save data and move to next step
                st.session_state.wizard_data['audience'] = selected_audience
                st.session_state.wizard_step = 2
                st.rerun()

    def _step_2_platform(self):
        """Step 2: Select target platform."""
        st.markdown("### 📱 Step 2: Which platform will you post on?")
        st.caption("Platform optimization improves hashtags, formatting, and timing")

        platform_options = {
            "instagram": "📷 Instagram - Best for visual content (18-35 age)",
            "facebook": "📘 Facebook - Best for local businesses & communities",
            "telegram": "✈️ Telegram - Best for tech-savvy, international audiences",
            "linkedin": "💼 LinkedIn - Best for B2B, SaaS, professional services"
        }

        selected_platform = st.radio(
            "Choose your platform",
            options=list(platform_options.keys()),
            format_func=lambda x: platform_options[x],
            key='wizard_platform'
        )

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("❌ Skip Wizard", key="skip_wizard_step2", use_container_width=True):
                st.session_state.wizard_active = False
                st.rerun()
        with col2:
            if st.button("← Back", key="back_step2", use_container_width=True):
                st.session_state.wizard_step = 1
                st.rerun()
        with col3:
            if st.button("Next →", key="next_step2", type="primary", use_container_width=True):
                # Save data and move to next step
                st.session_state.wizard_data['platform'] = selected_platform
                st.session_state.wizard_step = 3
                st.rerun()

    def _step_3_template(self):
        """Step 3: Select content template."""
        st.markdown("### 📝 Step 3: What type of content do you want to create?")
        st.caption("Choose a template that matches your campaign goal")

        # Group templates by category (if possible)
        selected_template = st.selectbox(
            "Select Content Template",
            self.template_names,
            key='wizard_template',
            help="Templates provide structure for different campaign types"
        )

        # Enable viral patterns by default
        use_viral = st.checkbox(
            "🔥 Use Viral Patterns (Recommended)",
            value=True,
            key='wizard_viral',
            help="Generate content with 2-3x more engagement using proven patterns"
        )

        if use_viral:
            st.info("💡 **Tip:** Viral patterns are based on 100+ successful campaigns and significantly boost engagement!")

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("❌ Skip Wizard", key="skip_wizard_step3", use_container_width=True):
                st.session_state.wizard_active = False
                st.rerun()
        with col2:
            if st.button("← Back", key="back_step3", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with col3:
            if st.button("Next →", key="next_step3", type="primary", use_container_width=True):
                # Save data and move to next step
                st.session_state.wizard_data['template'] = selected_template
                st.session_state.wizard_data['use_viral'] = use_viral
                st.session_state.wizard_step = 4
                st.rerun()

    def _step_4_preview(self):
        """Step 4: Preview settings and generate."""
        st.markdown("### ✅ Step 4: Review & Generate")
        st.caption("Review your settings and start generating content!")

        # Display summary
        wizard_data = st.session_state.wizard_data

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📋 Campaign Settings:**")
            st.markdown(f"👥 **Audience:** {wizard_data.get('audience', 'Not selected')}")
            st.markdown(f"📱 **Platform:** {wizard_data.get('platform', 'Not selected').title()}")

        with col2:
            st.markdown("**🎨 Content Settings:**")
            st.markdown(f"📝 **Template:** {wizard_data.get('template', 'Not selected')}")
            viral_status = "✅ Enabled" if wizard_data.get('use_viral', False) else "❌ Disabled"
            st.markdown(f"🔥 **Viral Patterns:** {viral_status}")

        # Query input
        st.markdown("---")
        st.markdown("**📝 Describe your campaign:**")

        query_placeholder = "Example: Launch 30-day transformation challenge with meal plan, workout videos, and coaching. Early bird: $199 (regular $299). Limited to 20 spots."

        user_query = st.text_area(
            "What do you want to promote?",
            placeholder=query_placeholder,
            height=150,
            key='wizard_query',
            help="Be specific about details, benefits, pricing, and urgency!"
        )

        st.markdown("---")

        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("❌ Cancel", key="cancel_wizard_step4", use_container_width=True):
                st.session_state.wizard_active = False
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {}
                st.rerun()
        with col2:
            if st.button("← Back", key="back_step4", use_container_width=True):
                st.session_state.wizard_step = 3
                st.rerun()
        with col3:
            if st.button("🚀 Generate Content", key="generate_step4", type="primary", use_container_width=True, disabled=not user_query):
                # Apply wizard settings to session state
                self._apply_wizard_settings(user_query)
                # Close wizard
                st.session_state.wizard_active = False
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {}
                st.success("✅ Wizard settings applied! Generating content...")
                st.rerun()

    def _apply_wizard_settings(self, user_query: str):
        """Apply wizard settings to main session state."""
        wizard_data = st.session_state.wizard_data

        # Set audience
        st.session_state['selected_audience_name'] = wizard_data.get('audience', '')

        # Set platform
        st.session_state['selected_platform'] = wizard_data.get('platform', 'instagram')

        # Set template
        st.session_state['template_name'] = wizard_data.get('template', '')

        # Set viral patterns
        st.session_state['use_viral_patterns'] = wizard_data.get('use_viral', False)

        # Set query
        st.session_state['user_query'] = user_query

        # Set default viral settings if enabled
        if wizard_data.get('use_viral', False):
            st.session_state['viral_industry'] = 'all'
            st.session_state['viral_account_type'] = 'brand_static_only'
            st.session_state['viral_content_type'] = 'static'
            st.session_state['viral_follower_count'] = 5000

        # Set flag to trigger generation
        st.session_state['wizard_generate_trigger'] = True
