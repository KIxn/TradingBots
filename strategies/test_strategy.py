from strategies.base_strategy import BaseStrategy


class TestStrategy(BaseStrategy):
    """
    Simple 2-candle mean reversion strategy.
    - Previous close > current close → BUY (price dropped, expect bounce)
    - Previous close < current close → SELL (price rose, expect reversal)
    """

    def init(self):
        # No indicators to precompute — logic is purely price comparison
        pass

    def next(self):
        prev_close = self.data.Close[-2]
        curr_close = self.data.Close[-1]

        if prev_close > curr_close:
            self._signal_buy = True
            self._signal_sell = False
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif prev_close < curr_close:
            self._signal_buy = False
            self._signal_sell = True
            if not self.position.is_short:
                self.position.close()
                self.sell()
        else:
            self._signal_buy = False
            self._signal_sell = False
