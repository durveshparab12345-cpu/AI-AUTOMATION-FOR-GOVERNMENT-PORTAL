"""
Reusable validation functions.

This module provides common validation functions used across the application
for validating inputs, ensuring data consistency, and enforcing business rules.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement email validation with proper regex or library
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement phone validation (support multiple formats)
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.

    Args:
        date_str: Date string to validate
        format: Expected date format

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_id_format(id_str: str) -> bool:
    """
    Validate ID format (UUID v4).

    Args:
        id_str: ID string to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    # TODO: Validate UUID v4 format
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return re.match(uuid_pattern, id_str, re.IGNORECASE) is not None


def validate_case_id(case_id: str) -> bool:
    """
    Validate case ID format.

    Args:
        case_id: Case ID to validate

    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement PMJAY-specific case ID validation
    # Example format: CASE-2024-00001
    pattern = r'^CASE-\d{4}-\d{5}$'
    return re.match(pattern, case_id) is not None


def validate_policy_number(policy_number: str) -> bool:
    """
    Validate insurance policy number format.

    Args:
        policy_number: Policy number to validate

    Returns:
        True if valid, False otherwise
    """
    # TODO: Implement policy number validation
    # Support multiple formats from different insurers
    return len(policy_number) >= 6


def validate_aadhar_number(aadhar: str) -> bool:
    """
    Validate Aadhaar number format (India).

    Args:
        aadhar: Aadhaar number to validate

    Returns:
        True if valid, False otherwise
    """
    # Aadhaar is 12 digits
    pattern = r'^\d{12}$'
    return re.match(pattern, aadhar) is not None


def validate_pan_number(pan: str) -> bool:
    """
    Validate PAN number format (India).

    Args:
        pan: PAN number to validate

    Returns:
        True if valid, False otherwise
    """
    # PAN format: AAAAA9999A
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return re.match(pattern, pan) is not None


def validate_ifsc_code(ifsc: str) -> bool:
    """
    Validate IFSC code format (India).

    Args:
        ifsc: IFSC code to validate

    Returns:
        True if valid, False otherwise
    """
    # IFSC format: AAAA0123456
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return re.match(pattern, ifsc) is not None


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$'
    return re.match(pattern, url) is not None


def validate_status_enum(status: str, valid_statuses: List[str]) -> bool:
    """
    Validate that status is in allowed values.

    Args:
        status: Status value to validate
        valid_statuses: List of valid status values

    Returns:
        True if status is valid, False otherwise
    """
    return status in valid_statuses


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    allow_same_day: bool = False,
) -> bool:
    """
    Validate date range.

    Args:
        start_date: Start date
        end_date: End date
        allow_same_day: If True, start and end can be same day

    Returns:
        True if range is valid, False otherwise
    """
    if allow_same_day:
        return start_date <= end_date
    else:
        return start_date < end_date


def validate_numeric_range(
    value: float,
    min_value: float = None,
    max_value: float = None,
) -> bool:
    """
    Validate numeric value is within range.

    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        True if value is within range, False otherwise
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that required fields are present and non-empty.

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        True if all required fields present, False otherwise
    """
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True


def validate_no_duplicates(items: List[Any]) -> bool:
    """
    Validate that list has no duplicate values.

    Args:
        items: List to check for duplicates

    Returns:
        True if no duplicates, False otherwise
    """
    return len(items) == len(set(items))


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    # TODO: Implement string sanitization
    # - Remove/escape dangerous characters
    # - Strip whitespace
    # - Enforce max length
    return value.strip()[:max_length]
