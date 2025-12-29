"""
Stripe webhook handler for subscription events.

NOTE: Streamlit doesn't natively support webhook endpoints.
For production, deploy this as a separate FastAPI/Flask service or use Stripe CLI for testing.

Week 7 MVP Approach:
- Use manual verification on Success page (checkout session verification)
- This file provides structure for future production webhooks
"""

import os
import stripe
from dotenv import load_dotenv
from repositories.workspace_repository import WorkspaceRepository
import logging

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

logger = logging.getLogger(__name__)


def handle_webhook_event(payload: bytes, sig_header: str) -> dict:
    """
    Process Stripe webhook event.

    Args:
        payload: Raw request body from Stripe
        sig_header: Stripe signature header (HTTP_STRIPE_SIGNATURE)

    Returns:
        dict with status and message

    Example (FastAPI):
        @app.post("/stripe-webhook")
        async def stripe_webhook(request: Request):
            payload = await request.body()
            sig_header = request.headers.get("stripe-signature")
            return handle_webhook_event(payload, sig_header)
    """
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )

    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {str(e)}")
        return {"status": "error", "message": "Invalid payload"}

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {str(e)}")
        return {"status": "error", "message": "Invalid signature"}

    # Handle the event
    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Received Stripe webhook: {event_type}")

    # Route to specific handler
    if event_type == "checkout.session.completed":
        return handle_checkout_completed(event_data)

    elif event_type == "customer.subscription.created":
        return handle_subscription_created(event_data)

    elif event_type == "customer.subscription.updated":
        return handle_subscription_updated(event_data)

    elif event_type == "customer.subscription.deleted":
        return handle_subscription_deleted(event_data)

    elif event_type == "invoice.payment_succeeded":
        return handle_payment_succeeded(event_data)

    elif event_type == "invoice.payment_failed":
        return handle_payment_failed(event_data)

    else:
        logger.info(f"Unhandled event type: {event_type}")
        return {"status": "ignored", "message": f"Event {event_type} not handled"}


def handle_checkout_completed(session: dict) -> dict:
    """
    Handle successful checkout session.

    This is also handled on the Success page (manual verification),
    but webhooks provide a backup in case user closes browser.
    """
    workspace_id = session["metadata"].get("workspace_id")
    plan_tier = session["metadata"].get("plan_tier")
    subscription_id = session.get("subscription")
    customer_id = session.get("customer")

    if not workspace_id or not plan_tier:
        logger.error("Checkout session missing metadata")
        return {"status": "error", "message": "Missing metadata"}

    try:
        workspace_repo = WorkspaceRepository()

        # Check if already upgraded (to avoid duplicate processing)
        workspace = workspace_repo.get_workspace(workspace_id)
        if workspace and workspace.plan_tier == plan_tier:
            logger.info(f"Workspace {workspace_id} already upgraded to {plan_tier}")
            return {"status": "ok", "message": "Already processed"}

        # Upgrade workspace
        workspace_repo.upgrade_plan(
            workspace_id=workspace_id,
            new_tier=plan_tier,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
        )

        logger.info(f"Webhook: Upgraded workspace {workspace_id} to {plan_tier}")

        return {"status": "ok", "message": "Workspace upgraded"}

    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}")
        return {"status": "error", "message": str(e)}


def handle_subscription_created(subscription: dict) -> dict:
    """Handle new subscription created."""
    customer_id = subscription.get("customer")
    plan_tier = subscription["metadata"].get("plan_tier")

    logger.info(f"Subscription created for customer {customer_id}: {plan_tier}")

    # Subscription already handled in checkout.session.completed
    return {"status": "ok", "message": "Subscription created"}


def handle_subscription_updated(subscription: dict) -> dict:
    """
    Handle subscription update (plan change, cancel scheduled, etc).
    """
    workspace_id = subscription["metadata"].get("workspace_id")
    subscription_id = subscription["id"]
    status = subscription["status"]

    if not workspace_id:
        logger.warning("Subscription missing workspace_id in metadata")
        return {"status": "error", "message": "Missing workspace_id"}

    try:
        workspace_repo = WorkspaceRepository()

        # Update subscription status
        workspace_repo.collection.update_one(
            {"_id": workspace_id},
            {"$set": {
                "subscription_status": status,
                "stripe_subscription_id": subscription_id,
            }}
        )

        logger.info(f"Updated subscription status: {workspace_id} -> {status}")

        return {"status": "ok", "message": "Subscription updated"}

    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")
        return {"status": "error", "message": str(e)}


def handle_subscription_deleted(subscription: dict) -> dict:
    """
    Handle subscription cancellation.
    Downgrade workspace to free plan.
    """
    workspace_id = subscription["metadata"].get("workspace_id")

    if not workspace_id:
        logger.warning("Subscription missing workspace_id in metadata")
        return {"status": "error", "message": "Missing workspace_id"}

    try:
        workspace_repo = WorkspaceRepository()

        # Downgrade to free plan
        workspace_repo.upgrade_plan(
            workspace_id=workspace_id,
            new_tier="free",
            stripe_subscription_id=None,
        )

        logger.info(f"Subscription cancelled: downgraded {workspace_id} to free")

        return {"status": "ok", "message": "Subscription cancelled"}

    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")
        return {"status": "error", "message": str(e)}


def handle_payment_succeeded(invoice: dict) -> dict:
    """Handle successful payment for subscription renewal."""
    customer_id = invoice.get("customer")
    amount_paid = invoice.get("amount_paid") / 100  # Convert cents to dollars

    logger.info(f"Payment succeeded: {customer_id} paid ${amount_paid}")

    # Payment success doesn't require action (subscription is already active)
    # Could send "thank you" email here

    return {"status": "ok", "message": "Payment recorded"}


def handle_payment_failed(invoice: dict) -> dict:
    """
    Handle failed payment.
    Send email notification to customer.
    """
    customer_id = invoice.get("customer")
    amount_due = invoice.get("amount_due") / 100

    logger.warning(f"Payment failed: {customer_id} owes ${amount_due}")

    # TODO: Send email notification
    # TODO: Update subscription status to "past_due"

    return {"status": "ok", "message": "Payment failure recorded"}


# FastAPI Example (for production deployment)
"""
from fastapi import FastAPI, Request, HTTPException
import uvicorn

app = FastAPI()

@app.post("/stripe-webhook")
async def stripe_webhook_endpoint(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    result = handle_webhook_event(payload, sig_header)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return {"received": True, **result}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# Flask Example (alternative)
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook_endpoint():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    if not sig_header:
        return jsonify({"error": "Missing signature"}), 400

    result = handle_webhook_event(payload, sig_header)

    if result["status"] == "error":
        return jsonify(result), 400

    return jsonify({"received": True, **result}), 200

if __name__ == '__main__':
    app.run(port=8000)
"""
