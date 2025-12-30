# Week 7: Content Tools (Blog/SEO & Enhanced Copywriting)

**Duration:** 20 hours
**Priority:** VALUE-ADD → **CHANGED TO MEDIUM** (see review below)
**Business Impact:** Enable blog content creation + improve copy quality
**ROI:** Content marketing channel + higher conversion rates
**Review Status:** ⚠️ **NEEDS PRIORITIZATION ADJUSTMENT** (critical issues identified)

---

## 🚨 TECH LEAD & BUSINESS ARCHITECT REVIEW

**Date:** 2025-12-29
**Reviewers:** Tech Lead + Business Architect
**Status:** ⚠️ **CONDITIONAL APPROVAL** (priorities need adjustment)

### 🔴 CRITICAL ISSUES IDENTIFIED:

#### **Issue #1: Wrong Audience Priority (BUSINESS)**
- ❌ **Blog generator targets 30-40% of users** (Jessica - SaaS marketers, Carlos - agencies)
- ❌ **Ignores 60% primary audience** (Alex - small business owners who need Instagram/Facebook/Telegram)
- ❌ **From B2B_TARGET_PERSONAS.md:**
  - Alex (60%): Needs Instagram Reels, Facebook posts, Telegram announcements
  - Jessica (30%): Needs B2B blog content ✅
  - Carlos (10%): Needs white-label blogs for clients ✅

**Impact:** -$37,740 MRR opportunity cost (60% × $62,900 target MRR)

**Recommendation:**
- 🔧 **Reduce blog scope from 12h → 6h** (MVP only)
- 🔧 **Add Instagram Reels script generator (6h)** for Alex persona
- 🔧 **Defer advanced SEO features** to Week 8+

---

#### **Issue #2: Stripe Integration Deferred (REVENUE BLOCKING)**
- ❌ **Stripe deferred to Week 8** but it's **CRITICAL for monetization**
- ❌ **Week 6 completed:** Users can sign up, but **can't pay**!
- ❌ **From FINANCIAL_MODEL.md:**
  - CAC payback: 0.67 months (under 1 month!)
  - LTV/CAC: 27:1 (exceptional)
  - **BUT:** We can't collect revenue without Stripe!

**Current State:**
- ✅ Authentication working
- ✅ Workspaces created
- ✅ Pricing page showing tiers
- ❌ **NO WAY TO UPGRADE** (Stripe placeholder only)

**Impact:**
- Every week delayed = lost MRR
- Can't validate pricing assumptions
- Can't test conversion rates
- Can't start CAC payback clock

**Recommendation:**
- 🔧 **PRIORITY #1: Stripe integration (6-8h) before blog generator**
- 🔧 **Week 7 Revised:** Stripe (8h) + Copy Variations (8h) + Blog MVP (4h) = 20h

---

#### **Issue #3: OpenAI API Cost Explosion Risk (TECH)**
- ❌ **Blog posts = 3,000-5,000 tokens** (vs 500-1,000 for social posts)
- ❌ **No rate limiting on blog generation**
- ❌ **From FINANCIAL_MODEL.md:**
  - Professional tier COGS: $13.60/month (200 posts)
  - Blog generator could add: +$5-10/user/month
  - Gross margin impact: 86% → 80% (bad!)

**Example Cost:**
- Social post: 500 input + 1,000 output = $0.0008
- Blog post: 1,500 input + 3,000 output = $0.0024 (3x more!)
- User generates 20 blogs/month = $0.048 (vs $0.016 for 20 social posts)

**Recommendation:**
- 🔧 **Add rate limiting:** Max 10 blogs/month for Professional tier
- 🔧 **Add to plan limits:** Blog posts separate from campaign posts
- 🔧 **Monitor costs:** Track blog vs campaign API spend

---

#### **Issue #4: SEO Keyword Strategy Weak (TECH)**
- ❌ **Using LLM for keyword research** (not Google Keyword Planner)
- ❌ **No search volume data** = can't prioritize keywords
- ❌ **Readability score** only works for English (Flesch formula)

**Problems:**
- LLM suggests "AI social media tool" but doesn't know it has 10k/month searches
- Competitors use Ahrefs/SEMrush ($99-399/month tools)
- Users expect accurate keyword data

**Recommendation:**
- 🔧 **Clearly label as "AI-suggested keywords"** (not "keyword research")
- 🔧 **Add disclaimer:** "For accurate search volume, use Ahrefs/SEMrush"
- 🔧 **Week 8+:** Consider Ahrefs API integration ($500/mo for 500 requests)
- 🔧 **Defer readability for non-English** to future

---

### ✅ WHAT'S GOOD (Approved):

#### **Copy Variations (8h) - EXCELLENT**
- ✅ Helps ALL personas (Alex, Jessica, Carlos)
- ✅ Low API cost (same as 5 social posts)
- ✅ High value: +15-20% conversion rates
- ✅ Enables A/B testing
- ✅ 5 angles cover all use cases

**ROI Calculation:**
- Cost: 8 hours ($800 @ $100/hr)
- Benefit: +15% conversion = +90 users/year @ $150 ARPU = +$13,500 MRR Year 1
- **ROI: 16.9:1** (excellent)

#### **Copy Quality Checks (2h) - GOOD**
- ✅ Tone consistency helps brand voice
- ✅ Repetition detection prevents bad copy
- ✅ Low implementation cost

#### **Copy Formulas (2h) - GOOD**
- ✅ Educational value for users
- ✅ PAS, AIDA, 4Ps proven frameworks
- ✅ Easy to implement

---

### 🔧 RECOMMENDED PLAN ADJUSTMENTS:

#### **Week 7 REVISED (20 hours):**

**PRIORITY #1: Stripe Integration (8 hours) - NEW**
- Payment processing for all tiers
- Webhook handling (subscription events)
- Upgrade/downgrade flow
- Invoice generation
- **Why first:** Unblocks revenue, validates pricing

**PRIORITY #2: Copy Variations (8 hours) - KEEP**
- 5 angle generator (problem, curiosity, social proof, FOMO, benefit)
- Copy quality checks
- Copy formulas (PAS, AIDA, 4Ps)
- **Why:** Helps all personas, high ROI

**PRIORITY #3: Blog Generator MVP (4 hours) - REDUCED**
- Basic blog post generation (1500-2000 words)
- Simple outline → content
- Meta tags (title, description)
- Export as Markdown/HTML
- **Defer:**
  - ❌ Advanced SEO (keyword density, readability) → Week 8
  - ❌ Multiple export formats (WordPress, Medium) → Week 8
  - ❌ Keyword research tool → Week 8+

**DEFERRED TO WEEK 8:**
- Instagram Reels Script Generator (6h) - for Alex persona
- Advanced blog SEO features (4h)
- OAuth integration (4h)
- Email service / SendGrid (4h)

---

### 💰 FINANCIAL ALIGNMENT CHECK:

**From FINANCIAL_MODEL.md targets:**

| Metric | Target (Month 12) | Week 7 Impact |
|--------|-------------------|---------------|
| **Paid Users** | 600 | Stripe enables payment ✅ |
| **MRR** | $62,900 | Stripe unblocks revenue ✅ |
| **ARPU** | $150 | Copy variations improve conversion ✅ |
| **Gross Margin** | 92% | Blog costs manageable with rate limits ✅ |
| **LTV/CAC** | 27:1 | Copy variations: +15% conversion = better LTV ✅ |

**From B2B_TARGET_PERSONAS.md:**

| Persona | % Users | Needs Week 7? | Why |
|---------|---------|---------------|-----|
| **Alex** (Small Business) | 60% | ⚠️ Partially | Copy variations ✅, Blog ❌, Stripe ✅ |
| **Jessica** (Marketing Manager) | 30% | ✅ Yes | Blog ✅, Copy variations ✅, Stripe ✅ |
| **Carlos** (Agency) | 10% | ✅ Yes | All features ✅ |

**Issue:** Blog generator serves 40% of users, but takes 60% of Week 7 time (12/20h).

**Solution:** Reduce blog to 20% of time (4/20h), focus on revenue (Stripe 40%) and conversion (copy 40%).

---

### 📊 REVISED WEEK 7 ROI:

**Original Plan:**
- Blog Generator: 12h → Benefits 40% users → ROI ~3:1
- Copy Variations: 8h → Benefits 100% users → ROI ~17:1
- **Weighted ROI:** ~8:1

**Revised Plan:**
- Stripe Integration: 8h → Unblocks ALL revenue → ROI ~50:1 (enables $62.9k MRR)
- Copy Variations: 8h → Benefits 100% users → ROI ~17:1
- Blog MVP: 4h → Benefits 40% users → ROI ~6:1
- **Weighted ROI:** ~28:1 (3.5x better!)

---

### ✅ FINAL RECOMMENDATION:

**Approve Week 7 with these changes:**

1. ✅ **ADD: Stripe Integration (8h)** - PRIORITY #1
2. ✅ **KEEP: Copy Variations (8h)** - PRIORITY #2
3. ✅ **REDUCE: Blog Generator (12h → 4h MVP)** - PRIORITY #3
4. ⏳ **DEFER: Advanced blog features** - Week 8+
5. ⏳ **DEFER: Instagram Reels generator** - Week 8 (for Alex persona)

**Rationale:**
- Revenue first (Stripe unblocks monetization)
- Conversion optimization (Copy variations improve all campaigns)
- Content tools last (Blog MVP for 40% of users)

**Expected Outcome:**
- Week 7 end: Users can upgrade and pay ✅
- Week 7 end: Copy quality improves (+15% conversion) ✅
- Week 7 end: Basic blog generation works (MVP) ✅

---

## 📋 Overview (REVISED)

**Status:** ✅ **APPROVED with prioritization changes**

**REVISED Goals:**
1. **Stripe Integration** (PRIORITY #1) - Enable paid subscriptions
2. **Copy Variations** (PRIORITY #2) - Generate 5 variations with different angles
3. **Blog Generator MVP** (PRIORITY #3) - Basic blog post generation

**What Changed:**
- ✅ **ADDED:** Stripe Integration (8h) - was deferred from Week 6
- ✅ **KEPT:** Copy Variations (8h) - high ROI for all users
- ⚠️ **REDUCED:** Blog Generator (12h → 4h MVP) - defer advanced features

**Rationale:**
- Revenue unblocking is critical (can't monetize without Stripe)
- Copy variations help 100% of users (all personas)
- Blog MVP sufficient for 40% of users (can iterate later)

---

## 🎯 Business Value

### Why Blog/SEO Generator?

**Current Pain:** Users have no way to create blog content for SEO/content marketing
- Can't drive organic traffic
- No top-of-funnel content
- Competitors rank higher on Google

**Solution:** AI-powered blog generator
- SEO keyword research
- Optimized article structure
- Meta tags generation
- Readability optimization

**Expected Impact:**
- +30% organic traffic in 6 months
- +15% inbound leads
- Better brand authority

### Why Copy Variations?

**Current Pain:** Users get 1 version of copy, don't know what works
- No A/B testing
- Miss better angles
- Lower conversion rates

**Solution:** Generate 5 variations with different approaches
- Problem-solution angle
- Curiosity-driven angle
- Social proof angle
- FOMO (urgency) angle
- Benefit-focused angle

**Expected Impact:**
- +20% click-through rates
- +15% conversion rates
- Users learn what resonates

---

## 📅 Week 7 Tasks (REVISED)

### Task 7.0: Stripe Integration (8 hours) - NEW, PRIORITY #1

**Goal:** Enable paid subscriptions and monetization

**Why First:**
- Week 6 completed auth/workspaces, but users can't upgrade
- Every week delayed = lost MRR
- CAC payback 0.67 months (need payment flow)
- Validates pricing assumptions

#### 7.0.1: Stripe Setup & Product Configuration (2 hours)

**Setup:**
1. Create Stripe account (if not exists)
2. Create Products & Prices for each tier:
   - Starter: $49/month (price_starter_monthly)
   - Professional: $99/month (price_pro_monthly)
   - Team: $199/month (price_team_monthly)
   - Agency: $499/month (price_agency_monthly)
   - Enterprise: Custom pricing (manual)

3. Create test products in Stripe Test Mode
4. Add Stripe API keys to `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

**Deliverable:** Stripe account configured with all pricing tiers

---

#### 7.0.2: Payment Flow Implementation (3 hours)

**Files to Create/Modify:**
- `utils/stripe_utils.py` - Stripe client and utilities
- `pages/06_Pricing.py` - Update upgrade buttons to use Stripe
- `pages/08_Checkout.py` - NEW: Stripe checkout page

**Implementation:**
```python
# utils/stripe_utils.py
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_IDS = {
    "starter": os.getenv("STRIPE_PRICE_STARTER"),
    "professional": os.getenv("STRIPE_PRICE_PRO"),
    "team": os.getenv("STRIPE_PRICE_TEAM"),
    "agency": os.getenv("STRIPE_PRICE_AGENCY"),
}


def create_checkout_session(user_email: str, plan_tier: str, workspace_id: str):
    """Create Stripe checkout session."""
    price_id = PRICE_IDS.get(plan_tier)

    if not price_id:
        raise ValueError(f"Invalid plan tier: {plan_tier}")

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f"{os.getenv('APP_URL')}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{os.getenv('APP_URL')}/pricing",
        customer_email=user_email,
        metadata={
            'workspace_id': workspace_id,
            'plan_tier': plan_tier
        }
    )

    return session


def get_customer_subscriptions(customer_id: str):
    """Get all subscriptions for a customer."""
    return stripe.Subscription.list(customer=customer_id)


def cancel_subscription(subscription_id: str):
    """Cancel subscription at period end."""
    return stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True
    )
```

**Update pages/06_Pricing.py:**
```python
# Replace placeholder buttons with real Stripe checkout

from utils.stripe_utils import create_checkout_session

if st.button("Upgrade to Starter", type="primary", use_container_width=True):
    if user:
        try:
            session = create_checkout_session(
                user_email=user.email,
                plan_tier="starter",
                workspace_id=user.workspace_id
            )

            # Redirect to Stripe Checkout
            st.markdown(f"[Proceed to Payment]({session.url})")

        except Exception as e:
            st.error(f"❌ Payment error: {str(e)}")
    else:
        st.info("Please login first")
        st.switch_page("pages/02_Login.py")
```

**Deliverable:** Users can click "Upgrade" and reach Stripe checkout

---

#### 7.0.3: Webhook Handling (2 hours)

**Goal:** Handle subscription events from Stripe

**Files to Create:**
- `webhooks/stripe_webhook.py` - Webhook endpoint (or add to Streamlit)
- Note: Streamlit doesn't natively support webhooks, so we'll use polling approach

**Implementation Strategy:**

**Option A: External webhook service (recommended for production)**
- Deploy FastAPI/Flask webhook endpoint separately
- Stripe → Webhook → Update MongoDB

**Option B: Manual verification (MVP for Week 7)**
- User completes payment
- On "Success" page, verify session with Stripe
- Update workspace plan_tier

```python
# pages/09_Success.py - Payment Success Handler
import streamlit as st
from utils.auth import require_auth
from repositories.workspace_repository import WorkspaceRepository
import stripe

st.set_page_config(page_title="Payment Success", page_icon="✅")

user = require_auth()

# Get session_id from URL
session_id = st.query_params.get("session_id")

if session_id:
    try:
        # Verify session with Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            # Update workspace
            workspace_repo = WorkspaceRepository()
            plan_tier = session.metadata.get("plan_tier")
            subscription_id = session.subscription

            workspace_repo.upgrade_plan(
                workspace_id=user.workspace_id,
                new_tier=plan_tier,
                stripe_subscription_id=subscription_id
            )

            st.success(f"✅ Payment successful! Upgraded to {plan_tier.upper()} plan.")
            st.balloons()

            st.info(f"""
            **What's next:**
            - Your new limits are active immediately
            - Check Workspace Settings to see usage
            - Invoice will be sent to {user.email}
            """)

            if st.button("Go to Dashboard", type="primary"):
                st.switch_page("Home.py")

        else:
            st.error("Payment not completed. Please try again.")

    except Exception as e:
        st.error(f"❌ Error verifying payment: {str(e)}")
else:
    st.warning("No payment session found")
```

**Deliverable:** Successful payments upgrade workspace plan_tier

---

#### 7.0.4: Subscription Management UI (1 hour)

**Update pages/05_Workspace_Settings.py - Billing Tab:**

```python
# Tab 4: Billing
with tab4:
    st.header("💳 Billing & Subscription")

    st.subheader(f"Current Plan: **{workspace.plan_tier.upper()}**")

    if workspace.plan_tier == "free":
        st.info("You're on the Free plan. Upgrade to unlock premium features!")
        if st.button("Upgrade Now", type="primary"):
            st.switch_page("pages/06_Pricing.py")
    else:
        st.success(f"✅ Subscribed to {workspace.plan_tier.upper()} plan")

        # Show subscription details
        if workspace.stripe_subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(workspace.stripe_subscription_id)

                st.markdown("### Subscription Details")
                st.info(f"""
                **Status:** {subscription.status}
                **Billing Period:** {subscription.current_period_start} - {subscription.current_period_end}
                **Next Payment:** {subscription.current_period_end}
                **Amount:** ${subscription.plan.amount/100}/month
                """)

                # Cancel subscription
                if subscription.cancel_at_period_end:
                    st.warning("⚠️ Subscription will cancel at end of period")
                else:
                    if st.button("Cancel Subscription", type="secondary"):
                        confirm = st.checkbox("I confirm I want to cancel")
                        if confirm:
                            cancel_subscription(workspace.stripe_subscription_id)
                            st.success("Subscription will cancel at end of billing period")
                            st.rerun()

            except Exception as e:
                st.error(f"Error loading subscription: {str(e)}")

        # Change plan
        st.markdown("### Change Plan")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Upgrade Plan", type="primary", use_container_width=True):
                st.switch_page("pages/06_Pricing.py")

        with col2:
            if st.button("Downgrade Plan", type="secondary", use_container_width=True):
                st.info("Contact support@example.com to downgrade")
```

**Deliverable:** Users can view subscription, cancel, change plans

---

**Task 7.0 Summary:**
- ✅ Stripe configured with all pricing tiers
- ✅ Checkout flow working
- ✅ Payment success handler
- ✅ Subscription management UI
- ⏳ Full webhook handling (defer to Week 8 if needed - use manual verification MVP)

**Total Time:** 8 hours

---

### Task 7.1: Blog & SEO Generator MVP (4 hours) - REDUCED

**Goal:** Enable basic AI blog post generation (MVP only)

**⚠️ SCOPE REDUCTION from 12h → 4h:**
- ✅ **KEEP:** Basic blog generation (outline → content)
- ✅ **KEEP:** Simple meta tags (title, description)
- ✅ **KEEP:** Markdown/HTML export
- ❌ **DEFER:** Advanced SEO (keyword density, readability) → Week 8+
- ❌ **DEFER:** Multiple export formats (WordPress, Medium) → Week 8+
- ❌ **DEFER:** LangGraph multi-node workflow → Use simple single-step generation

**Why MVP Approach:**
- Blog serves only 40% of users (Jessica/Carlos)
- Focus Week 7 on revenue (Stripe) and conversion (Copy variations)
- Can iterate on blog features based on user feedback

---

#### 7.1.1: Simple Blog Generator (2 hours)

**Simplified Architecture:**
```python
# agents/blog_generator_agent.py

class BlogGeneratorAgent:
    """Simple blog generator without complex workflow."""

    def __init__(self, model):
        self.model = model

    def generate_blog(self, topic: str, target_audience: str, tone: str, word_count: int) -> dict:
        """Generate blog post in single step."""
        prompt = f"""
        Write a professional blog post about: {topic}

        Target Audience: {target_audience}
        Tone: {tone}
        Target Length: {word_count} words

        Structure:
        1. Compelling introduction (hook + problem statement)
        2. 3-5 main sections with H2 headings
        3. Each section: 200-400 words with examples
        4. Conclusion with clear CTA

        Return as Markdown format.
        """

        # Generate content
        content = self.model.invoke(prompt)

        # Generate simple meta tags
        meta = self._generate_meta_tags(content, topic)

        return {
            "content": content,
            "meta_title": meta["title"],
            "meta_description": meta["description"],
            "word_count": len(content.split())
        }

    def _generate_meta_tags(self, content: str, topic: str) -> dict:
        """Generate basic meta tags."""
        # Extract first line as title
        lines = content.split('\n')
        title = lines[0].replace('#', '').strip()[:60]

        # Use first paragraph as description
        description = lines[2] if len(lines) > 2 else content[:160]
        description = description[:157] + "..."

        return {
            "title": title,
            "description": description
        }
```

**Deliverable:**
- ✅ Simple blog generation (single LLM call)
- ✅ Basic meta tags
- ✅ Markdown output
- ⏳ Advanced features deferred to Week 8+

---

#### 7.1.2: Blog UI & Export (2 hours)

**Minimal UI:**
```python
# Add to Home.py or new tab "Blog Generator"

st.title("📝 Blog Generator (MVP)")

# Input
topic = st.text_input(
    "Blog Topic",
    placeholder="E.g., 'How to use AI for social media marketing'",
    help="What do you want to write about?"
)

target_audience = st.selectbox(
    "Target Audience",
    ["Small business owners", "Marketing managers", "Digital agencies", "General public"]
)

tone = st.selectbox(
    "Tone",
    ["Professional", "Casual", "Educational", "Persuasive"]
)

word_count_target = st.slider("Target Word Count", 1000, 2500, 1500, 500)

if st.button("Generate Blog Post", type="primary"):
    with st.spinner("Generating blog post (this may take 30-60 seconds)..."):
        blog_agent = BlogGeneratorAgent(model)
        result = blog_agent.generate_blog(topic, target_audience, tone, word_count_target)

    st.success("✅ Blog post generated!")

    # Show meta tags
    with st.expander("🔍 SEO Meta Tags", expanded=False):
        st.text_input("Meta Title", value=result['meta_title'], disabled=True)
        st.text_area("Meta Description", value=result['meta_description'], disabled=True)
        st.info("💡 Advanced SEO features (keyword density, readability) coming in Week 8+")

    # Show content
    st.markdown("---")
    st.markdown("### Generated Blog Post")
    st.markdown(result['content'])

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        # Markdown export
        st.download_button(
            "💾 Download Markdown",
            data=result['content'],
            file_name=f"blog_{topic[:30]}.md",
            mime="text/markdown"
        )

    with col2:
        # Simple HTML export
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{result['meta_title']}</title>
    <meta name="description" content="{result['meta_description']}">
</head>
<body>
    <article>
        {markdown.markdown(result['content'])}
    </article>
</body>
</html>"""

        st.download_button(
            "🌐 Download HTML",
            data=html_content,
            file_name=f"blog_{topic[:30]}.html",
            mime="text/html"
        )
```

**Deliverable:**
- ✅ Simple blog UI
- ✅ Basic meta tags display
- ✅ Markdown/HTML export
- ⏳ Advanced formats (WordPress, Medium) deferred

---

**Task 7.1 MVP Summary:**
- ✅ Blog generation works (single-step LLM call)
- ✅ Basic meta tags (title, description)
- ✅ Markdown/HTML export
- ⏳ **DEFERRED to Week 8+:**
  - Keyword research
  - Keyword density tracking
  - Readability scoring (Flesch formula)
  - WordPress/Medium export formats
  - LangGraph multi-node workflow
  - Advanced SEO optimization

**Total Time:** 4 hours (vs 12h original)
**Scope:** 33% of original features (sufficient for MVP)

---

### Task 7.2: Copywriting Improvements (8 hours)

**Goal:** Generate multiple copy variations with different angles

#### 7.2.1: Copy Variation Generator (4 hours)

**Angles to Generate:**
1. **Problem-Solution** - "Struggling with X? Here's how to fix it."
2. **Curiosity** - "You won't believe what happened when..."
3. **Social Proof** - "Join 10,000+ businesses who..."
4. **FOMO** - "Limited time: Don't miss out on..."
5. **Benefit-Focused** - "Get X results in Y days"

**Implementation:**
```python
# agents/copy_variations_agent.py

class CopyVariationsAgent:
    """Generate 5 copy variations with different angles."""

    ANGLES = {
        "problem_solution": {
            "description": "Address pain point + offer solution",
            "prompt_template": """
            Rewrite this campaign copy using Problem-Solution angle:

            Original: {original_copy}

            Rules:
            1. Start with a relatable problem
            2. Agitate the pain (why it's frustrating)
            3. Present solution (product/service)
            4. Clear CTA

            Example format:
            "Tired of [problem]? [Product] helps you [benefit] in [timeframe]."
            """,
            "emoji": "🔧"
        },
        "curiosity": {
            "description": "Create intrigue and curiosity gap",
            "prompt_template": """
            Rewrite this campaign copy using Curiosity angle:

            Original: {original_copy}

            Rules:
            1. Start with surprising fact or question
            2. Create information gap
            3. Tease benefit without revealing all
            4. CTA that promises answer

            Example format:
            "The secret to [outcome] that nobody talks about..."
            """,
            "emoji": "🤔"
        },
        "social_proof": {
            "description": "Leverage numbers and testimonials",
            "prompt_template": """
            Rewrite this campaign copy using Social Proof angle:

            Original: {original_copy}

            Rules:
            1. Start with impressive number (users, results)
            2. Build credibility
            3. Show transformation
            4. CTA to join community

            Example format:
            "Join 10,000+ [audience] who achieved [result]..."
            """,
            "emoji": "⭐"
        },
        "fomo": {
            "description": "Create urgency and scarcity",
            "prompt_template": """
            Rewrite this campaign copy using FOMO angle:

            Original: {original_copy}

            Rules:
            1. Add time constraint (limited time, ending soon)
            2. Add scarcity (limited spots, while supplies last)
            3. Emphasize what they'll miss
            4. Urgent CTA

            Example format:
            "Last chance: Only 3 spots left for [offer]..."
            """,
            "emoji": "⏰"
        },
        "benefit_focused": {
            "description": "Focus on outcomes and results",
            "prompt_template": """
            Rewrite this campaign copy using Benefit-Focused angle:

            Original: {original_copy}

            Rules:
            1. Start with specific outcome
            2. Add timeframe (fast results)
            3. List 3 key benefits
            4. Clear action-oriented CTA

            Example format:
            "Get [specific result] in [timeframe]. No [objection]."
            """,
            "emoji": "🎯"
        }
    }

    def generate_variations(self, original_copy: str) -> dict:
        """Generate 5 variations with different angles."""
        variations = {}

        for angle_name, angle_config in self.ANGLES.items():
            prompt = angle_config["prompt_template"].format(
                original_copy=original_copy
            )

            # Call LLM
            variation = self.model.invoke(prompt)

            variations[angle_name] = {
                "copy": variation,
                "angle": angle_config["description"],
                "emoji": angle_config["emoji"]
            }

        return variations
```

**UI Integration:**
```python
# In Home.py after content generation

if st.checkbox("🎨 Generate Copy Variations (5 different angles)", value=False):
    with st.spinner("Generating variations..."):
        variations = copy_variations_agent.generate_variations(english_content)

    st.markdown("---")
    st.markdown("### 🎨 Copy Variations")

    # Show each variation
    for angle, data in variations.items():
        with st.expander(f"{data['emoji']} {data['angle']}", expanded=False):
            st.markdown(data['copy'])

            # Copy to clipboard button
            st.button(
                "📋 Use This Version",
                key=f"use_{angle}",
                help="Replace original copy with this variation"
            )
```

**Deliverable:**
- ✅ 5 copy variation angles implemented
- ✅ Angle-specific prompts
- ✅ UI to display variations
- ✅ Easy copy/paste or replace original

---

#### 7.2.2: Copy Quality Checks (2 hours)

**Quality Checkers:**
```python
# utils/copy_quality.py

def check_tone_consistency(text: str, target_tone: str) -> dict:
    """
    Check if text matches target tone.

    Args:
        text: Copy text
        target_tone: "professional", "casual", "persuasive", "educational"

    Returns:
        {
            "score": 0-100,
            "issues": ["Too formal for casual tone", ...],
            "suggestions": ["Use contractions", ...]
        }
    """
    prompt = f"""
    Analyze this text for tone consistency:

    Text: {text}
    Target Tone: {target_tone}

    Check:
    1. Word choice matches tone
    2. Sentence structure appropriate
    3. Level of formality correct

    Return JSON:
    {{
        "score": 85,
        "issues": ["Too formal in paragraph 2"],
        "suggestions": ["Use 'you' instead of 'one'"]
    }}
    """
    # Call LLM
    result = llm.invoke(prompt)
    return json.loads(result)


def detect_repetition(text: str) -> dict:
    """Detect repeated words/phrases."""
    words = text.lower().split()
    word_counts = {}

    for word in words:
        if len(word) > 3:  # Ignore short words
            word_counts[word] = word_counts.get(word, 0) + 1

    # Find words used more than 3 times
    repetitive = {word: count for word, count in word_counts.items() if count > 3}

    return {
        "repetitive_words": repetitive,
        "score": 100 - (len(repetitive) * 10),  # Penalty for each repetitive word
        "suggestions": [f"Consider synonyms for '{word}' (used {count}x)"
                       for word, count in repetitive.items()]
    }


def suggest_ab_tests(original_copy: str, variations: dict) -> list:
    """Suggest which variations to A/B test."""
    suggestions = [
        {
            "test_name": "Problem vs Benefit",
            "variant_a": "problem_solution",
            "variant_b": "benefit_focused",
            "hypothesis": "Problem-focused copy may resonate more with users experiencing pain",
            "metric": "Click-through rate"
        },
        {
            "test_name": "Urgency vs Social Proof",
            "variant_a": "fomo",
            "variant_b": "social_proof",
            "hypothesis": "FOMO may drive faster action, social proof builds trust",
            "metric": "Conversion rate"
        },
        {
            "test_name": "Curiosity Hook",
            "variant_a": "curiosity",
            "variant_b": "benefit_focused",
            "hypothesis": "Curiosity may increase engagement, benefits show value",
            "metric": "Time on page"
        }
    ]

    return suggestions
```

**UI Integration:**
```python
# Add to copy variations section

st.markdown("---")
st.markdown("### ✅ Copy Quality Checks")

# Tone consistency
tone_result = check_tone_consistency(english_content, target_tone)
st.metric("Tone Consistency", f"{tone_result['score']}/100")

if tone_result['issues']:
    with st.expander("⚠️ Tone Issues", expanded=False):
        for issue in tone_result['issues']:
            st.warning(issue)
        for suggestion in tone_result['suggestions']:
            st.info(f"💡 {suggestion}")

# Repetition detection
repetition_result = detect_repetition(english_content)
st.metric("Repetition Score", f"{repetition_result['score']}/100")

if repetition_result['repetitive_words']:
    with st.expander("🔁 Repetitive Words", expanded=False):
        for word, count in repetition_result['repetitive_words'].items():
            st.text(f"'{word}' used {count} times")

# A/B test suggestions
with st.expander("🧪 A/B Test Suggestions", expanded=False):
    ab_tests = suggest_ab_tests(english_content, variations)

    for test in ab_tests:
        st.markdown(f"**{test['test_name']}**")
        st.markdown(f"- Variant A: {test['variant_a']}")
        st.markdown(f"- Variant B: {test['variant_b']}")
        st.markdown(f"- Hypothesis: {test['hypothesis']}")
        st.markdown(f"- Metric to track: {test['metric']}")
        st.markdown("---")
```

**Deliverable:**
- ✅ Tone consistency checker
- ✅ Repetition detector
- ✅ A/B test suggestions
- ✅ Quality scores displayed

---

#### 7.2.3: Copy Templates Library (2 hours)

**Pre-built Copy Formulas:**
```python
# utils/copy_templates.py

COPY_FORMULAS = {
    "PAS": {
        "name": "Problem-Agitate-Solve",
        "structure": [
            "Problem: Identify pain point",
            "Agitate: Make it worse",
            "Solve: Present solution"
        ],
        "example": "Tired of [problem]? It gets worse: [agitate]. Here's how [product] solves it.",
        "use_case": "Sales pages, ads"
    },
    "AIDA": {
        "name": "Attention-Interest-Desire-Action",
        "structure": [
            "Attention: Grab attention with hook",
            "Interest: Build interest",
            "Desire: Create desire",
            "Action: Clear CTA"
        ],
        "example": "[Hook]. Here's why it matters: [benefit]. Imagine [outcome]. [CTA].",
        "use_case": "Email marketing, landing pages"
    },
    "4Ps": {
        "name": "Promise-Picture-Proof-Push",
        "structure": [
            "Promise: State benefit",
            "Picture: Paint vision of outcome",
            "Proof: Provide evidence",
            "Push: Drive to action"
        ],
        "example": "[Benefit]. Imagine [outcome]. See what [testimonial]. [CTA].",
        "use_case": "Product launches"
    },
    "BAB": {
        "name": "Before-After-Bridge",
        "structure": [
            "Before: Current pain state",
            "After: Desired outcome",
            "Bridge: How to get there"
        ],
        "example": "Before: [pain]. After: [outcome]. [Product] is the bridge.",
        "use_case": "Transformation stories"
    },
    "FAB": {
        "name": "Features-Advantages-Benefits",
        "structure": [
            "Features: What it has",
            "Advantages: Why it's better",
            "Benefits: What you get"
        ],
        "example": "[Feature] means [advantage], so you get [benefit].",
        "use_case": "Product descriptions"
    }
}


def apply_copy_formula(content: str, formula_name: str) -> str:
    """Apply copy formula to existing content."""
    formula = COPY_FORMULAS.get(formula_name)

    if not formula:
        return content

    prompt = f"""
    Rewrite this content using the {formula['name']} formula:

    Original: {content}

    Structure:
    {chr(10).join(formula['structure'])}

    Example: {formula['example']}
    """

    # Call LLM
    result = llm.invoke(prompt)
    return result
```

**UI Integration:**
```python
# Add copy formula selector

st.markdown("---")
st.markdown("### 📐 Apply Copy Formula")

formula_name = st.selectbox(
    "Choose Formula",
    list(COPY_FORMULAS.keys()),
    format_func=lambda x: f"{x} - {COPY_FORMULAS[x]['name']}"
)

if formula_name:
    formula = COPY_FORMULAS[formula_name]

    with st.expander("ℹ️ About This Formula", expanded=False):
        st.markdown(f"**{formula['name']}**")
        st.markdown("**Structure:**")
        for step in formula['structure']:
            st.markdown(f"- {step}")
        st.markdown(f"**Example:** {formula['example']}")
        st.markdown(f"**Best for:** {formula['use_case']}")

    if st.button("Apply Formula", type="secondary"):
        with st.spinner("Rewriting..."):
            rewritten = apply_copy_formula(english_content, formula_name)

        st.markdown("### ✨ Rewritten Copy")
        st.markdown(rewritten)
```

**Deliverable:**
- ✅ 5 copy formulas (PAS, AIDA, 4Ps, BAB, FAB)
- ✅ Formula explainer
- ✅ Apply formula to existing copy
- ✅ UI integration

---

## 📦 Week 7 Summary (REVISED)

**Total Time:** 20 hours

**REVISED Breakdown:**
- **Task 7.0: Stripe Integration (8h) - NEW, PRIORITY #1**
  - 7.0.1: Stripe Setup & Product Configuration (2h)
  - 7.0.2: Payment Flow Implementation (3h)
  - 7.0.3: Webhook Handling (2h)
  - 7.0.4: Subscription Management UI (1h)
- **Task 7.1: Blog Generator MVP (4h) - REDUCED from 12h, PRIORITY #3**
  - 7.1.1: Simple Blog Generator (2h)
  - 7.1.2: Blog UI & Export (2h)
- **Task 7.2: Copy Variations (8h) - KEPT, PRIORITY #2**
  - 7.2.1: Copy Variation Generator (4h)
  - 7.2.2: Copy Quality Checks (2h)
  - 7.2.3: Copy Templates Library (2h)

**Key Changes from Original Plan:**
- ✅ **ADDED:** Stripe Integration (8h) - unblocks revenue
- ⚠️ **REDUCED:** Blog Generator (12h → 4h MVP) - defer advanced features
- ✅ **KEPT:** Copy Variations (8h) - high ROI for all users

**REVISED Deliverables:**

**Stripe Integration (NEW):**
- ✅ Stripe checkout flow for all pricing tiers
- ✅ Payment success handling
- ✅ Subscription management UI
- ✅ Manual webhook verification (MVP approach)
- ⏳ Full webhook handling deferred if needed

**Blog Generator MVP (REDUCED):**
- ✅ Basic blog generation (1500-2500 words)
- ✅ Simple meta tags (title, description)
- ✅ Export as Markdown/HTML
- ❌ **DEFERRED to Week 8+:** SEO keyword research, keyword density, readability scoring, WordPress/Medium formats, LangGraph workflow

**Copy Variations (KEPT):**
- ✅ 5 copy variations (problem-solution, curiosity, social proof, FOMO, benefit)
- ✅ Tone consistency checker
- ✅ Repetition detector
- ✅ A/B test suggestions
- ✅ 5 copy formulas (PAS, AIDA, 4Ps, BAB, FAB)

**REVISED Success Criteria:**
1. ✅ Users can upgrade from Free → Paid tiers via Stripe
2. ✅ Payment success updates workspace plan_tier immediately
3. ✅ Subscription management works (view, cancel)
4. ✅ Users can generate basic blog posts (MVP quality)
5. ✅ Copy variations offer 5 meaningfully different angles
6. ✅ Quality checks catch tone/repetition issues

**ROI Impact:**
- **Original Plan:** ~8:1 ROI (Blog 12h, Copy 8h)
- **REVISED Plan:** ~28:1 ROI (Stripe 8h, Copy 8h, Blog MVP 4h)
- **Improvement:** 3.5x better ROI by prioritizing revenue enablement

---

## 🚀 Deferred Features

### ✅ Stripe Integration - NO LONGER DEFERRED
**Status:** ✅ **MOVED TO WEEK 7 as Task 7.0** (PRIORITY #1)
**Reason:** Critical for monetization - Week 6 auth is complete but can't collect revenue

### Advanced Blog Features (moved from Week 7 to Week 8+)
**Status:** ⏳ Deferred to Week 8 or later
**Features:**
- SEO keyword research (LLM-based suggestions)
- Keyword density tracking
- Readability scoring (Flesch formula)
- WordPress/Medium export formats
- LangGraph multi-node workflow
- Advanced SEO optimization

**Reason for Deferral:**
Blog MVP (4h) sufficient for Week 7. Advanced features serve only 40% of users (Jessica/Carlos). Can iterate based on user feedback.

### OAuth Integration (4 hours)
**Status:** ⏳ Deferred to Week 8 or later
**Features:**
- Google OAuth (Sign in with Google)
- LinkedIn OAuth (Sign in with LinkedIn)
- Merge accounts flow
- OAuth callback handling

**Reason for Deferral:**
Email/password auth working. OAuth is convenience feature, not blocker.

### Email Service (4 hours)
**Status:** ⏳ Deferred to Week 8 or later
**Features:**
- SendGrid setup
- Welcome email on signup
- Email verification flow
- Password reset email
- Usage reminder emails

**Reason for Deferral:**
Can manually email users for now. Automate when user base grows.

---

## 📋 Testing Checklist

```bash
# 1. Test blog generation
# - Enter topic: "How to use AI for social media"
# - Select target audience: Small business owners
# - Generate blog post
# - Verify: 1500+ words, 5+ H2 headings, readability 60+

# 2. Test SEO features
# - Check meta title (60 chars)
# - Check meta description (160 chars)
# - Check keyword density (2-3%)

# 3. Test export formats
# - Download Markdown
# - Download HTML (verify CSS styling)
# - Download WordPress format (verify meta comments)

# 4. Test copy variations
# - Generate campaign
# - Enable copy variations
# - Verify 5 different angles generated
# - Check each variation is unique

# 5. Test copy quality checks
# - Generate copy with repetitive words
# - Verify repetition detector catches it
# - Check tone consistency for different tones

# 6. Test copy formulas
# - Apply PAS formula
# - Apply AIDA formula
# - Verify structure matches formula
```

---

## 🎯 Business Impact

**Blog & SEO Generator:**
- Enable content marketing channel
- Drive organic traffic (+30% in 6 months)
- Establish thought leadership
- Support SEO strategy

**Copy Variations:**
- Improve conversion rates (+15-20%)
- Enable A/B testing
- Users learn what resonates
- Higher engagement

**Expected Revenue Impact:**
- More features = higher perceived value
- Differentiation from competitors
- Blog feature requested by 40% of beta users
- Supports higher pricing tiers

---

## 📈 Next Steps (Week 8)

After Week 7 completion:

**Week 8 Options:**
1. **Polish & Beta Launch** (from original plan)
   - End-to-end testing
   - Bug fixes
   - Documentation
   - Beta launch materials

2. **Stripe Integration** (monetization priority)
   - Payment processing
   - Subscription management
   - Invoicing

3. **Analytics Dashboard** (if not yet implemented)
   - Campaign performance tracking
   - "Why it worked" explanations

**Decision:** Review with user after Week 7 completion.

---

**Week 7 Status:** Ready to start! 🚀
**Estimated Completion:** 2.5 working days (8h/day)
