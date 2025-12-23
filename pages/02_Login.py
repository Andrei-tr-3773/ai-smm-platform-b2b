"""Login page for user authentication."""
import streamlit as st
from utils.auth import verify_password, create_session
from repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.title("🔐 Login to AI SMM Platform")

st.markdown("""
Welcome back! Login to access your workspace and continue creating professional social media content.
""")

st.markdown("---")

# Login form
with st.form("login_form"):
    st.markdown("### Enter your credentials")

    email = st.text_input(
        "Email",
        placeholder="your@email.com",
        help="Email address you used to sign up"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        help="Your account password"
    )

    submit = st.form_submit_button(
        "Login",
        type="primary",
        use_container_width=True
    )

    if submit:
        # Validation
        if not email or not password:
            st.error("❌ Please enter both email and password")
        else:
            # Verify credentials
            try:
                repo = UserRepository()
                user = repo.get_user_by_email(email)

                if user and verify_password(password, user.password_hash):
                    # Create session
                    create_session(user)

                    st.success(f"✅ Welcome back, {user.name}!")
                    st.balloons()

                    # Redirect to home
                    st.info("Redirecting to Home...")
                    st.switch_page("Home.py")
                else:
                    st.error("❌ Invalid email or password")

                    # Increment failed login attempts (for security)
                    if user:
                        repo.increment_failed_login(email)

            except Exception as e:
                logger.error(f"Login error: {e}")
                st.error("❌ An error occurred during login. Please try again.")

st.markdown("---")

# Footer actions
col1, col2 = st.columns(2)

with col1:
    st.markdown("### New to our platform?")
    if st.button("📝 Create Account", use_container_width=True):
        st.switch_page("pages/03_Signup.py")

with col2:
    st.markdown("### Forgot Password?")
    if st.button("🔑 Reset Password", use_container_width=True):
        st.info("Password reset coming in Week 7! For now, contact support@example.com")

# OAuth section (placeholder for Week 7)
st.markdown("---")
st.markdown("### Or sign in with:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔵 Continue with Google", use_container_width=True):
        st.info("Google OAuth coming in Week 7")

with col2:
    if st.button("💼 Continue with LinkedIn", use_container_width=True):
        st.info("LinkedIn OAuth coming in Week 7")

# Footer
st.markdown("---")
st.caption("""
By logging in, you agree to our Terms of Service and Privacy Policy.

**Need help?** Contact support@example.com
""")
