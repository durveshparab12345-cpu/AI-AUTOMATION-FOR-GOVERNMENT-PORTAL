"""
BrowserManager — process-level registry of active BrowserSessions.

One manager instance lives for the lifetime of the application (stored in
app.state).  It maps execution_id → BrowserSession so that route handlers
can look up an existing session by ID.
"""

from __future__ import annotations

import logging

from app.services.browser.browser_session import BrowserSession

logger = logging.getLogger(__name__)


class BrowserManager:
    """Registry of active browser sessions, keyed by execution_id."""

    def __init__(self) -> None:
        self._sessions: dict[str, BrowserSession] = {}

    async def create_session(self, execution_id: str) -> BrowserSession:
        """Create, register, and start a new BrowserSession."""
        if execution_id in self._sessions:
            logger.warning("Session %s already exists — closing old session first", execution_id)
            await self.close_session(execution_id)

        session = BrowserSession(execution_id=execution_id)
        await session.start()
        self._sessions[execution_id] = session
        logger.info("Browser session created for execution %s", execution_id)
        return session

    def get_session(self, execution_id: str) -> BrowserSession | None:
        """Return the active session for execution_id, or None."""
        return self._sessions.get(execution_id)

    async def close_session(self, execution_id: str) -> None:
        """Close and remove a session from the registry."""
        session = self._sessions.pop(execution_id, None)
        if session:
            await session.close()
            logger.info("Browser session closed for execution %s", execution_id)

    async def close_all(self) -> None:
        """Close every active session — called on application shutdown."""
        ids = list(self._sessions.keys())
        for eid in ids:
            await self.close_session(eid)

    @property
    def active_count(self) -> int:
        return len(self._sessions)
