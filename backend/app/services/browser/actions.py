"""
Reusable browser action helpers.

These functions operate on a BrowserSession and encapsulate common
interaction patterns.  They are NOT portal-specific — the portal adapter
composes these into portal-specific workflows.
"""

from __future__ import annotations

import logging

from app.services.browser.browser_session import BrowserSession

logger = logging.getLogger(__name__)


async def safe_navigate(session: BrowserSession, url: str) -> str:
    """Navigate to url, then check for human-required triggers. Returns page title."""
    await session.navigate(url)
    await session.check_for_human_required()
    title = await session.get_title()
    logger.info("Navigated to %s — title: %r", url, title)
    return title


async def wait_and_fill(session: BrowserSession, label: str, value: str) -> None:
    """Fill a labelled form field after checking for CAPTCHA/OTP."""
    await session.check_for_human_required()
    await session.fill_by_label(label, value)
    logger.debug("Filled field %r", label)


async def wait_and_click_role(session: BrowserSession, role: str, name: str) -> None:
    """Click a role-based element after checking for CAPTCHA/OTP."""
    await session.check_for_human_required()
    await session.click_by_role(role, name)
    logger.debug("Clicked role=%r name=%r", role, name)
