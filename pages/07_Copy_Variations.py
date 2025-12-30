"""
Copy Variations Tool - Generate multiple copy variations with different angles.
"""

import streamlit as st
from agents.copy_variations_agent import CopyVariationsAgent
from utils.openai_utils import get_openai_model
from utils.auth import get_current_user
from repositories.workspace_repository import WorkspaceRepository
from utils.copy_quality import (
    analyze_copy_comprehensively,
    check_tone_consistency,
    detect_repetition,
    check_readability,
    check_cta_strength
)
from utils.copy_formulas import (
    COPY_FORMULAS,
    apply_formula_to_copy,
    list_all_formulas,
    explain_formula
)
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Copy Variations", page_icon="🎨", layout="wide")

st.title("🎨 Copy Variations Generator")

st.markdown("""
Generate 5 variations of your marketing copy using proven copywriting angles.
Perfect for A/B testing and finding the most effective message for your audience.

**5 Proven Angles:**
- 🔧 **Problem-Solution** - Address pain points
- 🤔 **Curiosity** - Create intrigue
- ⭐ **Social Proof** - Leverage testimonials
- ⏰ **FOMO** - Create urgency
- 🎯 **Benefit-Focused** - Focus on outcomes
""")

st.markdown("---")

# Get current user (optional - works for guests too)
user = get_current_user()

# Input section
st.header("📝 Original Copy")

col1, col2 = st.columns([2, 1])

with col1:
    original_copy = st.text_area(
        "Enter your marketing copy",
        placeholder="""Example:
Transform your social media in minutes with AI-powered content generation.
Create professional posts in 15+ languages. Start free today!""",
        height=150,
        help="Paste your existing copy or write new copy to generate variations"
    )

with col2:
    st.markdown("### 💡 Tips")
    st.info("""
    **Best results:**
    - Keep it 50-150 words
    - Include a clear value proposition
    - Have a call-to-action
    - Be specific about benefits
    """)

# Advanced options (optional)
with st.expander("⚙️ Advanced Options", expanded=False):
    st.markdown("**Context (optional)**")

    col_adv1, col_adv2 = st.columns(2)

    with col_adv1:
        product_name = st.text_input(
            "Product/Service Name",
            placeholder="e.g., AI SMM Platform",
            help="Optional - helps generate more contextual variations"
        )

    with col_adv2:
        target_audience = st.selectbox(
            "Target Audience",
            ["General", "Small Business Owners", "Marketing Managers", "Digital Agencies", "E-commerce", "SaaS Companies"],
            help="Optional - helps tailor copy to audience"
        )

# Generate button
st.markdown("---")

generate_clicked = st.button(
    "🎨 Generate 5 Variations",
    type="primary",
    use_container_width=True,
    disabled=not original_copy
)

if generate_clicked and original_copy:
    with st.spinner("Generating copy variations... This may take 30-60 seconds"):
        try:
            # Initialize agent
            model = get_openai_model()
            agent = CopyVariationsAgent(model)

            # Generate variations
            context = {
                "product_name": product_name if product_name else None,
                "target_audience": target_audience
            }

            variations = agent.generate_variations(original_copy, context)

            # Success message
            st.success("✅ 5 copy variations generated successfully!")

            # Display variations
            st.markdown("---")
            st.header("📊 Generated Variations")

            # Original copy for comparison
            with st.expander("📄 Original Copy (for comparison)", expanded=False):
                st.markdown(f"```\n{original_copy}\n```")

            # Display each variation
            for angle_key, variation_data in variations.items():
                with st.expander(
                    f"{variation_data['emoji']} {variation_data['name']} - {variation_data['description']}",
                    expanded=True
                ):
                    # Variation copy
                    st.markdown("**Generated Copy:**")
                    st.info(variation_data['copy'])

                    # Quality analysis for this variation
                    with st.container():
                        st.markdown("**📊 Quality Analysis:**")

                        quality = analyze_copy_comprehensively(
                            variation_data['copy'],
                            target_tone="persuasive"  # Variations are marketing copy
                        )

                        col_q1, col_q2, col_q3, col_q4 = st.columns(4)

                        with col_q1:
                            tone_score = quality["tone"]["score"]
                            color = "🟢" if tone_score >= 80 else "🟡" if tone_score >= 60 else "🔴"
                            st.metric("Tone", f"{color} {tone_score}/100")

                        with col_q2:
                            rep_score = quality["repetition"]["score"]
                            color = "🟢" if rep_score >= 80 else "🟡" if rep_score >= 60 else "🔴"
                            st.metric("Clarity", f"{color} {rep_score}/100")

                        with col_q3:
                            read_score = quality["readability"]["score"]
                            st.metric("Readability", quality["readability"]["rating"])

                        with col_q4:
                            cta_score = quality["cta"]["score"]
                            color = "🟢" if cta_score >= 70 else "🟡" if cta_score >= 40 else "🔴"
                            st.metric("CTA", f"{color} {cta_score}/100")

                        # Overall score
                        overall = quality["overall_score"]
                        if overall >= 80:
                            st.success(f"✅ Overall Quality: {overall}/100 - Excellent!")
                        elif overall >= 60:
                            st.info(f"💡 Overall Quality: {overall}/100 - Good")
                        else:
                            st.warning(f"⚠️ Overall Quality: {overall}/100 - Needs Improvement")

                    # Example for reference
                    with st.container():
                        col_var1, col_var2 = st.columns([3, 1])

                        with col_var1:
                            st.caption(f"**Example:** {variation_data['example']}")

                        with col_var2:
                            # Copy to clipboard button
                            if st.button(
                                "📋 Copy",
                                key=f"copy_{angle_key}",
                                help="Copy this variation to clipboard",
                                use_container_width=True
                            ):
                                # JavaScript to copy to clipboard
                                st.code(variation_data['copy'], language=None)
                                st.success("Copied!")

            # A/B Testing Recommendations
            st.markdown("---")
            st.header("🧪 A/B Testing Recommendations")

            recommendations = agent.compare_variations(variations)

            st.markdown("### 📈 Best Use Cases by Goal:")

            col_rec1, col_rec2, col_rec3 = st.columns(3)

            with col_rec1:
                st.markdown("**For Awareness:**")
                st.info(f"{variations[recommendations['best_for_awareness']]['emoji']} {variations[recommendations['best_for_awareness']]['name']}")

                st.markdown("**For Cold Traffic:**")
                st.info(f"{variations[recommendations['best_for_cold_traffic']]['emoji']} {variations[recommendations['best_for_cold_traffic']]['name']}")

            with col_rec2:
                st.markdown("**For Conversion:**")
                st.info(f"{variations[recommendations['best_for_conversion']]['emoji']} {variations[recommendations['best_for_conversion']]['name']}")

                st.markdown("**For Warm Traffic:**")
                st.info(f"{variations[recommendations['best_for_warm_traffic']]['emoji']} {variations[recommendations['best_for_warm_traffic']]['name']}")

            with col_rec3:
                st.markdown("**For Trust Building:**")
                st.info(f"{variations[recommendations['best_for_trust']]['emoji']} {variations[recommendations['best_for_trust']]['name']}")

            # Suggested A/B tests
            st.markdown("### 🔬 Suggested A/B Tests:")

            for test in recommendations['suggested_tests']:
                with st.expander(f"📊 {test['test_name']}", expanded=False):
                    col_test1, col_test2 = st.columns(2)

                    with col_test1:
                        st.markdown(f"**Variant A:** {variations[test['variant_a']]['name']}")
                        st.code(variations[test['variant_a']]['copy'], language=None)

                    with col_test2:
                        st.markdown(f"**Variant B:** {variations[test['variant_b']]['name']}")
                        st.code(variations[test['variant_b']]['copy'], language=None)

                    st.markdown(f"**Hypothesis:** {test['hypothesis']}")
                    st.markdown(f"**Metric to Track:** {test['metric']}")

            # Export all variations
            st.markdown("---")
            st.header("💾 Export Variations")

            # Create export text
            export_text = f"""Original Copy:
{original_copy}

---

Copy Variations Generated on {st.session_state.get('timestamp', 'N/A')}

"""
            for angle_key, variation_data in variations.items():
                export_text += f"""
{variation_data['emoji']} {variation_data['name']}:
{variation_data['copy']}

---
"""

            col_export1, col_export2 = st.columns([2, 1])

            with col_export1:
                st.download_button(
                    "📄 Download All Variations (TXT)",
                    data=export_text,
                    file_name="copy_variations.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col_export2:
                st.info("💡 Save variations for A/B testing")

        except Exception as e:
            logger.error(f"Error generating copy variations: {str(e)}")
            st.error(f"❌ Error generating variations: {str(e)}")
            st.info("Please try again or contact support if the issue persists.")

# Usage tracking (if user is logged in)
if user and generate_clicked and original_copy:
    try:
        workspace_repo = WorkspaceRepository()
        # Could track copy variations usage separately if needed
        logger.info(f"Copy variations generated by user {user.email}")
    except Exception as e:
        logger.warning(f"Could not track usage: {str(e)}")

# Copy Formulas Section
st.markdown("---")
st.header("📐 Copy Formula Library")

st.markdown("""
Apply proven copywriting formulas to your copy. Each formula is a battle-tested framework
used by top marketers to boost conversions.
""")

# Formula selector
formula_options = list_all_formulas()
formula_display = {f"{f['emoji']} {f['name']} - {f['best_for']}": f['key'] for f in formula_options}

selected_formula_display = st.selectbox(
    "Choose a Formula",
    options=list(formula_display.keys()),
    help="Select a copywriting formula to learn about or apply"
)

selected_formula_key = formula_display[selected_formula_display]

# Show formula details
with st.expander(f"ℹ️ About {COPY_FORMULAS[selected_formula_key]['name']}", expanded=False):
    st.markdown(explain_formula(selected_formula_key))

# Apply formula to original copy
if original_copy:
    if st.button(f"✨ Apply {COPY_FORMULAS[selected_formula_key]['name']} to Your Copy", type="secondary", use_container_width=True):
        with st.spinner(f"Applying {COPY_FORMULAS[selected_formula_key]['name']} formula..."):
            try:
                model = get_openai_model()
                formula_copy = apply_formula_to_copy(original_copy, selected_formula_key, model)

                st.success(f"✅ {COPY_FORMULAS[selected_formula_key]['name']} formula applied!")

                # Display result
                st.markdown("### ✨ Formula-Applied Copy:")
                st.info(formula_copy)

                # Quality check
                quality = analyze_copy_comprehensively(formula_copy, target_tone="persuasive")

                col_f1, col_f2, col_f3, col_f4 = st.columns(4)

                with col_f1:
                    st.metric("Overall Quality", f"{quality['overall_score']}/100")

                with col_f2:
                    st.metric("Tone", f"{quality['tone']['score']}/100")

                with col_f3:
                    st.metric("Readability", quality['readability']['rating'])

                with col_f4:
                    st.metric("CTA Strength", f"{quality['cta']['score']}/100")

                # Download button
                st.download_button(
                    "💾 Download Formula Copy",
                    data=formula_copy,
                    file_name=f"copy_{selected_formula_key}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                logger.error(f"Error applying formula: {str(e)}")
                st.error(f"❌ Error applying formula: {str(e)}")
else:
    st.info("💡 Enter copy above to apply formulas")

# Footer
st.markdown("---")
st.markdown("""
### 📚 Learn More About Copywriting Angles

**Problem-Solution** - Best for addressing specific pain points. Works well for cold traffic who are actively seeking solutions.

**Curiosity** - Great for increasing engagement and click-through rates. Creates an information gap that readers want to fill.

**Social Proof** - Builds trust and credibility. Most effective when you have strong numbers or testimonials.

**FOMO** - Drives immediate action through urgency and scarcity. Use ethically - only when deadlines/limits are real.

**Benefit-Focused** - Clear and direct. Works best for warm traffic who already understand the problem.

**Pro Tip:** Test 2-3 variations at a time. Start with Problem-Solution vs Benefit-Focused, then test the winner against others.
""")

st.caption("""
**Need help?** Check out our [copywriting guide](/Copywriting_Guide) or contact support@example.com
""")
