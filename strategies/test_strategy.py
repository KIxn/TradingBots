from strategies.base_strategy import BaseStrategy


class TestStrategy(BaseStrategy):
    """
    Simple 2-candle mean reversion strategy.
    - Previous close > current close → BUY (price dropped, expect bounce)
    - Previous close < current close → SELL (price rose, expect reversal)
    """

    def init(self):
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

    @classmethod
    def get_live_signal(cls, df) -> dict:
        prev_close = df["Close"].iloc[-2]
        curr_close = df["Close"].iloc[-1]

        if prev_close > curr_close:
            return {"decision": "buy", "entry": curr_close * 1.01, "exit": curr_close * 1.02}
        elif prev_close < curr_close:
            return {"decision": "sell", "entry": curr_close * 0.99, "exit": curr_close * 0.98}
        else:
            return {"decision": "hold", "entry": None, "exit": None}
