# Binance Futures Testnet Trading Bot

A small Python CLI application for placing Market, Limit, and Stop-Limit orders on Binance USDT-M Futures Testnet.

The application uses direct signed REST calls against:

```text
https://testnet.binancefuture.com
```

## Features

- Places `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Supports `BUY` and `SELL`
- Bonus order type: `STOP` / `STOP_LIMIT`
- Validates CLI input before sending requests
- Prints a clean request summary and response details
- Logs API requests, responses, validation events, and errors to `logs/trading_bot.log`
- Keeps API logic separate from CLI logic

## Project Structure

```text
trading_bot/
  bot/
    client.py          # Binance signed REST client
    orders.py          # Order placement service
    validators.py      # CLI input validation
    logging_config.py  # JSON-lines file logging
    exceptions.py      # Custom exceptions
  cli.py               # CLI entry point
  __main__.py          # python -m trading_bot entry point
README.md
requirements.txt
.env.example
logs/.gitkeep
```

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a Binance Futures Testnet account and generate API credentials.

4. Create a `.env` file:

```bash
cp .env.example .env
```

5. Edit `.env` with your testnet credentials:

```text
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## Usage Examples

Run commands from the repository root.

### Market Order

```bash
python -m trading_bot \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Limit Order

```bash
python -m trading_bot \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 120000 \
  --time-in-force GTC
```

### Stop-Limit Order

Binance Futures uses `STOP` for stop-limit orders.

```bash
python -m trading_bot \
  --symbol BTCUSDT \
  --side SELL \
  --type STOP_LIMIT \
  --quantity 0.001 \
  --price 118000 \
  --stop-price 119000 \
  --time-in-force GTC
```

## Output

Successful orders print:

- order request summary
- `orderId`
- `status`
- `executedQty`
- `avgPrice`
- success message
- log file location

Example:

```text
Order request summary
  Symbol:       BTCUSDT
  Side:         BUY
  Type:         MARKET
  Quantity:     0.001

Order response details
  Order ID:     123456789
  Status:       FILLED
  Executed qty: 0.001
  Avg price:    65000.00
  Client ID:    abc123

Success: order submitted to Binance Futures Testnet.
Log file: logs/trading_bot.log
```

## Logging

Logs are written as JSON lines to:

```text
logs/trading_bot.log
```

The log captures:

- validated order input
- API request metadata
- API response body
- API errors
- network failures

API signatures are not logged.

After running one market order and one limit order, include `logs/trading_bot.log` in the submitted zip/repository. The file is intentionally not committed here because it depends on real testnet credentials and live Binance responses.

## Error Handling

The CLI exits with a non-zero status and prints a clear failure message for:

- missing API credentials
- invalid symbol, side, order type, quantity, price, or stop price
- Binance API errors
- network failures
- non-JSON or unexpected API responses

## Assumptions

- This bot is for Binance USDT-M Futures Testnet only.
- Credentials are provided through environment variables or `.env`.
- Quantity and price precision must be valid for the selected Binance symbol. Binance will reject values that do not match the exchange filters.
- Orders are sent with `newOrderRespType=RESULT` so the response includes useful order status details when available.

