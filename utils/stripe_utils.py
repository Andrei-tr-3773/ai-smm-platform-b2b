"""
Stripe utilities for payment processing and subscription management.
"""

import os
import stripe
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Stripe Price IDs for each tier
PRICE_IDS = {
    "starter": os.getenv("STRIPE_PRICE_STARTER"),
    "professional": os.getenv("STRIPE_PRICE_PRO"),
    "team": os.getenv("STRIPE_PRICE_TEAM"),
    "agency": os.getenv("STRIPE_PRICE_AGENCY"),
}

# Plan tier metadata
PLAN_METADATA = {
    "starter": {
        "name": "Starter",
        "price_monthly": 49,
        "campaigns": 50,
        "custom_templates": 3,
        "team_members": 1,
        "languages": 5,
    },
    "professional": {
        "name": "Professional",
        "price_monthly": 99,
        "campaigns": 200,
        "custom_templates": 5,
        "team_members": 1,
        "languages": 15,
    },
    "team": {
        "name": "Team",
        "price_monthly": 199,
        "campaigns": 500,
        "custom_templates": 10,
        "team_members": 5,
        "languages": 15,
    },
    "agency": {
        "name": "Agency",
        "price_monthly": 499,
        "campaigns": 2000,
        "custom_templates": 20,
        "team_members": 10,
        "languages": 15,
    },
}

logger = logging.getLogger(__name__)


def create_checkout_session(
    user_email: str,
    plan_tier: str,
    workspace_id: str,
    success_url: str = None,
    cancel_url: str = None,
) -> stripe.checkout.Session:
    """
    Create Stripe checkout session for subscription.

    Args:
        user_email: Customer email
        plan_tier: Plan tier (starter, professional, team, agency)
        workspace_id: Workspace ID to link subscription
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment cancelled

    Returns:
        Stripe checkout session object

    Raises:
        ValueError: If plan_tier is invalid
        stripe.error.StripeError: If Stripe API call fails
    """
    price_id = PRICE_IDS.get(plan_tier)

    if not price_id:
        raise ValueError(f"Invalid plan tier: {plan_tier}")

    # Default URLs if not provided
    app_url = os.getenv("APP_URL", "http://localhost:8501")
    if not success_url:
        success_url = f"{app_url}/Success?session_id={{CHECKOUT_SESSION_ID}}"
    if not cancel_url:
        cancel_url = f"{app_url}/Pricing"

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user_email,
            metadata={
                "workspace_id": workspace_id,
                "plan_tier": plan_tier,
            },
            subscription_data={
                "metadata": {
                    "workspace_id": workspace_id,
                    "plan_tier": plan_tier,
                }
            },
        )

        logger.info(
            f"Created checkout session {session.id} for workspace {workspace_id}, plan {plan_tier}"
        )

        return session

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        raise


def verify_checkout_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Verify and retrieve checkout session details.

    Args:
        session_id: Stripe checkout session ID

    Returns:
        Dict with session details or None if session not found/invalid
        {
            "payment_status": "paid"|"unpaid",
            "customer_email": str,
            "workspace_id": str,
            "plan_tier": str,
            "subscription_id": str,
            "customer_id": str,
        }
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            "payment_status": session.payment_status,
            "customer_email": session.customer_email,
            "workspace_id": session.metadata.get("workspace_id"),
            "plan_tier": session.metadata.get("plan_tier"),
            "subscription_id": session.subscription,
            "customer_id": session.customer,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Error verifying checkout session {session_id}: {str(e)}")
        return None


def get_subscription(subscription_id: str) -> Optional[stripe.Subscription]:
    """
    Get subscription details by ID.

    Args:
        subscription_id: Stripe subscription ID

    Returns:
        Stripe Subscription object or None if not found
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription

    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving subscription {subscription_id}: {str(e)}")
        return None


def get_customer_subscriptions(customer_id: str) -> list:
    """
    Get all subscriptions for a customer.

    Args:
        customer_id: Stripe customer ID

    Returns:
        List of Stripe Subscription objects
    """
    try:
        subscriptions = stripe.Subscription.list(customer=customer_id)
        return subscriptions.data

    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving customer subscriptions: {str(e)}")
        return []


def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
    """
    Cancel subscription.

    Args:
        subscription_id: Stripe subscription ID
        at_period_end: If True, cancel at end of billing period. If False, cancel immediately.

    Returns:
        True if successful, False otherwise
    """
    try:
        if at_period_end:
            stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )
            logger.info(
                f"Subscription {subscription_id} will cancel at period end"
            )
        else:
            stripe.Subscription.cancel(subscription_id)
            logger.info(f"Subscription {subscription_id} cancelled immediately")

        return True

    except stripe.error.StripeError as e:
        logger.error(f"Error cancelling subscription {subscription_id}: {str(e)}")
        return False


def reactivate_subscription(subscription_id: str) -> bool:
    """
    Reactivate a subscription that was set to cancel at period end.

    Args:
        subscription_id: Stripe subscription ID

    Returns:
        True if successful, False otherwise
    """
    try:
        stripe.Subscription.modify(
            subscription_id, cancel_at_period_end=False
        )
        logger.info(f"Subscription {subscription_id} reactivated")
        return True

    except stripe.error.StripeError as e:
        logger.error(f"Error reactivating subscription {subscription_id}: {str(e)}")
        return False


def change_subscription_plan(
    subscription_id: str, new_plan_tier: str
) -> Optional[stripe.Subscription]:
    """
    Change subscription to a different plan tier.

    Args:
        subscription_id: Stripe subscription ID
        new_plan_tier: New plan tier (starter, professional, team, agency)

    Returns:
        Updated Stripe Subscription object or None if failed
    """
    new_price_id = PRICE_IDS.get(new_plan_tier)

    if not new_price_id:
        logger.error(f"Invalid plan tier: {new_plan_tier}")
        return None

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Update subscription with new price
        updated_subscription = stripe.Subscription.modify(
            subscription_id,
            items=[
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id,
                }
            ],
            metadata={
                "plan_tier": new_plan_tier,
            },
        )

        logger.info(
            f"Subscription {subscription_id} changed to {new_plan_tier}"
        )

        return updated_subscription

    except stripe.error.StripeError as e:
        logger.error(f"Error changing subscription plan: {str(e)}")
        return None


def format_subscription_status(subscription: stripe.Subscription) -> Dict[str, Any]:
    """
    Format subscription details for display.

    Args:
        subscription: Stripe Subscription object

    Returns:
        Dict with formatted subscription info
    """
    from datetime import datetime

    return {
        "status": subscription.status,
        "plan_tier": subscription.metadata.get("plan_tier", "unknown"),
        "current_period_start": datetime.fromtimestamp(
            subscription.current_period_start
        ).strftime("%Y-%m-%d"),
        "current_period_end": datetime.fromtimestamp(
            subscription.current_period_end
        ).strftime("%Y-%m-%d"),
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "amount": subscription.plan.amount / 100,  # Convert cents to dollars
        "currency": subscription.plan.currency.upper(),
        "interval": subscription.plan.interval,
    }
