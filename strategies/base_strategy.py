from abc import abstractmethod
from backtesting import Strategy


class BaseStrategy(Strategy):
    """
    Base class for all strategies. Extends backtesting.Strategy so each strategy
    works for both backtesting and live trading from a single implementation.

    Subclasses must implement:
        - init(): precompute indicators
        - next(): define buy/sell logic using self.buy() / self.sell()

    For live trading, get_signal() translates the last bar into a signal dict.
    """

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def next(self):
        pass

    def get_signal(self) -> dict:
        """
        Called by the live trading loop after init().
        Runs next() on the latest data and returns a signal dict.
        """
        signal = {'decision': 'hold', 'entry': None, 'exit': None}
        close = self.data.Close[-1]

        # Temporarily capture what next() would do by checking position intent
        # Subclasses can override this for more precise live signal extraction
        prev_buy = getattr(self, '_signal_buy', False)
        prev_sell = getattr(self, '_signal_sell', False)

        if prev_buy:
            signal = {'decision': 'buy', 'entry': close * 1.01, 'exit': close * 1.02}
        elif prev_sell:
            signal = {'decision': 'sell', 'entry': close * 0.99, 'exit': close * 0.98}

        return signal
