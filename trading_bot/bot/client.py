"""Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests

from trading_bot.bot.exceptions import BinanceAPIError, ConfigError


LOGGER = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    """Minimal signed REST client for Binance USDT-M Futures Testnet."""

    def __init__(
        self,
        api_key: str | None,
        api_secret: str | None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 10,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8") if api_secret else None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-MBX-APIKEY": api_key})

    def _sign(self, params: dict[str, Any]) -> str:
        if self.api_secret is None:
            raise ConfigError("BINANCE_API_SECRET is missing")
        query_string = urlencode(params, doseq=True)
        return hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _signed_request(self, method: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise ConfigError("BINANCE_API_KEY is missing")

        request_params = {
            **params,
            "timestamp": int(time.time() * 1000),
            "recvWindow": 5000,
        }
        request_params["signature"] = self._sign(request_params)
        safe_params = {k: v for k, v in request_params.items() if k != "signature"}
        url = f"{self.base_url}{path}"

        LOGGER.info(
            "Sending Binance API request",
            extra={"event": "api_request", "data": {"method": method, "url": url, "params": safe_params}},
        )

        try:
            response = self.session.request(method, url, params=request_params, timeout=self.timeout)
        except requests.RequestException as exc:
            LOGGER.exception(
                "Network error while calling Binance API",
                extra={"event": "api_network_error", "data": {"method": method, "url": url}},
            )
            raise BinanceAPIError(f"network error: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            LOGGER.error(
                "Binance API returned a non-JSON response",
                extra={
                    "event": "api_invalid_json",
                    "data": {"status_code": response.status_code, "text": response.text[:500]},
                },
            )
            raise BinanceAPIError("Binance returned a non-JSON response") from exc

        LOGGER.info(
            "Received Binance API response",
            extra={
                "event": "api_response",
                "data": {"status_code": response.status_code, "body": payload},
            },
        )

        if response.status_code >= 400:
            message = payload.get("msg", "unknown Binance API error") if isinstance(payload, dict) else payload
            raise BinanceAPIError(f"Binance API error ({response.status_code}): {message}")

        if not isinstance(payload, dict):
            raise BinanceAPIError("Binance returned an unexpected response shape")

        return payload

    def place_order(self, order_params: dict[str, str]) -> dict[str, Any]:
        """Place an order on Binance USDT-M Futures."""
        params: dict[str, Any] = {
            **order_params,
            "newOrderRespType": "RESULT",
        }
        return self._signed_request("POST", "/fapi/v1/order", params)
