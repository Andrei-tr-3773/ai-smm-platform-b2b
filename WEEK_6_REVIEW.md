# Week 6 Plan Review - Tech Lead & Business Architect

**Date:** 2025-12-23
**Reviewers:** Tech Lead + Business Architect
**Plan:** WEEK_6_TASKS.md
**Status:** ⚠️ **CRITICAL ISSUES FOUND** - Requires immediate correction

---

## 🚨 CRITICAL ISSUES

### Issue #1: **PRICING MISMATCH** (BLOCKER)

**Problem:** Week 6 pricing does NOT match Financial Model

| Tier | Week 6 Price | Financial Model Price | Discrepancy |
|------|--------------|---------------------|-------------|
| Free | $0 | $0 | ✅ Match |
| Starter | $49 | $49 | ✅ Match |
| Professional | **$99** | $99 | ✅ Match |
| Team | $199 | $199 | ✅ Match |
| Agency | **$299** | **$499** | ❌ **$200 OFF!** |
| Enterprise | $999 | $999+ | ✅ Match |

**Impact:**
- ❌ **Revenue Loss**: $200/month per agency customer
- ❌ **Financial Model Broken**: ARPU calculations wrong
- ❌ **Year 1 Revenue**: -$36,000 (15 agency customers × $200 × 12 months)

**Fix:** Change Agency tier from $299 → $499

**Business Architect Note:**
> "Agency tier at $299 destroys our unit economics. Financial model assumes $499 based on competitor analysis (Hootsuite $99-$739, Later $40-$80 per profile). We CANNOT go below $499 for agency tier without losing profitability."

---

### Issue #2: **PLAN TIERS NAMING INCONSISTENCY**

**Problem:** Different plan names across documents

| Document | Tier Names |
|----------|------------|
| **Week 6** | Free, **Starter**, Professional, **Team**, Agency, Enterprise |
| **Financial Model** | Free, **Starter**, Professional, **Team**, Agency, Enterprise |
| **Multi-Tenancy Design** | Free, Professional, **Business**, Agency, Enterprise |

**Impact:**
- Confusion in codebase (which tier name to use?)
- Database schema mismatch
- Pricing page inconsistency

**Decision:**
Use **Financial Model tiers** as source of truth:
- ✅ Free ($0)
- ✅ Starter ($49)
- ✅ Professional ($99)
- ✅ Team ($199)
- ✅ Agency ($499)
- ✅ Enterprise ($999+)

Drop "Business" tier name from Multi-Tenancy Design.

---

### Issue #3: **FEATURE LIMITS MISMATCH**

**Problem:** Campaign limits differ across documents

| Tier | Week 6 Limits | Multi-Tenancy Limits | Financial Model |
|------|---------------|---------------------|-----------------|
| **Free** | 10 campaigns, 0 templates | 10 campaigns, 1 template | 10 campaigns |
| **Starter** | N/A in code! | N/A! | **50 campaigns** |
| **Professional** | **100 campaigns**, 5 templates | **200 campaigns**, 5 templates | **200 campaigns** |
| **Team** | Unlimited, Unlimited | Unlimited, 20 templates | Unlimited |
| **Agency** | Unlimited, Unlimited | Unlimited, **50 templates** | Unlimited |

**Impact:**
- Users on Professional tier get HALF the campaigns they should (100 vs 200)
- Starter tier completely missing from Week 6!
- Template limits inconsistent

**Fix:**
Use **Multi-Tenancy Design** as source of truth:
- Free: 10 campaigns/month, 1 custom template, 1 user, 3 languages
- Starter: 50 campaigns/month, 3 custom templates, 1 user, 5 languages
- Professional: 200 campaigns/month, 5 custom templates, 1 user, 15 languages
- Team: Unlimited campaigns, 20 custom templates, 3 users, 15 languages
- Agency: Unlimited campaigns, 50 custom templates, 10 users, 15 languages
- Enterprise: Unlimited everything

**Business Architect Note:**
> "Professional tier at 100 campaigns/month is not competitive. Jasper offers 'unlimited' at $99. We need 200 to justify pricing."

---

## ⚠️ TECH LEAD CONCERNS

### Concern #1: **Password Security Insufficient**

**Current:** Password validation only checks:
- Minimum 8 characters
- 1 uppercase letter
- 1 number

**Problem:**
- 8 characters is TOO WEAK (industry standard: 12+)
- No special character requirement
- No check for common passwords (password123, etc.)
- No password strength meter

**Fix Required:**
```python
# Minimum requirements for Week 6:
- 12 characters minimum (not 8)
- 1 uppercase, 1 lowercase, 1 number, 1 special char
- Not in common password list (use zxcvbn library)
- Password strength meter in UI
```

**Security Impact:** Medium-High (accounts vulnerable to brute force)

---

### Concern #2: **Missing Rate Limiting**

**Current:** No rate limiting on:
- Login attempts
- Signup requests
- Password reset (when implemented)

**Problem:**
- Vulnerable to brute force attacks
- Vulnerable to spam signups
- No DDoS protection

**Fix Required:**
```python
# Add rate limiting:
- Login: 5 attempts per 15 minutes per IP
- Signup: 3 signups per hour per IP
- API calls: 100 requests per hour per user (when API added)
```

**Tool:** Use `slowapi` library (FastAPI) or `Flask-Limiter`

**Security Impact:** High (critical for production)

---

### Concern #3: **Database Indices Missing**

**Current:** Week 6 doesn't mention creating database indices

**Problem:**
- Queries on `workspace_id`, `email`, `user_id` will be SLOW
- Performance degrades as user base grows
- MongoDB full table scans = expensive

**Fix Required:**
```python
# Required indices for Week 6:
db.users.create_index("email", unique=True)
db.users.create_index("workspace_id")
db.workspaces.create_index("owner_user_id")
db.campaigns.create_index("workspace_id")
db.campaigns.create_index([("workspace_id", 1), ("created_at", -1)])  # For sorting
db.content_templates.create_index([("workspace_id", 1), ("is_shared", 1)])
```

**Performance Impact:** High (100x faster queries with indices)

---

### Concern #4: **No Refresh Token Strategy**

**Current:** JWT tokens expire after 7 days, then user must re-login

**Problem:**
- Poor UX (user forced to login every week)
- No way to revoke tokens (if account compromised)
- Cannot logout user from all devices

**Better Approach:**
```python
# Access token: 15 minutes (short-lived)
# Refresh token: 30 days (stored in httpOnly cookie)
# On access token expiry, use refresh token to get new access token
# Revoke refresh tokens on logout
```

**Defer to:** Week 7 (acceptable for MVP, but add to roadmap)

---

## 📊 BUSINESS ARCHITECT CONCERNS

### Concern #1: **No Conversion Tracking**

**Current:** Week 6 tracks usage limits but NOT conversion metrics

**Problem:**
- Can't measure Free → Paid conversion rate
- Can't identify high-value users
- Can't optimize pricing tiers
- No A/B testing capability

**Fix Required:**
```python
# Add analytics events:
- user_signed_up (tier: free)
- user_created_campaign (count: 1, tier: free)
- user_hit_limit (limit_type: campaigns, tier: free)
- user_viewed_pricing (referrer: limit_modal)
- user_upgraded (from_tier: free, to_tier: professional)
```

**Tool:** Use Mixpanel or Amplitude (Week 7)

**Business Impact:** High (can't optimize without data)

---

### Concern #2: **Freemium Limits Too Generous?**

**Current:** Free tier gets:
- 10 campaigns/month
- 3 languages

**Problem:**
- Financial Model assumes 55% conversion (Free → Paid)
- Industry standard: 2-5%
- If limits too generous, users won't upgrade

**Question for Validation:**
- Is 10 campaigns/month enough for small business to never upgrade?
- Should we reduce to 5 campaigns/month?

**Recommendation:**
```
Option A (Current): 10 campaigns/month → Expect 10-15% conversion
Option B (Stricter): 5 campaigns/month → Expect 20-30% conversion
Option C (Time-based): 14-day trial unlimited, then 5/month → Expect 30-40% conversion

Recommend: Option C for highest conversion
```

**Test:** Run A/B test in Month 3-4

---

### Concern #3: **No Onboarding Email Automation**

**Current:** Week 6 only implements signup, no post-signup flow

**Problem:**
- Business Model Canvas says "Personal outreach in first 7 days reduces churn 30%"
- Week 6 has NO email automation
- Users sign up and get... nothing

**Missing:**
- Welcome email (immediate)
- Day 1: "Create your first campaign" tutorial
- Day 3: "Here are 3 example campaigns"
- Day 7: "You've used 3/10 campaigns - upgrade?"

**Fix:** Add to Week 7 (use SendGrid + Drip campaign)

**Business Impact:** Medium-High (30% churn reduction = $200k Year 1)

---

### Concern #4: **Stripe Integration Deferred**

**Current:** Week 6 only shows pricing page, actual payment in Week 7

**Problem:**
- Can't accept money for 1 more week
- Early adopters who want to pay can't
- Momentum loss

**Risk:**
If user wants to upgrade TODAY but can't, they may:
- Forget to come back
- Find competitor
- Lose urgency

**Mitigation Options:**
1. **Accelerate Stripe to Week 6** (add 6h) ← RECOMMENDED
2. **Collect emails** for "notify me when paid plans launch"
3. **Manual invoicing** for first 10 customers (stopgap)

**Recommendation:** Add Stripe integration to Week 6 (extend to 30h total)

**Business Architect Verdict:**
> "Delaying revenue by 1 week when we're building a revenue-generating platform is risky. Add Stripe to Week 6 or at minimum collect pre-orders."

---

## ✅ WHAT'S GOOD ABOUT WEEK 6

**Tech Lead Approves:**
- ✅ bcrypt for password hashing (industry standard)
- ✅ JWT for sessions (stateless, scalable)
- ✅ Workspace multi-tenancy architecture (clean design)
- ✅ Repository pattern for data isolation (best practice)
- ✅ Role-based access control (owner/admin/member)

**Business Architect Approves:**
- ✅ Pricing page with clear tiers (good UX)
- ✅ Usage tracking (campaigns, templates, team members)
- ✅ Upgrade prompts when limits hit (conversion optimization)
- ✅ Team management UI (supports collaboration)

---

## 📋 REQUIRED CHANGES (Before Week 6 Start)

### HIGH PRIORITY (Blockers)

1. **Fix Agency Pricing: $299 → $499** ✅ CRITICAL
   - File: `WEEK_6_TASKS.md` lines 101-107, 281-283, 388-395

2. **Fix Professional Campaign Limit: 100 → 200** ✅ CRITICAL
   - File: `WEEK_6_TASKS.md` lines 103, 183-195

3. **Add Starter Tier** (missing entirely!)
   - 50 campaigns/month, 3 custom templates, $49/month
   - Files: All pricing tables, Workspace.get_plan_limits()

4. **Add Database Indices** ✅ HIGH
   - Add Task 6.5: "Create Database Indices" (2h)

5. **Add Rate Limiting** ✅ HIGH
   - Add Task 6.6: "Add Rate Limiting" (2h)

### MEDIUM PRIORITY (Important, not blockers)

6. **Strengthen Password Requirements**
   - 8 chars → 12 chars minimum
   - Add special character requirement

7. **Add Conversion Analytics Events**
   - Track signup, upgrade, churn events

8. **Add Onboarding Email Plan**
   - Define email sequence for Week 7

### OPTIONAL (Nice to have)

9. **Consider Adding Stripe to Week 6**
   - Adds 6h, but enables immediate revenue

10. **A/B Test Free Tier Limits**
    - 5 vs 10 campaigns/month (Month 3)

---

## 📊 CORRECTED PLAN TIERS (Source of Truth)

| Tier | Price/Month | Campaigns | Templates | Users | Languages | Analytics |
|------|-------------|-----------|-----------|-------|-----------|-----------|
| **Free** | $0 | 10 | 1 | 1 | 3 | Basic |
| **Starter** | **$49** | **50** | **3** | 1 | 5 | Basic |
| **Professional** | $99 | **200** | 5 | 1 | 15 | Advanced |
| **Team** | $199 | Unlimited | 20 | **3** | 15 | Advanced |
| **Agency** | **$499** | Unlimited | 50 | **10** | 15 | Advanced + API |
| **Enterprise** | $999+ | Unlimited | Unlimited | Unlimited | 15 | Advanced + API + SLA |

---

## 🎯 UPDATED FINANCIAL IMPACT

**Original Week 6 Projection** (with $299 agency tier):
- Month 12: 15 agency customers × $299 = $4,485 MRR
- Year 1 Revenue: $53,820

**Corrected Week 6 Projection** (with $499 agency tier):
- Month 12: 15 agency customers × $499 = $7,485 MRR
- Year 1 Revenue: **$89,820**

**Difference:** +$36,000 Year 1 revenue 💰

---

## ✅ ACTION ITEMS

**Before Starting Week 6:**
1. [ ] Update WEEK_6_TASKS.md with corrected pricing ($499 agency)
2. [ ] Add Starter tier to all code examples
3. [ ] Fix campaign limits (Professional: 200, Starter: 50)
4. [ ] Add Task 6.5: Database Indices (2h)
5. [ ] Add Task 6.6: Rate Limiting (2h)
6. [ ] Update password requirements (12 chars min)
7. [ ] Add indices creation script
8. [ ] Document required environment variables

**Total Time Adjustment:**
- Original: 24h
- Add indices: +2h
- Add rate limiting: +2h
- **New Total: 28 hours**

---

## 🟢 APPROVAL STATUS

**Tech Lead:** ✅ APPROVED (with changes above)
**Business Architect:** ✅ APPROVED (with pricing corrections)
**Overall:** ⚠️ **CONDITIONALLY APPROVED** - Must fix pricing before Week 6 start

**Signature:** Tech Lead & Business Architect Review
**Date:** 2025-12-23
