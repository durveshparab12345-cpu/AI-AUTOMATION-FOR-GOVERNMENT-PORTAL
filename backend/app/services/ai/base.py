"""
Abstract base class for AI providers.

This module defines the interface that all AI provider implementations
must follow, enabling easy switching between different AI backends.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    Defines the interface for AI services (OpenAI, Claude, custom models).
    Implementations must provide all abstract methods.
    """

    def __init__(self, api_key: str, model: str, timeout: int = 30):
        """
        Initialize AI provider.

        Args:
            api_key: API key for the provider
            model: Model name/ID to use
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            **kwargs: Provider-specific arguments

        Returns:
            Generated text

        Raises:
            AIProviderException: If completion fails
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate chat response.

        Args:
            messages: Chat message history
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            **kwargs: Provider-specific arguments

        Returns:
            Generated response

        Raises:
            AIProviderException: If chat fails
        """
        pass

    @abstractmethod
    async def extract_fields(
        self,
        text: str,
        fields: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract structured fields from text.

        Args:
            text: Input text to extract from
            fields: List of field names to extract
            **kwargs: Provider-specific arguments

        Returns:
            Dictionary of extracted fields

        Raises:
            AIProviderException: If extraction fails
        """
        pass

    @abstractmethod
    async def classify(
        self,
        text: str,
        categories: List[str],
        **kwargs
    ) -> str:
        """
        Classify text into one of provided categories.

        Args:
            text: Text to classify
            categories: List of possible categories
            **kwargs: Provider-specific arguments

        Returns:
            Selected category

        Raises:
            AIProviderException: If classification fails
        """
        pass

    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int = 200,
        **kwargs
    ) -> str:
        """
        Generate summary of text.

        Args:
            text: Text to summarize
            max_length: Maximum summary length
            **kwargs: Provider-specific arguments

        Returns:
            Generated summary

        Raises:
            AIProviderException: If summarization fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is available and responding.

        Returns:
            True if provider is available, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured model.

        Returns:
            Dictionary with model information
        """
        pass


class AIProviderManager:
    """
    Manager for multiple AI providers.

    Allows switching between different AI backends and
    provides fallback capabilities.
    """

    def __init__(self):
        """Initialize provider manager."""
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider: Optional[str] = None

    def register_provider(
        self,
        name: str,
        provider: AIProvider,
        set_default: bool = False,
    ) -> None:
        """
        Register an AI provider.

        Args:
            name: Name for this provider
            provider: Provider instance
            set_default: If True, set as default provider
        """
        self.providers[name] = provider
        if set_default or self.default_provider is None:
            self.default_provider = name

    def get_provider(self, name: Optional[str] = None) -> AIProvider:
        """
        Get an AI provider by name.

        Args:
            name: Provider name; uses default if not specified

        Returns:
            Provider instance

        Raises:
            ValueError: If provider not found
        """
        if name is None:
            name = self.default_provider

        if name not in self.providers:
            raise ValueError(f"Provider not found: {name}")

        return self.providers[name]

    async def get_available_provider(self) -> AIProvider:
        """
        Get first available AI provider.

        Checks provider health and returns first responding provider.

        Returns:
            Available provider instance

        Raises:
            AIProviderException: If no providers available
        """
        # TODO: Implement health checking and fallback logic
        pass
