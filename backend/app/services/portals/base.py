"""
Base portal adapter interface.

Every portal integration must implement this abstract class.
Route handlers and the workflow engine interact with this interface —
never with portal-specific code directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class PortalStepResult:
    """Result of a single portal interaction step."""

    success: bool
    message: str
    requires_human: bool = False
    human_reason: str = ""
    data: dict = field(default_factory=dict)
    screenshot_path: str | None = None


class PortalAdapter(ABC):
    """
    Abstract base class for all portal adapters.

    Subclasses implement the specific portal logic.
    The workflow engine calls these methods in sequence.
    """

    @abstractmethod
    async def connect(self) -> PortalStepResult:
        """Open the browser and navigate to the portal URL."""
        ...

    @abstractmethod
    async def authenticate(self, credentials_ref: str) -> PortalStepResult:
        """
        Initiate portal authentication.
        credentials_ref is a reference to stored credentials — never the
        password itself.  This method must pause for OTP/CAPTCHA/DSC.
        """
        ...

    @abstractmethod
    async def navigate_to_section(self, section: str) -> PortalStepResult:
        """Navigate to a named section of the portal."""
        ...

    @abstractmethod
    async def search(self, query: str) -> PortalStepResult:
        """Execute a search on the current portal section."""
        ...

    @abstractmethod
    async def read_page(self) -> PortalStepResult:
        """Read and return structured data from the current portal page."""
        ...

    @abstractmethod
    async def fill_field(self, field_name: str, value: str) -> PortalStepResult:
        """Fill a named field on the current portal form."""
        ...

    @abstractmethod
    async def upload_document(self, field_name: str, file_path: str) -> PortalStepResult:
        """Upload a document to the portal."""
        ...

    @abstractmethod
    async def validate(self) -> PortalStepResult:
        """Ask the portal to validate the current form state."""
        ...

    @abstractmethod
    async def request_human_action(self, reason: str) -> PortalStepResult:
        """Signal that human intervention is required."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the portal session."""
        ...
