"""Payment success page - handles Stripe checkout completion."""

import streamlit as st
from utils.auth import require_auth
from repositories.workspace_repository import WorkspaceRepository
from utils.stripe_utils import verify_checkout_session
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Payment Successful", page_icon="✅", layout="centered")

# Require authentication
user = require_auth()

st.title("✅ Payment Successful!")

# Get session_id from URL query params
query_params = st.query_params

if "session_id" in query_params:
    session_id = query_params["session_id"]

    try:
        # Verify session with Stripe
        session_details = verify_checkout_session(session_id)

        if not session_details:
            st.error("❌ Could not verify payment session")
            st.info("Please contact support@example.com if you were charged")
            st.stop()

        if session_details["payment_status"] == "paid":
            # Update workspace plan
            workspace_repo = WorkspaceRepository()
            plan_tier = session_details["plan_tier"]
            subscription_id = session_details["subscription_id"]
            customer_id = session_details["customer_id"]

            # Upgrade workspace
            workspace_repo.upgrade_plan(
                workspace_id=user.workspace_id,
                new_tier=plan_tier,
                stripe_subscription_id=subscription_id,
                stripe_customer_id=customer_id,
            )

            logger.info(
                f"Workspace {user.workspace_id} upgraded to {plan_tier} via Stripe"
            )

            # Success message
            st.balloons()

            st.success(
                f"""
            🎉 **Welcome to the {plan_tier.upper()} plan!**

            Your payment has been processed successfully.
            """
            )

            # Show what's unlocked
            workspace = workspace_repo.get_workspace(user.workspace_id)
            limits = workspace.get_plan_limits()

            st.markdown("### 🔓 What's Unlocked:")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Campaigns per Month",
                    "Unlimited"
                    if limits["campaigns"] == -1
                    else f"{limits['campaigns']}",
                )
                st.metric("Languages", limits["languages"])

            with col2:
                st.metric("Custom Templates", limits["custom_templates"])
                st.metric("Team Members", limits["team_members"])

            # Next steps
            st.markdown("---")
            st.markdown("### 🚀 Next Steps:")

            st.markdown(
                f"""
            1. ✅ **Explore your new features** - You now have access to all {plan_tier.upper()} tier features
            2. 📧 **Check your email** - Invoice sent to {user.email}
            3. 📊 **Manage subscription** - View details in [Workspace Settings](/Workspace_Settings)
            4. 🎨 **Start creating** - Generate campaigns with your expanded limits
            """
            )

            # Action buttons
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "🏠 Go to Dashboard",
                    type="primary",
                    use_container_width=True,
                ):
                    st.switch_page("Home.py")

            with col2:
                if st.button(
                    "⚙️ Workspace Settings",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.switch_page("pages/05_Workspace_Settings.py")

            with col3:
                if st.button(
                    "📧 Support", type="secondary", use_container_width=True
                ):
                    st.info("Email: support@example.com")

            # Thank you message
            st.markdown("---")
            st.info(
                """
            ### 💙 Thank You!

            Thank you for upgrading! We're committed to helping you create amazing marketing content.

            If you have any questions or need help getting started, reach out to support@example.com
            """
            )

        elif session_details["payment_status"] == "unpaid":
            st.warning("⚠️ Payment not completed")
            st.info(
                """
            Your payment session was created but not completed.

            **What to do:**
            1. Return to [Pricing](/Pricing) to try again
            2. Contact support@example.com if you need help
            """
            )

            if st.button("Back to Pricing", type="primary"):
                st.switch_page("pages/06_Pricing.py")

        else:
            st.error(
                f"❌ Unknown payment status: {session_details['payment_status']}"
            )
            st.info("Please contact support@example.com")

    except Exception as e:
        logger.error(f"Error processing payment success: {str(e)}")
        st.error("❌ Error processing payment")
        st.exception(e)

        st.info(
            """
        **Don't worry!** If you were charged, we'll update your account shortly.

        Please contact support@example.com with:
        - Your email address
        - Payment confirmation number
        - This error message
        """
        )

else:
    # No session_id in URL
    st.warning("⚠️ No payment session found")

    st.info(
        """
    This page is for payment confirmations only.

    **Looking to upgrade?**
    Visit our [Pricing page](/Pricing) to choose a plan.
    """
    )

    if st.button("Go to Pricing", type="primary", use_container_width=True):
        st.switch_page("pages/06_Pricing.py")
