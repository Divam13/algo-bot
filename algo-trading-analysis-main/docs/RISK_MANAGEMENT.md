# Risk Management Rules

## Core Principles

Risk management is the cornerstone of successful algorithmic trading. These rules are designed to protect capital and ensure long-term sustainability.

## 1. Position Sizing Rules

### Maximum Position Size
- **Single Position**: No more than 10% of total capital in any single position
- **Sector Exposure**: No more than 30% of total capital in any single sector
- **Strategy Allocation**: Diversify across multiple strategies

### Risk Per Trade
- **Standard Risk**: 1-2% of capital per trade
- **High Conviction**: Maximum 3% of capital per trade
- **Never Exceed**: 5% of capital in any single trade

### Formula
```python
Position_Size = (Total_Capital × Risk_Percentage) / Entry_Price
Max_Position_Value = Total_Capital × 0.10  # 10% limit

Actual_Position = min(Position_Size, Max_Position_Value / Entry_Price)
```

## 2. Stop-Loss Rules

### Mandatory Stop-Loss
- **Every position MUST have a stop-loss order**
- Set immediately upon entry
- Never remove or widen a stop-loss
- Can tighten (move closer) as position becomes profitable

### Stop-Loss Levels

#### Momentum Strategy
- **Initial Stop**: 5-7% below entry price for long positions
- **Trailing Stop**: Move stop to breakeven after 3% profit
- **Profit Protection**: Trail stop by 50% of maximum profit

#### Mean Reversion Strategy
- **Initial Stop**: 3-5% below entry price for long positions
- **Time-based**: Exit if position hasn't moved favorably within 3 days
- **Volatility-adjusted**: Use ATR (Average True Range) based stops

### Mathematical Example
```python
# Long position
Entry_Price = 100
Stop_Loss_Percentage = 0.05  # 5%
Stop_Loss_Price = Entry_Price × (1 - Stop_Loss_Percentage)
                = 100 × 0.95 = 95

# Risk calculation
Position_Size = 100 shares
Risk_Per_Share = Entry_Price - Stop_Loss_Price = 5
Total_Risk = Position_Size × Risk_Per_Share = 500
```

## 3. Portfolio-Level Risk Controls

### Maximum Drawdown Limits
- **Alert Level**: -10% from portfolio peak
- **Reduce Risk**: -15% from portfolio peak (reduce position sizes by 50%)
- **Stop Trading**: -20% from portfolio peak (close all positions, reassess)

### Daily Loss Limits
- **Maximum Daily Loss**: 5% of portfolio value
- **Action**: Stop trading for the day if limit hit
- **Recovery Period**: Review and analyze before resuming

### Correlation Management
- Avoid highly correlated positions
- Target correlation coefficient < 0.7 between positions
- Diversify across different asset classes and sectors

## 4. Leverage Rules

### Conservative Approach (Recommended)
- **No Leverage**: Trade with 1:1 ratio for beginners
- **Maximum Leverage**: 2:1 for experienced traders
- **Never Exceed**: 3:1 under any circumstances

### Margin Requirements
- Maintain minimum 40% cash buffer
- Never use more than 60% of available margin
- Reduce leverage during high volatility periods

## 5. Market Condition Adjustments

### High Volatility (VIX > 20)
- Reduce position sizes by 30-50%
- Widen stop-losses to avoid premature exits
- Increase cash allocation
- Consider reducing number of open positions

### Low Liquidity
- Reduce position sizes for illiquid assets
- Use limit orders instead of market orders
- Account for wider bid-ask spreads
- Ensure ability to exit positions quickly

### Market Stress Events
- Reduce overall exposure by 50%
- Increase cash reserves
- Tighten risk parameters
- Monitor positions more frequently

## 6. Time-Based Rules

### Holding Period Limits
- **Momentum Strategy**: Maximum 30 days per position
- **Mean Reversion Strategy**: Maximum 10 days per position
- **Force Exit**: If no clear profit/loss after max holding period

### Review Intervals
- **Daily**: Check all open positions and stops
- **Weekly**: Review overall portfolio performance and risk metrics
- **Monthly**: Comprehensive strategy and parameter review

## 7. Win/Loss Management

### Profit Taking
- **Scale Out**: Take partial profits at predetermined levels
- **25% at 5% profit**
- **50% at 10% profit**
- **Remaining at trailing stop**

### Loss Management
- Accept small losses quickly
- Never average down on losing positions
- Review and learn from each losing trade
- Keep a trading journal for analysis

## 8. Risk Metrics Monitoring

### Key Metrics to Track

#### Sharpe Ratio
- **Target**: > 1.0
- **Good**: > 1.5
- **Excellent**: > 2.0
- **Formula**: (Returns - Risk_Free_Rate) / Std_Deviation

#### Maximum Drawdown
- **Acceptable**: < 20%
- **Warning**: 20-30%
- **Unacceptable**: > 30%

#### Win Rate
- **Momentum Strategy**: Target 40-50%
- **Mean Reversion Strategy**: Target 55-65%
- **Minimum**: > 35% for any strategy

#### Profit Factor
- **Formula**: Gross_Profit / Gross_Loss
- **Target**: > 1.5
- **Good**: > 2.0

### Monitoring Dashboard
```python
# Example risk metrics calculation
def calculate_risk_metrics(trades_df):
    returns = trades_df['returns']
    
    sharpe_ratio = returns.mean() / returns.std() * sqrt(252)
    max_drawdown = (returns.cumsum() - returns.cumsum().cummax()).min()
    win_rate = (returns > 0).sum() / len(returns)
    profit_factor = returns[returns > 0].sum() / abs(returns[returns < 0].sum())
    
    return {
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'profit_factor': profit_factor
    }
```

## 9. Emergency Procedures

### Circuit Breakers
Implement automatic position closure when:
1. Portfolio loses more than 5% in a single day
2. A single position loses more than 10%
3. Maximum drawdown exceeds 20%
4. Margin call warning received

### Crisis Management
1. **Assess**: Quickly evaluate market conditions
2. **Hedge**: Consider protective positions if appropriate
3. **Reduce**: Scale down positions immediately
4. **Review**: Analyze what went wrong
5. **Adapt**: Adjust parameters before resuming

## 10. Psychological Risk Management

### Trading Rules
- Never trade based on emotions
- Follow the system strictly
- No revenge trading after losses
- Take breaks after significant losses
- Maintain work-life balance

### Decision Making
- Use checklists before every trade
- Document reasoning for each trade
- Review decisions regularly
- Learn from both wins and losses
- Stay disciplined and patient

## Implementation Checklist

Before going live with any strategy:

- [ ] All stop-loss levels calculated and programmed
- [ ] Position sizing formulas verified
- [ ] Maximum drawdown alerts configured
- [ ] Daily loss limits set
- [ ] Portfolio correlation checked
- [ ] Risk metrics dashboard ready
- [ ] Emergency procedures documented
- [ ] Backtesting completed with risk rules
- [ ] Walk-forward validation performed
- [ ] Paper trading tested for at least 1 month

## Compliance and Regulatory Considerations

### Record Keeping
- Maintain detailed logs of all trades
- Document strategy changes and parameters
- Keep audit trail for regulatory compliance
- Store data for minimum 5 years

### Reporting
- Regular performance reports
- Risk exposure summaries
- Compliance with trading limits
- Incident reports for significant losses

## Continuous Improvement

### Regular Reviews
- Monthly: Strategy performance and risk metrics
- Quarterly: Parameter optimization and refinement
- Annually: Comprehensive strategy overhaul

### Adaptation
- Adjust risk parameters based on market conditions
- Update strategies based on performance data
- Incorporate lessons learned from losses
- Stay informed about market changes

---

**Remember**: The goal is not to eliminate risk, but to manage it intelligently. Consistent, disciplined risk management is more important than any trading strategy.
