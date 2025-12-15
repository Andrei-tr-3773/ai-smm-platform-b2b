import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# OpenAI Pricing (Dec 2024)
PRICING = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,   # $0.150 per 1M tokens
        "output": 0.600 / 1_000_000,  # $0.600 per 1M tokens
    },
    "gpt-4o": {
        "input": 5.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
    "gpt-4o-2024-05-13": {
        "input": 5.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
    "whisper-1": {
        "audio": 0.006 / 60,  # $0.006 per minute
    }
}

class APIUsageTracker:
    def __init__(self, storage_path: str = ".api_usage.json"):
        self.storage_path = Path(storage_path)
        self.usage_data = self._load_usage()

    def _load_usage(self) -> Dict:
        """Load usage from file"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_model": {},
            "by_date": {},
            "requests": []
        }

    def _save_usage(self):
        """Save usage to file"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.usage_data, f, indent=2)

    def track_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ):
        """Track API request"""
        pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
        cost = (
            input_tokens * pricing["input"] +
            output_tokens * pricing["output"]
        )

        # Update totals
        total_tokens = input_tokens + output_tokens
        self.usage_data["total_tokens"] += total_tokens
        self.usage_data["total_cost"] += cost

        # Update by model
        if model not in self.usage_data["by_model"]:
            self.usage_data["by_model"][model] = {
                "tokens": 0,
                "cost": 0.0,
                "requests": 0
            }
        self.usage_data["by_model"][model]["tokens"] += total_tokens
        self.usage_data["by_model"][model]["cost"] += cost
        self.usage_data["by_model"][model]["requests"] += 1

        # Update by date
        date = datetime.now().strftime("%Y-%m-%d")
        if date not in self.usage_data["by_date"]:
            self.usage_data["by_date"][date] = {"tokens": 0, "cost": 0.0, "requests": 0}
        self.usage_data["by_date"][date]["tokens"] += total_tokens
        self.usage_data["by_date"][date]["cost"] += cost
        self.usage_data["by_date"][date]["requests"] += 1

        # Log request
        self.usage_data["requests"].append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "metadata": metadata or {}
        })

        # Limit request history to prevent unbounded growth
        MAX_REQUESTS_HISTORY = 1000
        if len(self.usage_data["requests"]) > MAX_REQUESTS_HISTORY:
            self.usage_data["requests"] = self.usage_data["requests"][-MAX_REQUESTS_HISTORY:]
            logger.info(f"Trimmed request history to {MAX_REQUESTS_HISTORY} most recent requests")

        # Save
        self._save_usage()

        # Warn if approaching limit
        if self.usage_data["total_cost"] > 80:
            logger.warning(f"⚠️  API costs: ${self.usage_data['total_cost']:.2f} (approaching $100 limit!)")

        logger.info(f"💰 API: {total_tokens} tokens, ${cost:.4f} (Total: ${self.usage_data['total_cost']:.2f})")

    def get_summary(self) -> Dict:
        """Get usage summary"""
        return {
            "total_tokens": self.usage_data["total_tokens"],
            "total_cost": round(self.usage_data["total_cost"], 2),
            "by_model": self.usage_data["by_model"],
            "current_month_cost": self._get_current_month_cost()
        }

    def _get_current_month_cost(self) -> float:
        """Get current month cost"""
        current_month = datetime.now().strftime("%Y-%m")
        month_cost = 0.0
        for date, data in self.usage_data["by_date"].items():
            if date.startswith(current_month):
                month_cost += data["cost"]
        return round(month_cost, 2)

# Global tracker
_tracker = None

def get_tracker() -> APIUsageTracker:
    """Get global tracker"""
    global _tracker
    if _tracker is None:
        _tracker = APIUsageTracker()
    return _tracker

def track_openai_request(model: str, response, metadata: Optional[Dict] = None):
    """Track OpenAI request from response"""
    tracker = get_tracker()

    try:
        if hasattr(response, 'usage'):
            usage = response.usage
            tracker.track_request(
                model=model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                metadata=metadata
            )
        elif hasattr(response, 'response_metadata'):
            # LangChain response format
            if 'token_usage' in response.response_metadata:
                usage = response.response_metadata['token_usage']
                tracker.track_request(
                    model=model,
                    input_tokens=usage.get('prompt_tokens', 0),
                    output_tokens=usage.get('completion_tokens', 0),
                    metadata=metadata
                )
            else:
                logger.warning(f"Cannot track usage: response_metadata exists but no token_usage found. Type: {type(response)}")
        else:
            logger.warning(f"Cannot track usage: unknown response format. Type: {type(response)}, Attributes: {dir(response)}")
    except Exception as e:
        logger.error(f"Error tracking API usage: {e}. Response type: {type(response)}")
        # Don't crash the app, just log the error
