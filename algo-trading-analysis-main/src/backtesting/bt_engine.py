
import backtrader as bt
import pandas as pd
from datetime import datetime

class PandasCSVData(bt.feeds.PandasData):
    """
    Custom Data Feed to handle the specific CSV format if needed,
    or just mapped correctly from standard Pandas DataFrames.
    """
    params = (
        ('datetime', None), # Datetime column name (None = Index)
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),
    )

class BacktestEngine:
    def __init__(self, initial_capital=100000.0, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.cerebro = bt.Cerebro()
        
        # Set initial capital
        self.cerebro.broker.setcash(self.initial_capital)
        
        # Set commission
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # Add Analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    def add_data(self, df: pd.DataFrame, name: str = "Stock"):
        """
        Add data to Cerebro. 
        Expects a DataFrame with a DateTime index and OHLCV columns.
        """
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'date' in df.columns or 'datetime' in df.columns:
                col = 'date' if 'date' in df.columns else 'datetime'
                df[col] = pd.to_datetime(df[col])
                df.set_index(col, inplace=True)
            else:
                raise ValueError("DataFrame must have a Datetime Index or a 'date' column")

        data = PandasCSVData(dataname=df)
        self.cerebro.adddata(data, name=name)

    def add_strategy(self, strategy_class, **kwargs):
        self.cerebro.addstrategy(strategy_class, **kwargs)

    def run(self):
        print(f'Starting Portfolio Value: {self.cerebro.broker.getvalue():.2f}')
        results = self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        print(f'Final Portfolio Value: {final_value:.2f}')
        
        strat = results[0]
        
        # Extract Metrics
        metrics = {
            'final_value': final_value,
            'total_return': (final_value - self.initial_capital) / self.initial_capital,
            'sharpe_ratio': strat.analyzers.sharpe.get_analysis().get('sharperatio', 0.0),
            'max_drawdown': strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0.0),
            'trades': strat.analyzers.trades.get_analysis()
        }
        
        return metrics
