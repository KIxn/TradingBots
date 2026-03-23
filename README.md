# Trading Bot

A modular Python trading bot with Streamlit web interface, supporting MetaTrader 5 and customizable trading strategies.

## Overview

This trading bot provides a complete algorithmic trading solution with:
- **Web-based interface** using Streamlit for easy configuration
- **MetaTrader 5 integration** for trading
- **Modular strategy system** for easy customization
- **Discord integration** for real-time alerts
- **Development container** for consistent environment setup

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Strategy Router │───▶│   Strategies    │
│    (app.py)     │    │ (strategy_router)│    │  (strategies/)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Platform Info  │    │   Data Flow     │    │ Trading Signals │
│ (helper_funcs)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Trading Platform│    │ Market Data     │    │  Alert System   │
│   (MetaTrader 5)│    │                 │    │   (Discord)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Files

- **`app.py`** - Streamlit web interface for bot configuration
- **`strategy_router.py`** - Routes trading requests to appropriate strategies
- **`strategies/`** - Directory containing trading strategy implementations
- **`helper_functions.py`** - Common utilities for data retrieval and platform management
- **`metatrader_interface.py`** - MetaTrader 5 platform integration
- **`discord_interaction.py`** - Discord bot for trading alerts
- **`static_content/`** - Configuration files for strategies and timeframes

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [MetaTrader 5](https://www.metatrader5.com/en/download) installed (for MetaTrader integration)
- Discord bot token (optional, for alerts)

### Quick Start

1. **Clone and install**:
   ```bash
   git clone <repository-url>
   cd trading-bot
   pip install -r requirements.txt
   ```

2. **Configure environment** (create `.env` file):
   ```bash
   # MetaTrader 5 Credentials
   metatrader_username=your_username
   metatrader_password=your_password
   metatrader_server=your_server
   metatrader_filepath=/path/to/metatrader5/terminal64.exe
   
   # Discord Bot Token (optional)
   discord_key=your_discord_bot_token
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Open browser** to `http://localhost:8501`

### Using the Trading Bot

1. **Platform Setup**:
   - Select "MetaTrader 5" as trading platform
   - Choose to use settings file or enter credentials manually
   - Enter MetaTrader 5 login details

2. **Trading Configuration**:
   - Select symbol (e.g., EURUSD, GBPUSD)
   - Choose timeframe (M1, H1, D1, etc.)
   - Pick a strategy (currently "Test Strategy")

3. **Get Trading Signals**:
   - Click "Get Data" to analyze market data
   - View buy/sell/hold signals with entry/exit prices
   - Enable Discord alerts for real-time notifications

## How It Works

### 1. Data Flow
The bot follows this sequence for each trading decision:
```
User Input → Platform Connection → Data Retrieval → Strategy Analysis → Signal Generation
```

### 2. Strategy System
Strategies are Python modules in the `strategies/` directory. Each strategy:
- Receives historical market data
- Analyzes using technical indicators
- Returns a signal dictionary:
  ```python
  {
      'decision': 'buy',  # 'buy', 'sell', or 'hold'
      'entry': 1.2345,    # Entry price
      'exit': 1.2456      # Exit price
  }
  ```

### 3. Example Strategy
The included `test_strategy.py` provides a simple example:
```python
def run_strategy(platform, symbol, timeframe):
    # Get market data
    dataframe = helpers.get_data(platform, symbol, timeframe)
    
    # Simple price comparison strategy
    current_close = dataframe.iloc[-1]['candle_close']
    previous_close = dataframe.iloc[-2]['candle_close']
    
    if previous_close > current_close:
        return {'decision': 'buy', 'entry': current_close * 1.01, 'exit': current_close * 1.02}
    elif previous_close < current_close:
        return {'decision': 'sell', 'entry': current_close * 0.99, 'exit': current_close * 0.98}
    else:
        return {'decision': 'hold', 'entry': None, 'exit': None}
```

### 4. Platform Integration

**MetaTrader 5**:
- Connects via `MetaTrader5` Python package
- Retrieves real-time and historical data
- Supports all MetaTrader symbols and timeframes

## Adding Custom Strategies

### Step 1: Create Strategy File
Create `strategies/my_custom_strategy.py`:
```python
import helper_functions as helpers

def run_strategy(platform, symbol, timeframe):
    # Your strategy logic here
    dataframe = helpers.get_data(platform, symbol, timeframe)
    
    # Analyze data and generate signal
    signal = {
        'decision': 'hold',
        'entry': None,
        'exit': None
    }
    
    # Your analysis code...
    
    return signal
```

### Step 2: Register Strategy
Add to `static_content/strategies.json`:
```json
{
    "strategies": [
        {
            "name": "My Custom Strategy",
            "description": "Description of your strategy",
            "platforms": ["MetaTrader5"],
            "id": 2
        }
    ]
}
```

### Step 3: Update Router
Add handling in `strategy_router.py`:
```python
if strategy_name == 'My Custom Strategy':
    signal = my_custom_strategy.run_strategy(
        platform=platform,
        symbol=symbol,
        timeframe=timeframe
    )
```

## Development

### Using Dev Container
The project includes VS Code dev container configuration:
- Pre-configured Python environment
- All dependencies installed
- Network access for trading platforms

### File Structure
```
trading-bot/
├── app.py                    # Main Streamlit application
├── strategy_router.py        # Strategy routing logic
├── helper_functions.py       # Platform utilities
├── metatrader_interface.py   # MT5 integration
├── discord_interaction.py    # Discord alerts
├── data_normalizer.py        # Data formatting
├── strategies/
│   └── test_strategy.py      # Example strategy
├── static_content/
│   ├── strategies.json       # Strategy registry
│   └── timeframes.json       # Supported timeframes
├── .devcontainer/            # Development environment
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

### Dependencies
- `streamlit` - Web interface
- `MetaTrader5` - MT5 platform integration
- `discord.py` - Discord bot for alerts
- `pandas` - Data manipulation
- `python-dotenv` - Environment management

## Configuration

### Environment Variables
Set in `.env` file or directly in the UI:
- `metatrader_username` - MT5 account username
- `metatrader_password` - MT5 account password
- `metatrader_server` - MT5 server address
- `metatrader_filepath` - Path to MT5 terminal executable
- `discord_key` - Discord bot token (optional)

### Timeframes
Supported timeframes are defined in `static_content/timeframes.json`:
- Minutes: M1, M5, M15, M30
- Hours: H1, H4, H8
- Days: D1
- Weeks: W1
- Months: MN1

## Testing

The included test strategy provides a basic example:
- Compares current and previous close prices
- Generates buy/sell signals with 1-2% profit targets
- Demonstrates the strategy interface pattern

Run the bot and select "Test Strategy" to see it in action.

## Next Steps & Roadmap

### Planned Features
- [ ] Backtesting framework
- [ ] Risk management system
- [ ] Multiple strategy execution
- [ ] Real-time trading execution
- [ ] Performance analytics dashboard
- [ ] More technical indicators (RSI, MACD, Bollinger Bands)

### Integration Targets
- [x] MetaTrader 5 (fully implemented)
- [ ] Binance API
- [ ] Coinbase API
- [ ] Interactive Brokers

## Support & Resources

### Documentation
- **TODO** MT5 documentation, python docs
- [YouTube Channel](https://youtube.com/@tradeoxy) - Video tutorials
- [Medium Articles](https://medium.com/@appnologyjames) - Technical deep dives

### Community
- [Discord Server](https://discord.com/channels/1143837842745864192/1143837843274342432) - Live support and discussion
- GitHub Issues - Bug reports and feature requests

### Educational Content
1. **Building Development Environment** - Setup with TA-Lib and AI tools
2. **Data Retrieval** - Getting market data from MetaTrader
3. **Technical Indicators** - Adding RSI, MACD, Bollinger Bands
4. **Strategy Development** - Creating and testing custom strategies

## License

This project is licensed under the terms included in the LICENSE file.

---
