# Week 5: UX Optimization & Onboarding

**Duration:** 20 hours
**Priority:** CRITICAL
**Business Impact:** Churn 5.5% → 4.5% = +$200k Year 1 revenue
**ROI:** 100:1 ($2,000 → $200,000)

---

## 📊 Business Case

**Current State:**
- Churn: 5.5% monthly → LTV $2,700
- Users abandoning after 3-5 posts
- Confusing UI for new users

**Target State:**
- Churn: 4.5% monthly → LTV $3,600 (+$900/user)
- Users creating 10+ posts (50% less churn)
- Guided wizard for first campaign

**Financial Impact:**
```
Investment: $2,000 (20 hours × $100/hr)
Year 1 Return: $200,000 (720 users × $900 LTV increase)
ROI: 100:1
```

---

## 📅 Week 5 Tasks

### Task 5.1: Getting Started Page (4 hours)

**Goal:** Reduce first-week churn by 30%

**File:** `pages/01_Getting_Started.py`

**Features:**
- Welcome section (30-second pitch)
- Quick Start Guide (5 steps with emojis)
- 3 demo campaigns (click-to-load):
  - 🏋️ Fitness: "Launch 30-day transformation challenge"
  - 💼 SaaS: "Announce new AI feature"
  - 🛍️ E-commerce: "Promote Black Friday sale"
- Video tutorial embed (Loom placeholder)
- Tips & Best Practices panel

**Code Example:**
```python
# pages/01_Getting_Started.py
import streamlit as st

st.set_page_config(page_title="Getting Started", page_icon="🚀")

st.title("🚀 Getting Started")

st.markdown("""
Welcome! Create your first viral campaign in 3 minutes.
""")

# Quick Start Guide
with st.expander("📖 Quick Start Guide", expanded=True):
    st.markdown("""
    **Step 1:** Choose your audience (Audiences tab)
    **Step 2:** Pick platform (Instagram, Facebook, LinkedIn, Telegram)
    **Step 3:** Generate content (use 🔥 Viral Patterns for best results)
    **Step 4:** Translate (optional, 15+ languages)
    **Step 5:** Export & Post (PDF, DOCX, HTML)
    """)

# Demo Campaigns
st.subheader("💡 Try Demo Campaigns")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏋️ Fitness")
    if st.button("Load Fitness Demo"):
        st.session_state['demo'] = 'fitness'
        st.success("✅ Go to 'Create New' tab")

# ... similar for SaaS and E-commerce

# Video Tutorial
st.subheader("🎥 Video Tutorial (3 min)")
st.video("https://www.loom.com/embed/placeholder")

# Tips
with st.expander("💡 Tips & Best Practices"):
    st.markdown("""
    **For Best Results:**
    - ✅ Use viral patterns (2-3x engagement)
    - ✅ Post at optimal times (9-11 AM for Instagram)
    - ✅ Test different hooks (first 3 seconds matter!)

    **Avoid:**
    - ❌ Generic hooks ("Check this out!")
    - ❌ Too many hashtags (max 11 for Instagram)
    - ❌ Same content across all platforms
    """)
```

**Deliverables:**
- [ ] Getting Started page created
- [ ] 3 demo campaigns (JSON files)
- [ ] Navigation updated
- [ ] Tips section complete

---

### Task 5.2: Examples Relayout + Tooltips (3 hours)

**Goal:** +20% feature engagement through better UX

**Files:** `Home.py` (modify)

**Features:**
- Move examples to sidebar expander "💡 Examples"
- Add tooltips (`help=...`) to all major widgets
- Add success messages after actions
- Improve visual hierarchy (icons, spacing)

**Code Example:**
```python
# Sidebar examples
with st.sidebar:
    st.markdown("### 📊 API Usage")
    # ... existing code ...

    # NEW: Examples
    with st.expander("💡 Examples", expanded=False):
        st.markdown("**Fitness:**")
        st.markdown("- Launch 30-day challenge")
        st.markdown("- Promote new class")

        st.markdown("**SaaS:**")
        st.markdown("- Announce new feature")
        st.markdown("- Share success story")

        st.markdown("**E-commerce:**")
        st.markdown("- Black Friday sale")
        st.markdown("- New product launch")

# Add tooltips
user_query = st.text_area(
    "Enter your query here...",
    default_query,
    key='user_query',
    help="💡 Describe what you want to promote. Be specific!"
)

template_name = st.selectbox(
    "Select Content Template",
    template_names,
    key='template_name',
    help="📝 Choose template based on campaign type"
)

selected_platform = st.selectbox(
    "Target Platform",
    options=["None"] + list(platform_options.keys()),
    key='selected_platform',
    help="📱 Choose platform for optimized content (hashtags, timing)"
)

use_viral_patterns = st.checkbox(
    "🔥 Use Viral Patterns",
    value=False,
    key='use_viral_patterns',
    help="🚀 Generate viral content (2-3x more engagement)"
)

# Success messages
if content_generated:
    st.success("✅ Content generated successfully!")
    st.balloons()
```

**Deliverables:**
- [ ] Examples moved to sidebar
- [ ] Tooltips added to 10+ widgets
- [ ] Success messages implemented
- [ ] Icons added to sections

---

### Task 5.3: Campaign Setup Wizard (8 hours)

**Goal:** Guide new users through first campaign (-20% churn)

**File:** `components/campaign_wizard.py` (new)

**Features:**
- 4-step wizard:
  - Step 1: Audience selection
  - Step 2: Platform selection
  - Step 3: Template selection
  - Step 4: Preview + Generate
- Progress indicator (Step X of 4)
- "Skip wizard" option for advanced users
- Integration with Home.py

**Code Example:**
```python
# components/campaign_wizard.py
import streamlit as st

class CampaignWizard:
    def __init__(self):
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 1

    def run(self):
        current_step = st.session_state.wizard_step
        st.progress(current_step / 4)
        st.markdown(f"### Step {current_step} of 4")

        if current_step == 1:
            self._step_1_audience()
        elif current_step == 2:
            self._step_2_platform()
        elif current_step == 3:
            self._step_3_template()
        elif current_step == 4:
            self._step_4_preview()

    def _step_1_audience(self):
        st.markdown("#### 👥 Who is your target audience?")

        # Audience selection
        selected_audience = st.selectbox("Select audience", audience_names)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Skip Wizard"):
                st.session_state.wizard_active = False
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.wizard_step = 2
                st.rerun()

    # ... similar for steps 2, 3, 4
```

**Integration in Home.py:**
```python
# In sidebar
with st.sidebar:
    if st.checkbox("🧙‍♂️ Use Setup Wizard", value=False):
        st.session_state.wizard_active = True

# In main content
if st.session_state.get('wizard_active'):
    wizard = CampaignWizard()
    wizard.run()
else:
    # Regular UI
    ...
```

**Deliverables:**
- [ ] Wizard component created
- [ ] 4 steps implemented
- [ ] Navigation working
- [ ] Integration complete

---

### Task 5.4: Template Selection Improvements (2 hours)

**Goal:** Better template discovery

**Files:** `Home.py` (modify)

**Features:**
- Show template preview on click
- Track "Recently used" templates
- Better template descriptions

**Code Example:**
```python
# Recently used templates
if 'recent_templates' not in st.session_state:
    st.session_state.recent_templates = []

# Show recently used
if st.session_state.recent_templates:
    with st.expander("⏱️ Recently Used"):
        for tmpl in st.session_state.recent_templates[:5]:
            if st.button(f"📄 {tmpl}", key=f"recent_{tmpl}"):
                st.session_state.template_name = tmpl
                st.rerun()

# Template preview
for template in templates:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{template['name']}**")
        st.caption(template.get('example_query', '')[:80])
    with col2:
        if st.button("Preview", key=f"prev_{template['name']}"):
            with st.expander(f"Preview: {template['name']}", expanded=True):
                st.markdown("**Fields:**")
                for item in template.get('items', [])[:5]:
                    st.markdown(f"- {item['name']}")
```

**Deliverables:**
- [ ] Preview implemented
- [ ] Recently used tracked
- [ ] Better descriptions

---

### Task 5.5: Testing & Bug Fixes (3 hours)

**Goal:** Polish and validate

**Checklist:**
- [ ] Test Getting Started page
- [ ] Test all wizard flows
- [ ] Test examples in sidebar
- [ ] Test tooltips
- [ ] Test demo campaigns
- [ ] Test recently used templates
- [ ] Fix any bugs
- [ ] User testing (internal - 3 scenarios)

**User Testing Scenarios:**
1. New user completes wizard
2. Power user skips wizard, uses viral patterns
3. User loads demo, translates to 3 languages

---

## 📦 Deliverables Summary

### Files Created
- [ ] `pages/01_Getting_Started.py`
- [ ] `components/campaign_wizard.py`
- [ ] `demo_campaigns/fitness_demo.json`
- [ ] `demo_campaigns/saas_demo.json`
- [ ] `demo_campaigns/ecommerce_demo.json`

### Files Modified
- [ ] `Home.py` (tooltips, examples, wizard integration)
- [ ] `CLAUDE.md` (update with Week 5 info)

### Features Delivered
- [ ] Getting Started page (reduces churn 30%)
- [ ] Campaign wizard (4 steps)
- [ ] Examples in sidebar
- [ ] Tooltips on all widgets
- [ ] Success messages
- [ ] Template preview
- [ ] Recently used templates

---

## 🧪 Testing Plan

**Manual Testing:**
- [ ] Getting Started loads correctly
- [ ] Demo campaigns work
- [ ] Wizard completes successfully
- [ ] Skip wizard works
- [ ] Examples clickable
- [ ] Tooltips appear
- [ ] Preview shows template info
- [ ] Recently used updates

**User Testing (Internal):**
- [ ] Alex (Fitness) - Complete wizard
- [ ] Jessica (SaaS) - Use viral patterns
- [ ] Carlos (Agency) - Translate campaign

---

## 🚀 Deployment

```bash
# 1. Create branch
git checkout -b feature/week_5

# 2. Commit changes
git add .
git commit -m "Week 5: UX optimization and onboarding"

# 3. Merge to main
git checkout main
git merge feature/week_5 --no-edit
git push origin main

# 4. Deploy to server
ssh semeniukandrei@34.165.201.76
cd ~/projects/ai-smm-platform-b2b
git pull origin main
pkill -f 'streamlit run' || true
export PATH="$HOME/.local/bin:$PATH"
nohup poetry run streamlit run Home.py --server.port=8501 --server.headless=true > streamlit.log 2>&1 &
exit

# 5. Verify
curl http://34.165.201.76:8501
```

---

## 💰 Expected ROI

**Investment:** $2,000 (20 hours)
**Year 1 Return:** $200,000
**ROI:** 100:1

**Churn Impact:**
- Before: 5.5% → LTV $2,700
- After: 4.5% → LTV $3,600
- Gain: +$900 per user

**Year 1 (720 users):**
- Additional LTV: $648,000
- Realized revenue: ~$200,000

---

## 📝 Notes

**No Color Theme Changes:**
- User will handle UI polish separately
- Focus on functionality, not aesthetics
- Keep existing Streamlit default theme

**Deferred to Week 7:**
- Bulk campaign generation
- Calendar view
- Advanced filters

---

**Status:** ⏳ Ready to start
**Branch:** `feature/week_5`
**Start Date:** TBD
