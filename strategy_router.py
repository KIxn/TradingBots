import importlib
import inspect
import pkgutil
import strategies
from strategies.base_strategy import BaseStrategy


def _discover_strategies() -> dict:
    """
    Auto-discovers all BaseStrategy subclasses in the strategies/ package.
    No manual registration needed — just create a file in strategies/.
    """
    strategy_map = {}
    for _, module_name, _ in pkgutil.iter_modules(strategies.__path__):
        if module_name == 'base_strategy':
            continue
        module = importlib.import_module(f'strategies.{module_name}')
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                # Use the class name converted to title case as the display name
                # e.g. TestStrategy -> "Test Strategy"
                name = _class_name_to_display(obj.__name__)
                strategy_map[name] = obj
    return strategy_map


def _class_name_to_display(class_name: str) -> str:
    """Converts CamelCase class name to spaced display name. e.g. TestStrategy -> Test Strategy"""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', class_name)


# Built once at import time
STRATEGY_MAP = _discover_strategies()


def get_strategy_class(strategy_name: str):
    if strategy_name not in STRATEGY_MAP:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(STRATEGY_MAP.keys())}")
    return STRATEGY_MAP[strategy_name]


def get_strategy_names() -> list:
    return list(STRATEGY_MAP.keys())


def strategy_router(platform, symbol, timeframe, strategy_name):
    """
    Runs the strategy on live data and returns a signal dict.
    """
    if not platform:
        raise ValueError('The platform is None')
    if not symbol:
        raise ValueError('The symbol is None')
    if not timeframe:
        raise ValueError('The timeframe is None')

    import helper_functions as helpers
    from backtesting import Backtest

    strategy_class = get_strategy_class(strategy_name)

    dataframe = helpers.get_data(platform, symbol, timeframe)
    dataframe = dataframe.rename(columns={
        'candle_open': 'Open', 'candle_high': 'High',
        'candle_low': 'Low', 'candle_close': 'Close',
    })
    if 'timestamp' in dataframe.columns:
        dataframe = dataframe.set_index('timestamp')

    bt = Backtest(dataframe, strategy_class, cash=100_000, trade_on_close=True)
    bt.run()

    # Get live signal from last bar
    strategy_instance = strategy_class()
    strategy_instance._data = type('Data', (), {
        'Close': dataframe['Close'].values,
        'Open': dataframe['Open'].values,
        'High': dataframe['High'].values,
        'Low': dataframe['Low'].values,
    })()
    strategy_instance.init()
    strategy_instance.next()
    return strategy_instance.get_signal()
