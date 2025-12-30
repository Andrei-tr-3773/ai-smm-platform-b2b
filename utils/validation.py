"""
Input validation and sanitization utilities.

Week 8: Task 8.1.2c - Security audit
Prevents injection attacks, validates user input, sanitizes data.
"""

import re
from typing import Optional, Any
from urllib.parse import urlparse
import html
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False

    # RFC 5322 compliant regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_workspace_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate workspace name.

    Args:
        name: Workspace name to validate

    Returns:
        Tuple of (is_valid, error_message)

    Rules:
        - 3-50 characters
        - Alphanumeric, spaces, hyphens, underscores only
        - Cannot start/end with space
    """
    if not name or not isinstance(name, str):
        return (False, "Workspace name is required")

    name = name.strip()

    if len(name) < 3:
        return (False, "Workspace name must be at least 3 characters")

    if len(name) > 50:
        return (False, "Workspace name must be less than 50 characters")

    # Allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return (False, "Workspace name can only contain letters, numbers, spaces, hyphens, and underscores")

    return (True, None)


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks.

    Args:
        text: Text that may contain HTML

    Returns:
        HTML-escaped text

    Examples:
        >>> sanitize_html("<script>alert('XSS')</script>")
        "&lt;script&gt;alert('XSS')&lt;/script&gt;"
    """
    if not text or not isinstance(text, str):
        return ""

    return html.escape(text)


def sanitize_mongodb_query(query: dict) -> dict:
    """
    Sanitize MongoDB query to prevent NoSQL injection.

    Args:
        query: MongoDB query dict

    Returns:
        Sanitized query dict

    Prevents:
        - $where operator (allows arbitrary JavaScript)
        - $regex with user input (ReDoS attack)
        - Injection via field names starting with $

    Examples:
        >>> sanitize_mongodb_query({"email": "user@example.com"})
        {"email": "user@example.com"}
        >>> sanitize_mongodb_query({"$where": "this.password == 'test'"})
        {}  # $where removed
    """
    if not isinstance(query, dict):
        logger.warning("Invalid MongoDB query type (expected dict)")
        return {}

    sanitized = {}

    for key, value in query.items():
        # Remove dangerous operators
        if key.startswith('$'):
            if key in ['$eq', '$ne', '$gt', '$gte', '$lt', '$lte', '$in', '$nin']:
                # Safe comparison operators
                sanitized[key] = value
            elif key == '$and' or key == '$or':
                # Recursively sanitize nested queries
                if isinstance(value, list):
                    sanitized[key] = [sanitize_mongodb_query(v) if isinstance(v, dict) else v for v in value]
            else:
                # Dangerous operators: $where, $expr, $function, etc.
                logger.warning(f"Blocked dangerous MongoDB operator: {key}")
                continue
        else:
            # Regular field - recursively sanitize if dict
            if isinstance(value, dict):
                sanitized[key] = sanitize_mongodb_query(value)
            else:
                sanitized[key] = value

    return sanitized


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid URL, False otherwise

    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not a url")
        False
    """
    if not url or not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def validate_language_code(lang_code: str) -> bool:
    """
    Validate language code format (ISO 639-1 with optional region).

    Args:
        lang_code: Language code (e.g., "en", "en-US", "uk-UA")

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_language_code("en-US")
        True
        >>> validate_language_code("invalid")
        False
    """
    if not lang_code or not isinstance(lang_code, str):
        return False

    # ISO 639-1 language code (2 letters) + optional region (2 letters)
    pattern = r'^[a-z]{2}(-[A-Z]{2})?$'
    return re.match(pattern, lang_code) is not None


def validate_plan_tier(tier: str) -> bool:
    """
    Validate plan tier value.

    Args:
        tier: Plan tier name

    Returns:
        True if valid tier, False otherwise
    """
    valid_tiers = ['free', 'starter', 'professional', 'team', 'agency', 'enterprise']
    return tier in valid_tiers


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Safe filename (only alphanumeric, dots, hyphens, underscores)

    Examples:
        >>> sanitize_filename("../../etc/passwd")
        "etcpasswd"
        >>> sanitize_filename("report_2024.pdf")
        "report_2024.pdf"
    """
    if not filename or not isinstance(filename, str):
        return "unnamed_file"

    # Remove directory separators
    filename = filename.replace('/', '').replace('\\', '')

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Keep only safe characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

    # Ensure not empty after sanitization
    if not filename:
        return "unnamed_file"

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename


def validate_json_structure(data: dict, required_fields: list[str]) -> tuple[bool, Optional[str]]:
    """
    Validate JSON structure has required fields.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_json_structure({"name": "Test", "email": "test@example.com"}, ["name", "email"])
        (True, None)
        >>> validate_json_structure({"name": "Test"}, ["name", "email"])
        (False, "Missing required field: email")
    """
    if not isinstance(data, dict):
        return (False, "Data must be a dictionary")

    for field in required_fields:
        if field not in data:
            return (False, f"Missing required field: {field}")

    return (True, None)


def validate_campaign_content(content: dict) -> tuple[bool, Optional[str]]:
    """
    Validate campaign content structure.

    Args:
        content: Campaign content dict

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['platform', 'items']

    is_valid, error = validate_json_structure(content, required_fields)
    if not is_valid:
        return (False, error)

    # Validate platform
    valid_platforms = ['instagram', 'facebook', 'telegram', 'linkedin']
    if content['platform'] not in valid_platforms:
        return (False, f"Invalid platform: {content['platform']}")

    # Validate items is a list
    if not isinstance(content['items'], list):
        return (False, "items must be a list")

    return (True, None)


def validate_integer_range(value: Any, min_val: int, max_val: int, field_name: str = "Value") -> tuple[bool, Optional[str]]:
    """
    Validate integer is within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Name of field (for error messages)

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_integer_range(5, 1, 10, "Age")
        (True, None)
        >>> validate_integer_range(15, 1, 10, "Age")
        (False, "Age must be between 1 and 10")
    """
    try:
        value_int = int(value)
    except (ValueError, TypeError):
        return (False, f"{field_name} must be an integer")

    if value_int < min_val or value_int > max_val:
        return (False, f"{field_name} must be between {min_val} and {max_val}")

    return (True, None)


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    General-purpose sanitization for user text input.

    Args:
        text: User input text
        max_length: Maximum allowed length (default 1000)

    Returns:
        Sanitized text

    Applies:
        - Trim whitespace
        - Limit length
        - Escape HTML
        - Remove control characters
    """
    if not text or not isinstance(text, str):
        return ""

    # Trim whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    # Remove control characters (except newline, tab)
    text = ''.join(char for char in text if char.isprintable() or char in ['\n', '\t'])

    # Escape HTML
    text = html.escape(text)

    return text


def validate_mongodb_objectid(object_id: str) -> bool:
    """
    Validate MongoDB ObjectId format.

    Args:
        object_id: ObjectId string

    Returns:
        True if valid ObjectId format, False otherwise

    Examples:
        >>> validate_mongodb_objectid("507f1f77bcf86cd799439011")
        True
        >>> validate_mongodb_objectid("invalid")
        False
    """
    if not object_id or not isinstance(object_id, str):
        return False

    # MongoDB ObjectId is 24 hex characters
    pattern = r'^[0-9a-fA-F]{24}$'
    return re.match(pattern, object_id) is not None


# Example usage in repository methods:
"""
from utils.validation import sanitize_mongodb_query, validate_email, sanitize_user_input

def get_user_by_email(email: str):
    # Validate email
    if not validate_email(email):
        raise ValueError("Invalid email format")

    # Sanitize query
    query = sanitize_mongodb_query({"email": email})

    # Execute safe query
    return db.users.find_one(query)

def create_campaign(campaign_text: str):
    # Sanitize user input
    safe_text = sanitize_user_input(campaign_text, max_length=5000)

    # Save to database
    db.campaigns.insert_one({"text": safe_text})
"""
