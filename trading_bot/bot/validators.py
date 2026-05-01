"""Input validation helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from trading_bot.bot.exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}
VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK", "GTX"}


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not value:
        raise ValidationError("symbol is required")
    if not value.endswith("USDT"):
        raise ValidationError("only USDT-M symbols are supported, for example BTCUSDT")
    if not value.isalnum():
        raise ValidationError("symbol must contain only letters and numbers")
    return value


def normalize_side(side: str) -> str:
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    return value


def normalize_order_type(order_type: str) -> str:
    value = order_type.strip().upper()
    if value == "STOP_LIMIT":
        value = "STOP"
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET, LIMIT, or STOP")
    return value


def parse_positive_decimal(raw_value: str, field_name: str) -> Decimal:
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
    """Validate and normalize CLI order input."""

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
            raise ValidationError("price is not accepted for MARKET orders")
        if stop_price is not None:
            raise ValidationError("stopPrice is not accepted for MARKET orders")
        return normalized

    if price is None:
        raise ValidationError("price is required for LIMIT and STOP orders")

    normalized["price"] = str(parse_positive_decimal(price, "price"))
    normalized["timeInForce"] = tif

    if normalized_type == "STOP":
        if stop_price is None:
            raise ValidationError("stopPrice is required for STOP orders")
        normalized["stopPrice"] = str(parse_positive_decimal(stop_price, "stopPrice"))
        normalized["type"] = "STOP"
    elif stop_price is not None:
        raise ValidationError("stopPrice is only accepted for STOP orders")

    return normalized

# v1.0.0 - Binance Futures Testnet Trading Bot
