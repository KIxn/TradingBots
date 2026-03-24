from abc import abstractmethod
from backtesting import Strategy


class BaseStrategy(Strategy):
    """
    Base class for all strategies. Extends backtesting.Strategy so each strategy
    works for both backtesting and live trading from a single implementation.

    Subclasses must implement:
        - init(): precompute indicators (used by backtesting engine)
        - next(): define buy/sell logic (used by backtesting engine)
        - get_live_signal(df): extract signal from latest OHLCV data (used by live trading)

    get_live_signal receives a pandas DataFrame with columns Open/High/Low/Close
    and must return a dict: {'decision': 'buy'|'sell'|'hold', 'entry': float|None, 'exit': float|None}
    """

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def next(self):
        pass

    @classmethod
    @abstractmethod
    def get_live_signal(cls, df) -> dict:
        """
        Called by the live trading loop each iteration.
        Receives the latest OHLCV DataFrame and returns a signal dict.
        No backtesting engine involved — pure data in, signal out.
        """
        pass
