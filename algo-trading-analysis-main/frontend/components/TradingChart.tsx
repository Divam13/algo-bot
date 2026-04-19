"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  BarData,
  LineData,
  Time,
} from "lightweight-charts";

interface TradingChartProps {
  chartType: "candlestick" | "bar" | "line" | "area";
}

export default function TradingChart({ chartType }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick" | "Bar" | "Line" | "Area"> | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#131722" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { color: "#1e222d" },
        horzLines: { color: "#1e222d" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: "#2B2B43",
      },
      rightPriceScale: {
        borderColor: "#2B2B43",
      },
      crosshair: {
        mode: 1,
        vertLine: {
          width: 1,
          color: "#758696",
          style: 3,
        },
        horzLine: {
          width: 1,
          color: "#758696",
          style: 3,
        },
      },
    });

    chartRef.current = chart;

    // Load sample data (this will be replaced with actual data from backend)
    loadSampleData().then((data) => {
      createSeries(chart, chartType, data);
      setIsLoading(false);
    });

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, []);

  // Update series when chart type changes
  useEffect(() => {
    if (chartRef.current && !isLoading) {
      // Remove old series
      if (seriesRef.current) {
        chartRef.current.removeSeries(seriesRef.current);
      }

      // Load and create new series
      loadSampleData().then((data) => {
        if (chartRef.current) {
          createSeries(chartRef.current, chartType, data);
        }
      });
    }
  }, [chartType, isLoading]);

  const createSeries = (
    chart: IChartApi,
    type: "candlestick" | "bar" | "line" | "area",
    data: any[]
  ) => {
    let series: ISeriesApi<"Candlestick" | "Bar" | "Line" | "Area">;

    switch (type) {
      case "candlestick":
        series = chart.addCandlestickSeries({
          upColor: "#26a69a",
          downColor: "#ef5350",
          borderVisible: false,
          wickUpColor: "#26a69a",
          wickDownColor: "#ef5350",
        });
        series.setData(data as CandlestickData[]);
        break;

      case "bar":
        series = chart.addBarSeries({
          upColor: "#26a69a",
          downColor: "#ef5350",
          openVisible: true,
          thinBars: false,
        });
        series.setData(data as BarData[]);
        break;

      case "line":
        series = chart.addLineSeries({
          color: "#2962FF",
          lineWidth: 2,
        });
        series.setData(
          data.map((d) => ({ time: d.time, value: d.close })) as LineData[]
        );
        break;

      case "area":
        series = chart.addAreaSeries({
          topColor: "rgba(41, 98, 255, 0.4)",
          bottomColor: "rgba(41, 98, 255, 0.0)",
          lineColor: "rgba(41, 98, 255, 1)",
          lineWidth: 2,
        });
        series.setData(
          data.map((d) => ({ time: d.time, value: d.close })) as LineData[]
        );
        break;
    }

    seriesRef.current = series;
    chart.timeScale().fitContent();
  };

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#131722] z-10 rounded-lg">
          <div className="text-gray-400">Loading chart...</div>
        </div>
      )}
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
}

// Sample data generator - this will be replaced with actual data from your backend
async function loadSampleData(): Promise<CandlestickData[]> {
  // Try to load from data directory first
  try {
    const response = await fetch("/api/data");
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log("Using sample data, backend not available");
  }

  // Generate sample OHLCV data
  const data: CandlestickData[] = [];
  const startDate = new Date("2024-01-01");
  let basePrice = 45000;

  for (let i = 0; i < 365; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    // Random walk with some volatility
    const change = (Math.random() - 0.48) * 1000;
    basePrice += change;

    const open = basePrice + (Math.random() - 0.5) * 200;
    const close = basePrice + (Math.random() - 0.5) * 200;
    const high = Math.max(open, close) + Math.random() * 300;
    const low = Math.min(open, close) - Math.random() * 300;

    data.push({
      time: (date.getTime() / 1000) as Time,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
    });
  }

  return data;
}
