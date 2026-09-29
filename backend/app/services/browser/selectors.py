"""
Selector constants for known portal elements.

Centralising selectors here means that when a portal changes its DOM,
only this file needs updating — not every action throughout the codebase.

IMPORTANT: Selectors are verified against the authorized portal only.
           Do NOT add selectors based on guesswork.
           Mark unverified selectors clearly.
"""

from __future__ import annotations


class PMJAYSelectors:
    """
    Selectors for the PM-JAY / TMS portal.

    Status: UNVERIFIED — must be confirmed against the authorized portal
    environment before use in production.  The workflow will pause at
    WAITING_FOR_HUMAN if an expected element is not found.
    """

    # Login page
    LOGIN_USERNAME_LABEL = "User Name"  # unverified
    LOGIN_PASSWORD_LABEL = "Password"  # unverified
    LOGIN_SUBMIT_ROLE = "button"
    LOGIN_SUBMIT_NAME = "Login"  # unverified

    # Dashboard / navigation
    BENEFICIARY_SEARCH_LINK = "Beneficiary Search"  # unverified

    # Beneficiary search
    SEARCH_ID_LABEL = "Beneficiary ID"  # unverified
    SEARCH_BUTTON_NAME = "Search"  # unverified

    # Result page
    RESULT_NAME_SELECTOR = "[data-field='beneficiary_name']"  # unverified
    RESULT_STATUS_SELECTOR = "[data-field='status']"  # unverified
