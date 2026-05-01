"""Input validation helpers.

Validates all CLI input before any API call is made.
Raises ValidationError for any invalid or missing field.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from trading_bot.bot.exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}
VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK", "GTX"}


def normalize_symbol(symbol: str) -> str:
    """Validate and normalise the trading symbol."""
    value = symbol.strip().upper()
    if not value:
        raise ValidationError("symbol is required")
    if not value.endswith("USDT"):
        raise ValidationError("only USDT-M symbols are supported, for example BTCUSDT")
    if not value.isalnum():
        raise ValidationError("symbol must contain only letters and numbers")
    return value


def normalize_side(side: str) -> str:
    """Validate order side: BUY or SELL."""
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    return value


def normalize_order_type(order_type: str) -> str:
    """Validate order type; map STOP / STOP_LIMIT aliases to STOP_MARKET."""
    value = order_type.strip().upper()
    if value in ("STOP", "STOP_LIMIT"):
        value = "STOP_MARKET"
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET, LIMIT, or STOP_MARKET")
    return value


def parse_positive_decimal(raw_value: str, field_name: str) -> Decimal:
    """Parse a string as a positive decimal number."""
    try:
        value = Decimal(str(raw_value))
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} must be a valid decimal number") from exc
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero")
    return value


def validate_order_inputs(
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
    time_in_force: str = "GTC",
) -> dict[str, str]:
    """Validate all CLI order fields and return a clean Binance request dict.

    Rules enforced:
    - symbol   : non-empty, ends with USDT, alphanumeric
    - side     : BUY or SELL
    - type     : MARKET, LIMIT, or STOP_MARKET
    - quantity : positive decimal
    - price    : required for LIMIT; forbidden for MARKET / STOP_MARKET
    - stopPrice: required for STOP_MARKET; forbidden for MARKET / LIMIT
    """

    normalized_type = normalize_order_type(order_type)
    normalized: dict[str, str] = {
        "symbol": normalize_symbol(symbol),
        "side": normalize_side(side),
        "type": normalized_type,
        "quantity": str(parse_positive_decimal(quantity, "quantity")),
    }

    tif = time_in_force.strip().upper()
    if tif not in VALID_TIME_IN_FORCE:
        raise ValidationError("timeInForce must be one of GTC, IOC, FOK, or GTX")

    if normalized_type == "MARKET":
        if price is not None:
            raise ValidationError("price must not be set for MARKET orders")
        if stop_price is not None:
            raise ValidationError("stopPrice must not be set for MARKET orders")
        return normalized

    if normalized_type == "STOP_MARKET":
        if price is not None:
            raise ValidationError("price must not be set for STOP_MARKET; use --stop-price instead")
        if stop_price is None:
            raise ValidationError("--stop-price is required for STOP_MARKET orders")
        normalized["stopPrice"] = str(parse_positive_decimal(stop_price, "stopPrice"))
        return normalized

    # LIMIT order
    if price is None:
        raise ValidationError("--price is required for LIMIT orders")
    normalized["price"] = str(parse_positive_decimal(price, "price"))
    normalized["timeInForce"] = tif
    if stop_price is not None:
        raise ValidationError("stopPrice must not be set for LIMIT orders")

    return normalized
