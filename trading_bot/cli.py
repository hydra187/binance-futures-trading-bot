"""CLI entry point for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv

from trading_bot.bot.client import BinanceFuturesClient, DEFAULT_BASE_URL
from trading_bot.bot.exceptions import TradingBotError
from trading_bot.bot.logging_config import LOG_FILE, configure_logging
from trading_bot.bot.orders import OrderService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place Binance USDT-M Futures Testnet orders.",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, for example BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"])
    parser.add_argument(
        "--type",
        "--order-type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP", "STOP_LIMIT", "market", "limit", "stop", "stop_limit"],
        help="Order type. STOP is Binance's stop-limit order type.",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Required for LIMIT and STOP orders")
    parser.add_argument("--stop-price", help="Required for STOP orders")
    parser.add_argument("--time-in-force", default="GTC", help="GTC, IOC, FOK, or GTX. Default: GTC")
    parser.add_argument("--base-url", default=os.getenv("BINANCE_BASE_URL", DEFAULT_BASE_URL))
    return parser


def print_summary(request: dict[str, str], response: dict[str, Any]) -> None:
    print("\nOrder request summary")
    print(f"  Symbol:       {request.get('symbol')}")
    print(f"  Side:         {request.get('side')}")
    print(f"  Type:         {request.get('type')}")
    print(f"  Quantity:     {request.get('quantity')}")
    if "price" in request:
        print(f"  Price:        {request.get('price')}")
    if "stopPrice" in request:
        print(f"  Stop price:   {request.get('stopPrice')}")
    if "timeInForce" in request:
        print(f"  Time in force:{request.get('timeInForce')}")

    print("\nOrder response details")
    print(f"  Order ID:     {response.get('orderId', 'N/A')}")
    print(f"  Status:       {response.get('status', 'N/A')}")
    print(f"  Executed qty: {response.get('executedQty', 'N/A')}")
    print(f"  Avg price:    {response.get('avgPrice', 'N/A')}")
    print(f"  Client ID:    {response.get('clientOrderId', 'N/A')}")


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    configure_logging()
    args = build_parser().parse_args(argv)

    try:
        client = BinanceFuturesClient(
            api_key=os.getenv("BINANCE_API_KEY"),
            api_secret=os.getenv("BINANCE_API_SECRET"),
            base_url=args.base_url,
        )
        service = OrderService(client)
        request, response = service.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            time_in_force=args.time_in_force,
        )
    except TradingBotError as exc:
        print(f"\nFailure: {exc}", file=sys.stderr)
        print(f"See log file: {LOG_FILE}", file=sys.stderr)
        return 1

    print_summary(request, response)
    print(f"\nSuccess: order submitted to Binance Futures Testnet.")
    print(f"Log file: {LOG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

