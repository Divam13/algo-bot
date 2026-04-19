#include "../include/strategy.hpp"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>


// ======================== Strategy Implementations ========================

// Simple Momentum Strategy
SimpleMomentum::SimpleMomentum(int fast, int slow)
    : fast_period(fast), slow_period(slow) {}

int SimpleMomentum::get_signal(const std::vector<Bar> &data, int i) {
  if (i < slow_period)
    return 0;

  // Calculate simple moving averages
  double fast_sum = 0, slow_sum = 0;
  for (int j = 0; j < fast_period; j++)
    fast_sum += data[i - j].close();
  for (int j = 0; j < slow_period; j++)
    slow_sum += data[i - j].close();

  double fast_ma = fast_sum / fast_period;
  double slow_ma = slow_sum / slow_period;

  // Previous bar MAs
  double prev_fast_sum = 0, prev_slow_sum = 0;
  for (int j = 1; j <= fast_period; j++)
    prev_fast_sum += data[i - j].close();
  for (int j = 1; j <= slow_period; j++)
    prev_slow_sum += data[i - j].close();

  double prev_fast_ma = prev_fast_sum / fast_period;
  double prev_slow_ma = prev_slow_sum / slow_period;

  // Crossover logic
  if (fast_ma > slow_ma && prev_fast_ma <= prev_slow_ma)
    return 1; // Buy signal
  if (fast_ma < slow_ma && prev_fast_ma >= prev_slow_ma)
    return -1; // Sell signal

  return 0; // Hold
}

// Buy & Hold Strategy
int BuyAndHold::get_signal(const std::vector<Bar> &data, int i) {
  return (i == slow_period) ? 1 : 0; // Buy once and hold
}

// Mean Reversion Strategy (Ornstein-Uhlenbeck)
MeanReversion::MeanReversion(int lookback, double entry_z, double exit_z)
    : lookback_period(lookback), entry_threshold(entry_z),
      exit_threshold(exit_z) {}

int MeanReversion::get_signal(const std::vector<Bar> &data, int i) {
  if (i < lookback_period)
    return 0;

  // Calculate mean and std dev
  double sum = 0;
  for (int j = 0; j < lookback_period; j++) {
    sum += data[i - j].close();
  }
  double mean = sum / lookback_period;

  double variance = 0;
  for (int j = 0; j < lookback_period; j++) {
    double diff = data[i - j].close() - mean;
    variance += diff * diff;
  }
  double std_dev = std::sqrt(variance / lookback_period);

  // Calculate Z-Score
  double z_score = (data[i].close() - mean) / std::max(std_dev, 1e-6);

  // Mean reversion logic
  if (z_score < -entry_threshold)
    return 1; // Oversold - Buy
  if (z_score > entry_threshold)
    return -1; // Overbought - Sell
  if (std::abs(z_score) < exit_threshold)
    return 0; // Exit signal

  return 0; // Hold current position
}

// ======================== Backtest Engine ========================

BacktestResponse Engine::run(const BacktestRequest &req) {
  BacktestResponse response;
  response.set_job_id(req.job_id());

  double cash = req.config().initial_capital();
  double holdings = 0;
  double equity = cash;
  int position = 0; // 0 = neutral, 1 = long, -1 = short

  std::vector<double> equity_curve;
  std::vector<double> returns_series;
  std::vector<Trade> trades;

  double entry_price = 0;

  // Select strategy based on config
  std::unique_ptr<Strategy> strategy;
  std::string strategy_id = req.config().strategy_id();

  if (strategy_id == "simple_momentum") {
    strategy = std::make_unique<SimpleMomentum>(10, 30);
  } else if (strategy_id == "buy_and_hold") {
    strategy = std::make_unique<BuyAndHold>();
  } else if (strategy_id == "mean_reversion") {
    strategy = std::make_unique<MeanReversion>(60, 2.0, 0.5);
  } else {
    // Default to momentum
    strategy = std::make_unique<SimpleMomentum>(10, 30);
  }

  const auto &data = req.data();
  std::vector<Bar> data_vec = vector_from_proto(data);

  // Main backtest loop
  for (size_t i = 1; i < data_vec.size(); ++i) {
    double price = data_vec[i].close();
    int signal = strategy->get_signal(data_vec, i);

    double commission = req.config().commission_rate();
    double slippage = req.config().slippage_bps() / 10000.0;

    // Execution Logic
    if (signal == 1 && position == 0) {
      // BUY: Enter long position
      double adjusted_price = price * (1.0 + slippage);
      double quantity = (cash * 0.99) / adjusted_price;

      if (quantity > 0) {
        holdings = quantity;
        double cost = quantity * adjusted_price * (1.0 + commission);
        cash -= cost;
        position = 1;
        entry_price = adjusted_price;

        // Log trade
        Trade trade;
        trade.set_type("BUY");
        trade.set_price(adjusted_price);
        trade.set_quantity(quantity);
        trade.set_timestamp(data_vec[i].timestamp());
        trade.set_pnl(0);
        trades.push_back(trade);

        auto *trade_msg = response.add_trades();
        *trade_msg = trade;
      }
    } else if (signal == -1 && position == 1) {
      // SELL: Exit long position
      double adjusted_price = price * (1.0 - slippage);
      double proceeds = holdings * adjusted_price * (1.0 - commission);
      double pnl = proceeds - (holdings * entry_price);

      cash += proceeds;
      holdings = 0;
      position = 0;

      // Log trade
      Trade trade;
      trade.set_type("SELL");
      trade.set_price(adjusted_price);
      trade.set_quantity(holdings);
      trade.set_timestamp(data_vec[i].timestamp());
      trade.set_pnl(pnl);
      trades.push_back(trade);

      auto *trade_msg = response.add_trades();
      *trade_msg = trade;
    }

    // Update equity
    double current_equity = cash + (holdings * price);
    equity_curve.push_back(current_equity);

    // Calculate returns
    if (!equity_curve.empty() && equity_curve.size() > 1) {
      double ret = (current_equity - equity_curve[equity_curve.size() - 2]) /
                   equity_curve[equity_curve.size() - 2];
      returns_series.push_back(ret);
    }

    equity = current_equity;

    // Add equity point to response
    auto *point = response.add_equity_curve();
    point->set_timestamp(data_vec[i].timestamp());
    point->set_equity(equity);
  }

  // Calculate metrics
  double total_return = (equity - req.config().initial_capital()) /
                        req.config().initial_capital();
  response.set_total_return(total_return);

  // Sharpe Ratio
  double sharpe = calculate_sharpe_ratio(returns_series);
  response.set_sharpe_ratio(sharpe);

  // Max Drawdown
  double max_dd = calculate_max_drawdown(equity_curve);
  response.set_max_drawdown(max_dd);

  // Win Rate
  double win_rate = calculate_win_rate(trades);
  response.set_win_rate(win_rate);

  // Total Trades
  response.set_total_trades(trades.size());

  response.set_success(true);
  response.set_message("C++ Backtest Completed Successfully");

  std::cout << "✅ Backtest completed: "
            << "Return=" << (total_return * 100) << "%, "
            << "Sharpe=" << sharpe << ", "
            << "MaxDD=" << (max_dd * 100) << "%, "
            << "Trades=" << trades.size() << std::endl;

  return response;
}

// Helper: Calculate Sharpe Ratio
double Engine::calculate_sharpe_ratio(const std::vector<double> &returns) {
  if (returns.size() < 2)
    return 0.0;

  double mean_return =
      std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();

  double variance = 0.0;
  for (double ret : returns) {
    variance += (ret - mean_return) * (ret - mean_return);
  }
  double std_dev = std::sqrt(variance / returns.size());

  if (std_dev < 1e-10)
    return 0.0;

  // Annualize (assuming daily returns)
  double sharpe = (mean_return / std_dev) * std::sqrt(252.0);
  return sharpe;
}

// Helper: Calculate Maximum Drawdown
double Engine::calculate_max_drawdown(const std::vector<double> &equity_curve) {
  if (equity_curve.size() < 2)
    return 0.0;

  double peak = equity_curve[0];
  double max_dd = 0.0;

  for (double equity : equity_curve) {
    if (equity > peak) {
      peak = equity;
    }
    double drawdown = (peak - equity) / peak;
    if (drawdown > max_dd) {
      max_dd = drawdown;
    }
  }

  return max_dd;
}

// Helper: Calculate Win Rate
double Engine::calculate_win_rate(const std::vector<Trade> &trades) {
  if (trades.empty())
    return 0.0;

  int winning_trades = 0;
  int total_completed_trades = 0;

  for (const auto &trade : trades) {
    if (trade.type() == "SELL") {
      total_completed_trades++;
      if (trade.pnl() > 0) {
        winning_trades++;
      }
    }
  }

  if (total_completed_trades == 0)
    return 0.0;
  return static_cast<double>(winning_trades) / total_completed_trades;
}

// Helper: Convert protobuf repeated field to std::vector
std::vector<Bar> Engine::vector_from_proto(
    const google::protobuf::RepeatedPtrField<Bar> &proto_data) {
  return std::vector<Bar>(proto_data.begin(), proto_data.end());
}
