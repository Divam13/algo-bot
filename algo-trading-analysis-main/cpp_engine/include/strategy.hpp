#pragma once

#include "backtest.pb.h" // Generated header
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>


using namespace alpha_engine;

// Base Strategy Class
class Strategy {
public:
  virtual int get_signal(const std::vector<Bar> &data, int current_idx) = 0;
  virtual ~Strategy() = default;
};

// Simple Momentum Strategy Implementation
class SimpleMomentum : public Strategy {
  int fast_period;
  int slow_period;

public:
  SimpleMomentum(int fast = 10, int slow = 30);
  int get_signal(const std::vector<Bar> &data, int i) override;
};

// Buy and Hold Strategy
class BuyAndHold : public Strategy {
  int slow_period = 30; // Needed for initial warmup

public:
  BuyAndHold() = default;
  int get_signal(const std::vector<Bar> &data, int i) override;
};

// Mean Reversion Strategy (Ornstein-Uhlenbeck based)
class MeanReversion : public Strategy {
  int lookback_period;
  double entry_threshold;
  double exit_threshold;

public:
  MeanReversion(int lookback = 60, double entry_z = 2.0, double exit_z = 0.5);
  int get_signal(const std::vector<Bar> &data, int i) override;
};

// Main Backtest Engine
class Engine {
public:
  BacktestResponse run(const BacktestRequest &req);

private:
  // Helper methods
  std::vector<Bar>
  vector_from_proto(const google::protobuf::RepeatedPtrField<Bar> &proto_data);

  // Metrics calculators
  double calculate_sharpe_ratio(const std::vector<double> &returns);
  double calculate_max_drawdown(const std::vector<double> &equity_curve);
  double calculate_win_rate(const std::vector<Trade> &trades);
};
