
import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    """
    Mean Reversion Strategy based on Bollinger Bands.
    
    Buy signal: Price closes below the lower Bollinger Band (Oversold).
    Sell signal: Price closes above the upper Bollinger Band (Overbought).
    """
    
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('order_pct', 0.95),
        ('ticker', 'Unknown')
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        
        # Bollinger Bands
        self.bband = bt.indicators.BollingerBands(
            self.datas[0], period=self.params.period, devfactor=self.params.devfactor)

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def next(self):
        if self.position:
            # Sell signal: Close > Upper Band
            if self.dataclose[0] > self.bband.lines.top[0]:
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.close()
        else:
            # Buy signal: Close < Lower Band
            if self.dataclose[0] < self.bband.lines.bot[0]:
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.buy()
