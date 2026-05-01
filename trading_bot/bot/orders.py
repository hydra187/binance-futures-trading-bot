"""Order placement service."""

from __future__ import annotations

import logging
from typing import Any

from trading_bot.bot.client import BinanceFuturesClient
from trading_bot.bot.validators import validate_order_inputs


LOGGER = logging.getLogger(__name__)


class OrderService:
    """Validates user input and delegates order placement to the API client."""

    def __init__(self, client: BinanceFuturesClient) -> None:
        self.client = client

    def place_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None,
        stop_price: str | None,
        time_in_force: str,
    ) -> tuple[dict[str, str], dict[str, Any]]:
        request = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )

        LOGGER.info("Validated order request", extra={"event": "order_validated", "data": request})
        response = self.client.place_order(request)
        LOGGER.info("Order placement completed", extra={"event": "order_completed", "data": response})
        return request, response

# v1.0.0 - Binance Futures Testnet Trading Bot
