"""
Portal adapter factory for creating portal-specific adapters.

This module provides a factory pattern for instantiating the correct
portal adapter based on portal type.
"""

from typing import Type, Dict
from enum import Enum

# TODO: Import portal adapters
# from .pmjay import PMJAYPortalAdapter


class PortalType(str, Enum):
    """Supported portal types."""

    PMJAY = "PMJAY"
    CUSTOM = "CUSTOM"


class PortalAdapterFactory:
    """
    Factory for creating portal adapters.

    Maps portal types to adapter classes and provides methods
    for instantiating adapters.
    """

    _adapters: Dict[PortalType, Type] = {}

    @classmethod
    def register(cls, portal_type: PortalType, adapter_class: Type) -> None:
        """
        Register a portal adapter.

        Args:
            portal_type: Type of portal
            adapter_class: Adapter class for this portal type
        """
        cls._adapters[portal_type] = adapter_class

    @classmethod
    def create(cls, portal_type: PortalType, **kwargs):
        """
        Create a portal adapter instance.

        Args:
            portal_type: Type of portal to create adapter for
            **kwargs: Arguments to pass to adapter constructor

        Returns:
            Portal adapter instance

        Raises:
            ValueError: If portal type is not registered
        """
        if portal_type not in cls._adapters:
            raise ValueError(f"Unknown portal type: {portal_type}")

        adapter_class = cls._adapters[portal_type]
        return adapter_class(**kwargs)

    @classmethod
    def get_supported_types(cls) -> list:
        """
        Get list of supported portal types.

        Returns:
            List of supported portal types
        """
        return list(cls._adapters.keys())


# Register default adapters
# TODO: Uncomment after portal adapters are implemented
# PortalAdapterFactory.register(PortalType.PMJAY, PMJAYPortalAdapter)
