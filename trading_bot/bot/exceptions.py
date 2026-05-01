"""Custom exceptions for the trading bot."""


class TradingBotError(Exception):
    """Base exception for bot failures."""


class ValidationError(TradingBotError):
    """Raised when user input is invalid."""


class ConfigError(TradingBotError):
    """Raised when required configuration is missing."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API error."""
