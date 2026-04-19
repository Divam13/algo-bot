"use client";

import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import React, { useEffect, useRef } from 'react';

interface ChartProps {
    data: { time: string; value: number }[];
    trades?: Array<{
        datetime?: string;           // Backend uses this
        entry_time?: string;         // Alternative field
        type?: string;               // Backend uses 'BUY' or 'SELL'
        direction?: string;          // Alternative field
        price: number;
    }>;
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        areaTopColor?: string;
        areaBottomColor?: string;
    };
}

export const TradingViewChart: React.FC<ChartProps> = ({ data, trades, colors = {} }) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Create Chart
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: colors.backgroundColor || 'transparent' },
                textColor: colors.textColor || '#D9D9D9',
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.2)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.2)' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(197, 203, 206, 0.2)',
            },
            timeScale: {
                borderColor: 'rgba(197, 203, 206, 0.2)',
                timeVisible: true,
            },
        });

        const isPositive = data.length > 0 && data[data.length - 1].value >= data[0].value;
        const primaryColor = isPositive ? '#22c55e' : '#ef4444'; // Green or Red

        // Add Area Series (Lightweight Charts v4 API)
        // Cast to 'any' to avoid TS conflicts if types are mismatched, but this method exists in v4 runtime
        const series = (chart as any).addAreaSeries({
            lineColor: primaryColor,
            topColor: isPositive ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)',
            bottomColor: isPositive ? 'rgba(34, 197, 94, 0.0)' : 'rgba(239, 68, 68, 0.0)',
            lineWidth: 2,
        });

        // Format Data
        // TradingView requires sorted data
        const sortedData = [...data].sort((a, b) => {
            const tA = typeof a.time === 'number' ? a.time : new Date(a.time).getTime();
            const tB = typeof b.time === 'number' ? b.time : new Date(b.time).getTime();
            return tA - tB;
        });

        // Unique-ify by time
        const uniqueData: { time: number; value: number }[] = [];
        const seenTimes = new Set<number>();

        sortedData.forEach(d => {
            let timeVal: number;
            if (typeof d.time === 'number') {
                timeVal = d.time;
            } else {
                timeVal = new Date(d.time).getTime() / 1000;
            }

            // Check valid number and not duplicate
            if (!isNaN(timeVal) && !seenTimes.has(timeVal)) {
                seenTimes.add(timeVal);
                uniqueData.push({
                    time: timeVal,
                    value: d.value
                });
            }
        });

        series.setData(uniqueData);

        // Add Trade Markers
        if (trades && trades.length > 0) {


            const markers = trades
                .filter(trade => {
                    // Backend uses 'type' (BUY/SELL) and 'datetime' fields
                    const hasType = trade && (trade.type || trade.direction);
                    const hasTime = trade && (trade.datetime || trade.entry_time);
                    return hasType && hasTime;
                })
                .map(trade => {
                    // Get timestamp - backend uses 'datetime' field
                    const timeField = trade.datetime || trade.entry_time || '';
                    const tradeTime = new Date(timeField).getTime() / 1000;

                    // Get type - backend uses 'type' with values 'BUY' or 'SELL'
                    const tradeType = (trade.type || trade.direction || '').toLowerCase();
                    const isBuy = (tradeType === 'buy' || tradeType === 'long');

                    return {
                        time: tradeTime,
                        position: isBuy ? 'belowBar' : 'aboveBar',
                        color: isBuy ? '#00ff7f' : '#ff3366', // Cyber green / Cyber red
                        shape: 'circle', // Use circles for cleaner look
                        text: '' // Remove text to reduce clutter
                    };
                })
                .filter(marker => !isNaN(marker.time)); // Filter out invalid timestamps

            if (markers.length > 0) {
                (series as any).setMarkers(markers);
            }
        }

        chart.timeScale().fitContent();

        // Resize Handler
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data, trades, colors]);

    return (
        <div ref={chartContainerRef} className="w-full h-[400px]" />
    );
};
