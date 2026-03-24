# Trading Bot

A modular Python trading bot with Streamlit web interface, supporting MetaTrader 5 and customizable trading strategies with built-in backtesting.

## Overview

- **Web-based interface** using Streamlit with Backtesting and Live Trading tabs
- **MetaTrader 5 integration** for live trading and historical data
- **Backtesting** via [backtesting.py](https://kernc.github.io/backtesting.py/) with stats and interactive charts
- **Auto-discovered strategy system** — add a file to `strategies/`, no registration needed
- **Discord integration** for real-time alerts

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Strategy Router │───▶│   Strategies    │
│    (app.py)     │    │ (strategy_router)│    │  (strategies/)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Trading Platform│    │  Backtesting.py │    │  BaseStrategy   │
│  (MetaTrader 5) │    │  (backtest tab) │    │  (base class)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Files

- **`app.py`** - Streamlit UI with Backtesting and Live Trading tabs
- **`strategy_router.py`** - Auto-discovers and routes strategies
- **`strategies/base_strategy.py`** - Base class all strategies must extend
- **`strategies/`** - Strategy implementations (auto-discovered)
- **`helper_functions.py`** - Platform utilities and data retrieval
- **`metatrader_interface.py`** - MetaTrader 5 integration and order execution
- **`discord_interaction.py`** - Discord alerts
- **`static_content/`** - Timeframe configuration

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [MetaTrader 5](https://www.metatrader5.com/en/download) installed (for MetaTrader integration)
- Discord bot token (optional, for alerts)

### macOS Prerequisites

MetaTrader 5 requires Windows, so on macOS you need to run it via [Wine](https://www.winehq.org/).

1. **Install Wine** via [Homebrew](https://brew.sh/):
   ```bash
   brew install --cask wine-stable
   ```

2. **Install Python for Windows** through Wine:
   ```bash
   wine msiexec /i python-3.10.x.msi
   ```
   Download the Windows installer from [python.org](https://www.python.org/downloads/windows/).

3. **Install MetaTrader 5** through Wine:
   ```bash
   wine mt5setup.exe
   ```

4. **If macOS blocks Wine** due to validation errors, run:
   ```bash
   sudo spctl --master-disable
   ```
   This disables Gatekeeper to allow unverified apps to run.

### Quick Start

1. **Clone and install**:
   ```bash
   git clone <repository-url>
   cd trading-bot
   pip install -r requirements.txt
   ```

2. **Configure environment** (create `.env` file):
   ```env
   metatrader_username=your_username
   metatrader_password=your_password
   metatrader_server=your_server
   metatrader_filepath=C:\path\to\terminal64.exe

   # Optional
   discord_key=your_discord_bot_token
   ```

3. **Run the application**:
   ```bash
   python -m streamlit run app.py
   ```

4. **Open browser** to `http://localhost:8501`

## Using the App

### Platform Setup (top bar)
- Select **Use Settings File** → Yes to load credentials from `.env`
- Select **Trading Platform** → MetaTrader 5 to connect
- Select **Make Trades** → Yes to enable live order execution

### Backtesting Tab (default)
1. Select symbol, timeframe, and strategy
2. Pick a date range
3. Click **Run Backtest**
4. View key stats, full stats, trade log, and interactive chart

### Live Trading Tab
1. Select symbol, timeframe, and strategy
2. Set the polling interval (seconds)
3. Click **▶ Start Trading** — runs the strategy in a loop
4. Click **⏹ Stop** to halt

## How It Works

### Strategy System

All strategies extend `BaseStrategy` which itself extends `backtesting.Strategy`. This means **one implementation works for both backtesting and live trading**.

```
User Input → Platform Connection → Data Retrieval → Strategy.init() → Strategy.next() → Signal / Order
```

For backtesting, `backtesting.py` calls `init()` and `next()` directly.
For live trading, the router calls `init()` + `next()` on the latest candles and reads the signal via `get_signal()`.

### Order Execution

When **Make Trades** is Yes and the signal is not hold:
- Market order placed immediately at current ask/bid
- Take profit: strategy's exit price
- Stop loss: 10% against the position
- Volume: 0.1 lots (fixed)

## Adding a Custom Strategy

### Step 1: Create the strategy file

Create `strategies/my_strategy.py`:

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def init(self):
        # Precompute indicators here using self.I()
        pass

    def next(self):
        # Define buy/sell logic
        if some_condition:
            self._signal_buy = True
            self._signal_sell = False
            self.buy()
        elif other_condition:
            self._signal_buy = False
            self._signal_sell = True
            self.sell()
        else:
            self._signal_buy = False
            self._signal_sell = False
```

That's it. The strategy is **automatically discovered** and appears in the UI — no registration or router changes needed.

The class name is converted to the display name: `MyStrategy` → `"My Strategy"`.

### Strategy API

Inside `init()` and `next()` you have access to:

| Attribute | Description |
|---|---|
| `self.data.Close` | Array of close prices |
| `self.data.Open/High/Low` | OHLC arrays |
| `self.I(func, *args)` | Wrap an indicator for auto-plotting |
| `self.buy()` / `self.sell()` | Place orders |
| `self.position` | Current position info |
| `self.position.close()` | Close current position |

Set `self._signal_buy = True` or `self._signal_sell = True` in `next()` so `get_signal()` can extract the live signal correctly.

## File Structure

```
trading-bot/
├── app.py                        # Streamlit UI (Backtesting + Live Trading tabs)
├── strategy_router.py            # Auto-discovers strategies, routes live signals
├── helper_functions.py           # Platform utilities
├── metatrader_interface.py       # MT5 integration + order execution
├── discord_interaction.py        # Discord alerts
├── data_normalizer.py            # Data formatting
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py          # BaseStrategy — extend this for all strategies
│   └── test_strategy.py          # Example: 2-candle mean reversion
├── static_content/
│   └── timeframes.json           # Supported timeframes
├── requirements.txt
└── README.md
```

## Dependencies

- `streamlit` - Web interface
- `MetaTrader5` - MT5 platform integration
- `backtesting` - Backtesting framework
- `discord.py` - Discord alerts
- `pandas` / `numpy` - Data manipulation
- `python-dotenv` - Environment management

## Configuration

### Environment Variables

| Variable | Description |
|---|---|
| `metatrader_username` | MT5 account login number |
| `metatrader_password` | MT5 account password |
| `metatrader_server` | MT5 broker server name |
| `metatrader_filepath` | Path to `terminal64.exe` |
| `discord_key` | Discord bot token (optional) |

### Timeframes

Defined in `static_content/timeframes.json`: M1, M5, M15, M30, H1, H4, H8, D1, W1, MN1

## Roadmap

### Planned
- [ ] Risk management (position sizing relative to account balance)
- [ ] Multiple simultaneous strategies
- [ ] Performance analytics dashboard
- [ ] More built-in indicators (RSI, MACD, Bollinger Bands)

### Integrations
- [x] MetaTrader 5

---

## License

This project is licensed under the terms included in the LICENSE file.
