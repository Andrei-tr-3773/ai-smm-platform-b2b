"""Signup page for new user registration."""
import streamlit as st
from utils.auth import hash_password, create_session, validate_password_strength
from repositories.user_repository import UserRepository
from repositories.workspace_repository import WorkspaceRepository
from models.user import User
from models.workspace import Workspace
import re
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

st.title("📝 Create Your Account")

st.markdown("""
Join thousands of businesses creating professional social media content in minutes.

**Start with Free plan:**
- 10 campaigns per month
- 3 languages
- Instagram + Facebook
- 1 custom template
""")

st.markdown("---")

# Signup form
with st.form("signup_form"):
    st.markdown("### Enter your information")

    name = st.text_input(
        "Full Name *",
        placeholder="John Smith",
        help="Your full name"
    )

    email = st.text_input(
        "Email *",
        placeholder="your@email.com",
        help="Your work email address"
    )

    password = st.text_input(
        "Password *",
        type="password",
        placeholder="Create a strong password",
        help="At least 8 characters, 1 uppercase letter, 1 number"
    )

    password_confirm = st.text_input(
        "Confirm Password *",
        type="password",
        placeholder="Re-enter your password"
    )

    st.markdown("---")

    company_name = st.text_input(
        "Company Name (optional)",
        placeholder="Your Business Name",
        help="Your company or workspace name"
    )

    st.markdown("---")

    agree_terms = st.checkbox(
        "I agree to the Terms of Service and Privacy Policy *",
        help="You must agree to create an account"
    )

    submit = st.form_submit_button(
        "Create Account",
        type="primary",
        use_container_width=True
    )

    if submit:
        # Validation
        errors = []

        # Required fields
        if not name or not email or not password:
            errors.append("Please fill in all required fields (marked with *)")

        # Email format
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid email format")

        # Password validation
        if password:
            is_valid, password_errors = validate_password_strength(password)
            if not is_valid:
                errors.extend(password_errors)

        # Password match
        if password != password_confirm:
            errors.append("Passwords do not match")

        # Terms agreement
        if not agree_terms:
            errors.append("You must agree to the Terms of Service")

        # Check if email already exists
        if email:
            try:
                user_repo = UserRepository()
                existing_user = user_repo.get_user_by_email(email)
                if existing_user:
                    errors.append("Email already registered. Please login instead.")
            except Exception as e:
                logger.error(f"Error checking existing email: {e}")

        # Display errors
        if errors:
            st.error("**Please fix the following errors:**")
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Create account
            try:
                # Create workspace first
                workspace_repo = WorkspaceRepository()
                workspace = Workspace(
                    name=company_name or f"{name}'s Workspace",
                    plan_tier="free",
                    owner_email=email
                )
                workspace_id = workspace_repo.create_workspace(workspace)

                # Create user
                user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    workspace_id=workspace_id,
                    role="owner"
                )
                user_id = user_repo.create_user(user)

                # Set ID for user object
                user.id = user_id

                # Create session
                create_session(user)

                st.success(f"✅ Account created! Welcome, {name}!")
                st.balloons()

                # Show next steps
                st.info("""
                **What's next?**
                1. Explore the Getting Started guide
                2. Create your first campaign
                3. Invite team members (coming soon)

                Redirecting to Getting Started page...
                """)

                # Auto-redirect after signup (wait a moment for user to see success message)
                import time
                time.sleep(2)
                st.switch_page("pages/00_Getting_Started.py")

            except Exception as e:
                logger.error(f"Signup error: {e}")
                st.error(f"❌ An error occurred during signup: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")

st.markdown("---")

# Login link
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("Already have an account?")

with col2:
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/02_Login.py")

# Social signup (placeholder for Week 7)
st.markdown("---")
st.markdown("### Or sign up with:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔵 Sign up with Google", use_container_width=True):
        st.info("Google OAuth coming in Week 7")

with col2:
    if st.button("💼 Sign up with LinkedIn", use_container_width=True):
        st.info("LinkedIn OAuth coming in Week 7")

# Footer
st.markdown("---")
st.caption("""
**Why create an account?**
- Track your usage and campaigns
- Save your work across devices
- Upgrade to unlock premium features
- Collaborate with team members

By creating an account, you agree to our Terms of Service and Privacy Policy.
""")
