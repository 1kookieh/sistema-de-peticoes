"""Typed errors raised by the LLM integration layer."""


class LLMError(RuntimeError):
    """Base class for expected LLM failures."""


class LLMConfigurationError(LLMError):
    """Provider or credential configuration is invalid."""


class LLMProviderError(LLMError):
    """The remote or local provider failed."""


class LLMResponseValidationError(LLMError):
    """The provider returned an invalid structured response."""
