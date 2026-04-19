
import backtrader as bt
import pandas as pd
from datetime import datetime

class MomentumStrategy(bt.Strategy):
    """
    Momentum Strategy based on Simple Moving Average Crossover.
    
    Buy signal: Short SMA crosses above Long SMA (Golden Cross).
    Sell signal: Short SMA crosses below Long SMA (Death Cross).
    """
    
    params = (
        ('short_period', 20),
        ('long_period', 50),
        ('order_pct', 0.95), # Uses 95% of available cash for orders
        ('ticker', 'Unknown')
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        
        # Add moving averages
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long_period)
        
        # Crossover indicator
        self.crossover = bt.indicators.CrossOver(self.sma_short, self.sma_long)

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()}, {txt}') # Commented out to reduce noise during optimization/testing

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending if so, we cannot send a 2nd one
        if self.position:
            # We are in the market
            if self.crossover < 0: # Death Cross: Short SMA crosses below Long SMA
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.close() # Sell entire position
        else:
            # We are not in the market
            if self.crossover > 0: # Golden Cross: Short SMA crosses above Long SMA
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                # Calculate size to buy
                # size = int(self.broker.get_cash() / self.dataclose[0] * self.params.order_pct)
                # self.buy(size=size) 
                self.buy() # Default uses fixed stake if not specified, usually need sizer for dynamic

