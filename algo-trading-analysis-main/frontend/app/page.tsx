'use client';

import { useEffect, useState } from 'react';
import { api, type Strategy, type BacktestResult } from '@/lib/api';
import { TradingViewChart } from '@/components/TradingViewChart';
import { Activity, BarChart3, Clock, TrendingUp, Zap, ChevronRight, Play, Terminal, Cpu, Shield } from 'lucide-react';

export default function Home() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [selectedDataSource, setSelectedDataSource] = useState<string>('equity_1min');
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const data = await api.listStrategies();
      setStrategies(data);
      if (data.length > 0) {
        setSelectedStrategy(data[0].id);
      }
    } catch (err) {
      setError('Connection refused: Backend [::8000] unreachable.');
    }
  };

  const runBacktest = async () => {
    if (!selectedStrategy) return;

    setBacktestRunning(true);
    setError('');

    try {
      const status = await api.runBacktest({
        strategy_id: selectedStrategy,
        data_source: selectedDataSource,
        max_bars: 2000,
      });

      let completed = false;
      while (!completed) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const currentStatus = await api.getBacktestStatus(status.job_id);

        if (currentStatus.status === 'completed') {
          const backtestResult = await api.getBacktestResult(status.job_id);
          setResult(backtestResult);
          completed = true;
        } else if (currentStatus.status === 'failed') {
          setError(currentStatus.message);
          completed = true;
        }
      }
    } catch (err: any) {
      setError(err.message || 'Backtest Execution Failed');
    } finally {
      setBacktestRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-black text-gray-300 font-rajdhani selection:bg-cyber-green selection:text-black">
      {/* Background Grid */}
      <div className="fixed inset-0 pointer-events-none z-0 opacity-20"
        style={{ backgroundImage: 'linear-gradient(rgba(0, 255, 127, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 127, 0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      <div className="relative z-10 max-w-[1800px] mx-auto p-6 space-y-8">

        {/* Header */}
        <header className="flex justify-between items-end border-b border-cyber-green/30 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-2 py-0.5 bg-cyber-green text-black font-orbitron font-bold text-xs">SYS.ONLINE</span>
              <span className="text-cyber-green/50 font-mono text-xs">V.2.0.45</span>
            </div>
            <h1 className="text-5xl font-orbitron font-black text-white tracking-widest uppercase flex items-center gap-4">
              ALGO<span className="text-cyber-green">BOT</span>
            </h1>
            <p className="text-cyber-green/70 font-mono mt-1 text-sm tracking-widest">
              QUANTITATIVE EXECUTION PROTOCOL
            </p>
          </div>
          <div className="flex gap-8">
            <StatSmall label="LATENCY" value="1.2ms" />
            <StatSmall label="UPTIME" value="99.99%" />
            <StatSmall label="MARKET" value="OPEN" color="text-cyber-green" />
          </div>
        </header>

        <main className="grid grid-cols-12 gap-8">

          {/* Sidebar - Controls */}
          <div className="col-span-12 lg:col-span-3 space-y-6">

            {/* Strategy Select */}
            <div className="border border-cyber-green/30 bg-cyber-darkgreen backdrop-blur-md p-0">
              <div className="bg-cyber-green/10 p-3 border-b border-cyber-green/30 flex justify-between items-center">
                <h2 className="font-orbitron text-cyber-green font-bold tracking-wider">STRATEGY.SELECT</h2>
                <Cpu className="w-4 h-4 text-cyber-green" />
              </div>
              <div className="p-4 space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
                {strategies.map((strategy) => (
                  <button
                    key={strategy.id}
                    onClick={() => setSelectedStrategy(strategy.id)}
                    className={`w-full text-left p-3 border transition-all duration-150 relative group ${selectedStrategy === strategy.id
                      ? 'border-cyber-green bg-cyber-green/20 text-white'
                      : 'border-white/10 text-gray-400 hover:border-cyber-green/50 hover:text-cyber-green'
                      }`}
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-bold font-orbitron">{strategy.name}</span>
                      {selectedStrategy === strategy.id && <div className="w-2 h-2 bg-cyber-green animate-pulse" />}
                    </div>
                    <p className="text-[10px] mt-1 opacity-70 font-mono uppercase truncate">{strategy.category}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="border border-cyber-green/30 bg-cyber-darkgreen p-4">
              <button
                onClick={runBacktest}
                disabled={backtestRunning || !selectedStrategy}
                className="w-full py-4 bg-cyber-green hover:bg-[#00cc66] text-black font-orbitron font-bold text-lg tracking-widest transition-all clip-path-polygon disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(0,255,127,0.4)]"
                style={{ clipPath: 'polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px)' }}
              >
                {backtestRunning ? 'EXECUTING...' : 'INITIATE BACKTEST_'}
              </button>

              {error && (
                <div className="mt-4 p-3 border border-cyber-red/50 bg-cyber-red/10 text-cyber-red font-mono text-xs">
                  [ERROR]: {error}
                </div>
              )}
            </div>

            <div className="border border-white/10 p-4 font-mono text-xs text-gray-500 space-y-2">
              <div className="flex justify-between">
                <span>ENGINE:</span>
                <span className="text-cyber-green">ONLINE</span>
              </div>
              <div className="flex justify-between">
                <span>DATA_FEED:</span>
                <span className="text-cyber-green uppercase">{selectedDataSource}</span>
              </div>

              {/* Data Source Selector */}
              <div className="pt-2 border-t border-white/10 mt-2">
                <span className="block mb-1 opacity-70">SELECT DATA:</span>
                <select
                  value={selectedDataSource}
                  onChange={(e) => setSelectedDataSource(e.target.value)}
                  className="w-full bg-black border border-cyber-green/30 text-cyber-green text-xs p-1 font-mono focus:outline-none focus:border-cyber-green"
                  disabled={backtestRunning}
                >
                  <option value="equity_1min">EQUITY_1MIN (FINE)</option>
                  <option value="weekly">WEEKLY (MACRO)</option>
                  <option value="options_minute">OPTIONS_MIN (VOL)</option>
                </select>
              </div>
              <div className="flex justify-between">
                <span>RISK_MODE:</span>
                <span className="text-yellow-500">AGGRESSIVE</span>
              </div>
            </div>

          </div>

          {/* Main Display */}
          <div className="col-span-12 lg:col-span-9 space-y-6">

            {/* Chart Container */}
            <div className="border border-cyber-green/30 bg-black/50 backdrop-blur-sm relative h-[600px] flex flex-col">
              <div className="absolute top-0 left-0 border-t-2 border-l-2 border-cyber-green w-4 h-4" />
              <div className="absolute top-0 right-0 border-t-2 border-r-2 border-cyber-green w-4 h-4" />
              <div className="absolute bottom-0 left-0 border-b-2 border-l-2 border-cyber-green w-4 h-4" />
              <div className="absolute bottom-0 right-0 border-b-2 border-r-2 border-cyber-green w-4 h-4" />

              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-black/80">
                <h3 className="font-orbitron text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-cyber-green" />
                  PERFORMANCE VISUALIZER // {selectedStrategy || 'NO_SIGNAL'}
                </h3>
                {result && (
                  <div className="flex gap-6 font-mono">
                    <span className={result.metrics.total_return >= 0 ? "text-cyber-green" : "text-cyber-red"}>
                      PNL: {(result.metrics.total_return * 100).toFixed(2)}%
                    </span>
                    <span className="text-gray-400">
                      EQ: ${result.metrics.final_value.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex-1 relative">
                {result ? (
                  <TradingViewChart
                    data={result.equity_curve.map(pt => ({ time: pt.datetime, value: pt.value }))}
                    trades={result.trades}
                    colors={{
                      backgroundColor: '#0a0f0a',
                      lineColor: '#00ff7f',
                      textColor: '#4b5563',
                      areaTopColor: 'rgba(0, 255, 127, 0.2)',
                      areaBottomColor: 'rgba(0, 255, 127, 0.0)',
                    }}
                  />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-cyber-green/20">
                    <Terminal className="w-24 h-24 mb-4" />
                    <p className="font-orbitron tracking-widest">AWAITING EXECUTION COMMAND</p>
                  </div>
                )}
              </div>
            </div>

            {/* Metrics Grid */}
            {result && (
              <div className="grid grid-cols-4 gap-4">
                <MetricBox label="SHARPE" value={result.metrics.sharpe_ratio.toFixed(2)} />
                <MetricBox label="DRAWDOWN" value={`${(result.metrics.max_drawdown * 100).toFixed(2)}%`} isRisk />
                <MetricBox label="WIN RATE" value={`${(result.metrics.win_rate * 100).toFixed(1)}%`} />
                <MetricBox label="PROFIT FACTOR" value={result.metrics.profit_factor.toFixed(2)} />

                <MetricBox label="TRADES" value={result.metrics.num_trades.toString()} />
                <MetricBox label="SORTINO" value={result.metrics.sortino_ratio.toFixed(2)} />
                <MetricBox label="CALMAR" value={result.metrics.calmar_ratio.toFixed(2)} />
                <MetricBox label="ALPHA" value="0.45" dim />
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  );
}

function StatSmall({ label, value, color = "text-white" }: { label: string, value: string, color?: string }) {
  return (
    <div className="flex flex-col items-end">
      <span className="text-[10px] text-gray-500 font-mono tracking-wider">{label}</span>
      <span className={`font-orbitron font-bold ${color}`}>{value}</span>
    </div>
  )
}

function MetricBox({ label, value, isRisk, dim }: { label: string, value: string, isRisk?: boolean, dim?: boolean }) {
  return (
    <div className={`border p-4 bg-black/50 backdrop-blur transition-all hover:bg-white/5 group relative overflow-hidden ${isRisk ? 'border-cyber-red/30' : 'border-cyber-green/30'
      }`}>
      <div className={`absolute left-0 top-0 bottom-0 w-1 transition-all group-hover:w-full group-hover:opacity-10 opacity-0 ${isRisk ? 'bg-cyber-red' : 'bg-cyber-green'
        }`} />

      <p className="text-[10px] text-gray-500 font-orbitron tracking-widest mb-1 relative z-10">{label}</p>
      <p className={`text-2xl font-bold font-mono relative z-10 ${isRisk ? 'text-cyber-red' : dim ? 'text-gray-500' : 'text-cyber-green'
        }`}>
        {value}
      </p>
    </div>
  )
}
