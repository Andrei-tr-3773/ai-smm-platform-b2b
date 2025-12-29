# Stripe Setup Guide

This guide explains how to configure Stripe for the AI SMM Platform.

## Prerequisites

- Stripe account (sign up at https://stripe.com)
- Access to Stripe Dashboard

## Step 1: Get Stripe API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy **Secret key** (starts with `sk_test_...`)
3. Copy **Publishable key** (starts with `pk_test_...`)
4. Add to `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
   STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY
   ```

## Step 2: Create Products and Prices

### Option A: Using Stripe Dashboard (Recommended)

1. Go to https://dashboard.stripe.com/test/products
2. Click **+ Add product** for each tier:

#### Starter Plan
- **Name:** Starter Plan
- **Description:** 50 campaigns/month, 3 custom templates, 5 languages
- **Pricing:**
  - Price: $49.00 USD
  - Billing period: Monthly
  - Click **Add pricing**
- **Save product**
- Copy the **Price ID** (starts with `price_...`)
- Add to `.env`: `STRIPE_PRICE_STARTER=price_...`

#### Professional Plan
- **Name:** Professional Plan
- **Description:** 200 campaigns/month, 5 custom templates, 15 languages
- **Pricing:**
  - Price: $99.00 USD
  - Billing period: Monthly
- Copy **Price ID**
- Add to `.env`: `STRIPE_PRICE_PRO=price_...`

#### Team Plan
- **Name:** Team Plan
- **Description:** 500 campaigns/month, 10 custom templates, 5 team members, 15 languages
- **Pricing:**
  - Price: $199.00 USD
  - Billing period: Monthly
- Copy **Price ID**
- Add to `.env`: `STRIPE_PRICE_TEAM=price_...`

#### Agency Plan
- **Name:** Agency Plan
- **Description:** 2000 campaigns/month, 20 custom templates, 10 team members, 15 languages
- **Pricing:**
  - Price: $499.00 USD
  - Billing period: Monthly
- Copy **Price ID**
- Add to `.env`: `STRIPE_PRICE_AGENCY=price_...`

### Option B: Using Stripe CLI

If you prefer to create products via CLI:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Create Starter Plan
stripe products create \
  --name="Starter Plan" \
  --description="50 campaigns/month, 3 custom templates, 5 languages"

stripe prices create \
  --product=<PRODUCT_ID_FROM_ABOVE> \
  --unit-amount=4900 \
  --currency=usd \
  --recurring[interval]=month

# Repeat for Professional, Team, and Agency plans
```

## Step 3: Configure Webhooks (Optional for MVP)

For production, you'll need to handle Stripe webhooks:

1. Go to https://dashboard.stripe.com/test/webhooks
2. Click **+ Add endpoint**
3. **Endpoint URL:** `https://your-domain.com/stripe-webhook` (or use Stripe CLI for local testing)
4. **Events to send:**
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**
6. Copy **Signing secret** (starts with `whsec_...`)
7. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`

### Local Testing with Stripe CLI

```bash
# Forward webhooks to localhost
stripe listen --forward-to localhost:8501/stripe-webhook

# This will output a webhook signing secret
# Add it to .env as STRIPE_WEBHOOK_SECRET
```

## Step 4: Test Payment Flow

1. Start the application: `poetry run streamlit run Home.py`
2. Sign up for an account
3. Go to **Pricing** page
4. Click **Upgrade to Starter**
5. You'll be redirected to Stripe Checkout
6. Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/34)
   - CVC: Any 3 digits (e.g., 123)
   - ZIP: Any 5 digits (e.g., 12345)
7. Complete payment
8. You should be redirected to Success page
9. Check that workspace plan_tier was updated

## Stripe Test Cards

Use these test cards in Test Mode:

| Card Number | Scenario |
|-------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Card declined |
| 4000 0000 0000 9995 | Insufficient funds |
| 4000 0025 0000 3155 | Requires authentication (3D Secure) |

Full list: https://stripe.com/docs/testing

## Production Setup

Before going live:

1. Switch to **Live mode** in Stripe Dashboard
2. Get **live API keys** from https://dashboard.stripe.com/apikeys
3. Create products in **Live mode** (repeat Step 2)
4. Update `.env` with live keys:
   ```env
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_PRICE_STARTER=price_live_...
   STRIPE_PRICE_PRO=price_live_...
   STRIPE_PRICE_TEAM=price_live_...
   STRIPE_PRICE_AGENCY=price_live_...
   ```
5. Set up production webhook endpoint
6. Update `APP_URL` to production domain

## Troubleshooting

### Error: "Invalid API Key"
- Check that `STRIPE_SECRET_KEY` in `.env` matches Stripe Dashboard
- Make sure you're using the correct mode (Test vs Live)

### Error: "No such price"
- Verify `STRIPE_PRICE_*` IDs in `.env` match Stripe Dashboard
- Ensure you created prices in the same mode as your API keys

### Payment succeeds but plan doesn't upgrade
- Check that workspace_id is correctly passed to checkout session
- Verify Success page is calling `workspace_repo.upgrade_plan()`
- Check Streamlit logs for errors

### Webhook not received
- Ensure webhook endpoint is publicly accessible (use ngrok for local testing)
- Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- Check webhook logs in Stripe Dashboard

## Resources

- Stripe Documentation: https://stripe.com/docs
- Stripe API Reference: https://stripe.com/docs/api
- Stripe Testing Guide: https://stripe.com/docs/testing
- Stripe CLI: https://stripe.com/docs/stripe-cli
