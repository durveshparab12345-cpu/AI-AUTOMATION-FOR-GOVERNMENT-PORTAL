"""
PM-JAY / TMS Portal Adapter — Stage 2A Prototype.

THIS IS A PROTOTYPE ADAPTER.

IMPORTANT SAFETY CONSTRAINTS:
  - This adapter does NOT bypass CAPTCHA, OTP, DSC, or any security control.
  - Every authentication step that requires a security token pauses with
    HumanActionRequired so the authorized operator can complete it.
  - No portal credentials are stored in this file or in any log.
  - Only actions that can be safely and legitimately automated are implemented.
  - If an expected element is not found, the workflow enters WAITING_FOR_HUMAN
    rather than attempting to click random elements.
  - No real patient data is used — only the demo case synthetic data.
  - Selectors are marked UNVERIFIED until confirmed in the authorized environment.

AUTHORIZED USE ONLY:
  This adapter must only be used with portal accounts that the operating
  organization is authorized to access.
"""

from __future__ import annotations

import logging

from app.models.demo_case import DemoCase
from app.services.browser.browser_session import BrowserSession, HumanActionRequired
from app.services.browser.selectors import PMJAYSelectors
from app.services.portals.base import PortalAdapter, PortalStepResult

logger = logging.getLogger(__name__)

# The PM-JAY / TMS portal URL.
# This must be set to the URL of the authorized portal environment.
# NEVER point this at a portal the organization is not authorized to access.
PMJAY_PORTAL_URL = "https://tmis.pmjay.gov.in"


class PMJAYAdapter(PortalAdapter):
    """
    PM-JAY portal adapter for the beneficiary/case processing demo workflow.

    Implements only the steps that can safely be assisted in the authorized
    portal environment.  Every step that requires human action (OTP, CAPTCHA,
    DSC, sensitive submission) raises HumanActionRequired.
    """

    def __init__(self, session: BrowserSession, demo_case: DemoCase):
        self._session = session
        self._demo_case = demo_case

    async def connect(self) -> PortalStepResult:
        """Step 1: Open the PM-JAY/TMS portal in the browser."""
        try:
            title = await self._session.page.title() if self._session.page else ""
            if not self._session.page:
                return PortalStepResult(success=False, message="Browser session not started")
            await self._session.navigate(PMJAY_PORTAL_URL)
            await self._session.check_for_human_required()
            title = await self._session.get_title()
            screenshot = await self._session.take_screenshot("connect")
            return PortalStepResult(
                success=True,
                message=f"Portal opened — page title: {title!r}",
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("connect_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required at portal open",
                screenshot_path=screenshot,
            )
        except Exception as e:
            logger.exception("connect() failed")
            return PortalStepResult(
                success=False,
                message=f"Could not open portal: {e}",
            )

    async def authenticate(self, credentials_ref: str) -> PortalStepResult:
        """
        Step 2: Initiate portal authentication.

        credentials_ref is a placeholder reference — the actual credentials
        are entered by the operator.  This method navigates to the login
        page and then ALWAYS pauses for the operator to enter credentials,
        because:
          - Credentials are never stored in this adapter.
          - OTP / CAPTCHA may be required.
          - DSC may be required.

        The operator completes login manually, then clicks Continue.
        """
        try:
            await self._session.check_for_human_required()
            screenshot = await self._session.take_screenshot("auth_start")
            # Intentionally hand over to the operator — we do not attempt
            # to fill the login form automatically because:
            # 1. Credentials are not stored here.
            # 2. OTP/CAPTCHA/DSC requirements are portal-specific.
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=(
                    "Portal authentication requires your credentials. "
                    "Please log in to the PM-JAY portal using your authorized "
                    "account, complete any OTP/CAPTCHA/DSC steps, then click "
                    "Continue to proceed with the demo."
                ),
                message="Waiting for operator authentication",
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("auth_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required during authentication",
                screenshot_path=screenshot,
            )
        except Exception as e:
            logger.exception("authenticate() failed")
            return PortalStepResult(success=False, message=f"Authentication step error: {e}")

    async def navigate_to_section(self, section: str) -> PortalStepResult:
        """Step 3: Navigate to the beneficiary/case section after login."""
        try:
            await self._session.check_for_human_required()

            # Try to find the section link by text
            found = await self._session.wait_for_text(
                PMJAYSelectors.BENEFICIARY_SEARCH_LINK, timeout_ms=5000
            )
            if not found:
                screenshot = await self._session.take_screenshot("nav_not_found")
                return PortalStepResult(
                    success=False,
                    requires_human=True,
                    human_reason=(
                        f"Expected portal element '{PMJAYSelectors.BENEFICIARY_SEARCH_LINK}' "
                        "was not found. The portal layout may have changed, or you may need "
                        "to navigate manually. Please navigate to the beneficiary search "
                        "section and click Continue."
                    ),
                    message="Expected portal element not found",
                    screenshot_path=screenshot,
                )

            await self._session.click_by_text(PMJAYSelectors.BENEFICIARY_SEARCH_LINK)
            await self._session.check_for_human_required()
            screenshot = await self._session.take_screenshot("navigated")
            return PortalStepResult(
                success=True,
                message=f"Navigated to section: {section}",
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("nav_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required during navigation",
                screenshot_path=screenshot,
            )
        except Exception as e:
            logger.exception("navigate_to_section() failed")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=(
                    f"Unexpected portal state during navigation: {e}. "
                    "Please navigate manually."
                ),
                message=f"Navigation error: {e}",
            )

    async def search(self, query: str) -> PortalStepResult:
        """Step 4: Search for the demo beneficiary using demo_beneficiary_id."""
        try:
            await self._session.check_for_human_required()
            beneficiary_id = self._demo_case.demo_beneficiary_id

            # Attempt to fill the search field — falls back to human if not found
            try:
                await self._session.fill_by_label(PMJAYSelectors.SEARCH_ID_LABEL, beneficiary_id)
                await self._session.click_by_role(
                    PMJAYSelectors.LOGIN_SUBMIT_ROLE, PMJAYSelectors.SEARCH_BUTTON_NAME
                )
            except Exception:
                screenshot = await self._session.take_screenshot("search_element_missing")
                return PortalStepResult(
                    success=False,
                    requires_human=True,
                    human_reason=(
                        f"Could not locate the beneficiary search field "
                        f"(label: '{PMJAYSelectors.SEARCH_ID_LABEL}'). "
                        f"Please search for Beneficiary ID: {beneficiary_id} manually, "
                        "then click Continue."
                    ),
                    message="Search field not found — human action required",
                    screenshot_path=screenshot,
                )

            await self._session.check_for_human_required()
            screenshot = await self._session.take_screenshot("search_submitted")
            return PortalStepResult(
                success=True,
                message=f"Search submitted for Beneficiary ID: {beneficiary_id}",
                data={"beneficiary_id": beneficiary_id},
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("search_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required during search",
                screenshot_path=screenshot,
            )
        except Exception as e:
            logger.exception("search() failed")
            return PortalStepResult(success=False, message=f"Search error: {e}")

    async def read_page(self) -> PortalStepResult:
        """Step 5: Read and return information from the current portal page."""
        try:
            await self._session.check_for_human_required()
            url = await self._session.get_url()
            title = await self._session.get_title()
            screenshot = await self._session.take_screenshot("read_page")
            # Only return information actually on the page — no fabrication
            return PortalStepResult(
                success=True,
                message="Page information captured",
                data={"page_title": title, "page_url": url},
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("read_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required",
                screenshot_path=screenshot,
            )
        except Exception as e:
            return PortalStepResult(success=False, message=f"Read page error: {e}")

    async def fill_field(self, field_name: str, value: str) -> PortalStepResult:
        """Step 7: Fill a portal form field with a mapped value."""
        try:
            await self._session.check_for_human_required()
            try:
                await self._session.fill_by_label(field_name, value)
                screenshot = await self._session.take_screenshot(f"fill_{field_name}")
                return PortalStepResult(
                    success=True,
                    message=f"Field '{field_name}' filled",
                    screenshot_path=screenshot,
                )
            except Exception:
                screenshot = await self._session.take_screenshot("fill_not_found")
                return PortalStepResult(
                    success=False,
                    requires_human=True,
                    human_reason=(
                        f"Portal field '{field_name}' was not found. "
                        "Please fill this field manually, then click Continue."
                    ),
                    message=f"Field '{field_name}' not found on portal page",
                    screenshot_path=screenshot,
                )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("fill_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required",
                screenshot_path=screenshot,
            )

    async def upload_document(self, field_name: str, file_path: str) -> PortalStepResult:
        """Step 9: Upload a document — requires human confirmation."""
        screenshot = await self._session.take_screenshot("upload_pending")
        return PortalStepResult(
            success=False,
            requires_human=True,
            human_reason=(
                f"Document upload for '{field_name}' requires human confirmation. "
                "Please upload the document manually, then click Continue."
            ),
            message="Document upload requires human action",
            screenshot_path=screenshot,
        )

    async def validate(self) -> PortalStepResult:
        """Step 8: Ask the portal to validate the current form."""
        try:
            await self._session.check_for_human_required()
            screenshot = await self._session.take_screenshot("validate")
            return PortalStepResult(
                success=True,
                message="Portal validation step reached",
                screenshot_path=screenshot,
            )
        except HumanActionRequired as e:
            screenshot = await self._session.take_screenshot("validate_human")
            return PortalStepResult(
                success=False,
                requires_human=True,
                human_reason=e.reason,
                message="Human action required during validation",
                screenshot_path=screenshot,
            )

    async def request_human_action(self, reason: str) -> PortalStepResult:
        """Explicitly request human intervention with a given reason."""
        screenshot = await self._session.take_screenshot("human_requested")
        return PortalStepResult(
            success=False,
            requires_human=True,
            human_reason=reason,
            message="Human action requested by workflow",
            screenshot_path=screenshot,
        )

    async def disconnect(self) -> None:
        """Close the browser session."""
        await self._session.close()
