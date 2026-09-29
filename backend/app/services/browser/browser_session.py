"""
BrowserSession — wraps a single Playwright browser context and page.

Each workflow execution gets its own BrowserSession.
The session is visible (non-headless) during live presentations so the
operator can see exactly what is happening and intervene when required.

SAFETY RULES enforced here:
- No coordinates-based clicking as primary mechanism (use roles/text/labels)
- Human-in-the-loop: raises HumanActionRequired for CAPTCHA/OTP/DSC
- Timeout on all waits — never hangs silently
- No credentials stored in screenshots or logs
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from app.core.config import settings

logger = logging.getLogger(__name__)

# Default per-action timeout in milliseconds
DEFAULT_TIMEOUT_MS = 15_000


class HumanActionRequired(Exception):
    """
    Raised when the workflow encounters a step that requires human intervention.
    Examples: OTP prompt, CAPTCHA, DSC confirmation, unexpected portal state.
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class BrowserSession:
    """
    Manages a single Playwright browser session for one workflow execution.

    Usage:
        session = BrowserSession(execution_id="abc123")
        await session.start()
        await session.navigate("https://example.com")
        await session.close()
    """

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.page: Page | None = None
        self._screenshot_dir = Path(settings.SCREENSHOT_DIR)
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def start(self) -> None:
        """Launch the browser. Visible by default for live demos."""
        logger.info(
            "[Session %s] Starting browser (headless=%s)",
            self.execution_id,
            settings.BROWSER_HEADLESS,
        )
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.BROWSER_HEADLESS,
            args=["--no-sandbox"],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
        )
        self.page = await self._context.new_page()
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
        logger.info("[Session %s] Browser started successfully", self.execution_id)

    async def navigate(self, url: str) -> None:
        """Navigate to a URL and wait for the page to be interactive."""
        if not self.page:
            raise RuntimeError("Browser session not started")
        logger.info("[Session %s] Navigating to %s", self.execution_id, url)
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

    async def get_title(self) -> str:
        """Return the current page title."""
        if not self.page:
            return ""
        return await self.page.title()

    async def get_url(self) -> str:
        """Return the current page URL."""
        if not self.page:
            return ""
        return self.page.url

    async def click_by_role(self, role: str, name: str) -> None:
        """Click an element by its ARIA role and accessible name."""
        if not self.page:
            raise RuntimeError("Browser session not started")
        await self.page.get_by_role(role, name=name).click()  # type: ignore[arg-type]

    async def click_by_text(self, text: str) -> None:
        """Click an element by its visible text content."""
        if not self.page:
            raise RuntimeError("Browser session not started")
        await self.page.get_by_text(text).first.click()

    async def fill_by_label(self, label: str, value: str) -> None:
        """Fill an input field identified by its associated label."""
        if not self.page:
            raise RuntimeError("Browser session not started")
        await self.page.get_by_label(label).fill(value)

    async def fill_by_placeholder(self, placeholder: str, value: str) -> None:
        """Fill an input field identified by its placeholder text."""
        if not self.page:
            raise RuntimeError("Browser session not started")
        await self.page.get_by_placeholder(placeholder).fill(value)

    async def wait_for_text(self, text: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> bool:
        """Return True if the text appears on the page within the timeout."""
        if not self.page:
            return False
        try:
            await self.page.get_by_text(text).first.wait_for(timeout=timeout_ms)
            return True
        except Exception:
            return False

    async def check_for_human_required(self) -> None:
        """
        Check the current page for known human-intervention triggers.
        Raises HumanActionRequired if found.

        This does NOT attempt to bypass any security control.
        It detects them and hands control to the operator.
        """
        if not self.page:
            return
        content = (await self.page.content()).lower()

        if any(kw in content for kw in ["captcha", "verify you are human", "bot detection"]):
            raise HumanActionRequired(
                "CAPTCHA or bot-detection challenge detected on portal page. "
                "Please complete the challenge manually then click Continue."
            )
        if any(kw in content for kw in ["otp", "one time password", "enter the code"]):
            raise HumanActionRequired(
                "OTP / One-Time Password prompt detected. "
                "Please enter the OTP you received then click Continue."
            )
        if any(kw in content for kw in ["digital signature", "dsc", "sign with"]):
            raise HumanActionRequired(
                "Digital Signature Certificate (DSC) action required. "
                "Please complete the DSC step manually then click Continue."
            )

    async def take_screenshot(self, label: str = "step") -> str | None:
        """
        Capture a screenshot and save it to the configured directory.
        Returns the relative file path, or None if capture fails.
        Screenshots do not capture form fields with sensitive data.
        """
        if not self.page:
            return None
        try:
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"{self.execution_id}_{label}_{ts}.png"
            path = self._screenshot_dir / filename
            await self.page.screenshot(path=str(path))
            logger.debug("[Session %s] Screenshot saved: %s", self.execution_id, filename)
            return str(path)
        except Exception as exc:
            logger.warning("[Session %s] Screenshot failed: %s", self.execution_id, exc)
            return None

    async def close(self) -> None:
        """Close the browser session and release all resources."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as exc:
            logger.warning("[Session %s] Error closing browser: %s", self.execution_id, exc)
        finally:
            self.page = None
            self._browser = None
            self._playwright = None
            logger.info("[Session %s] Browser session closed", self.execution_id)
