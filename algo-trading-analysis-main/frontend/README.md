# Algo Trading Frontend

A modern Next.js dashboard for visualizing trading data with TradingView Lightweight Charts.

## Features

- 📊 **Multiple Chart Types**: Candlestick, Bar, Line, and Area charts
- 🌙 **Dark Mode**: Beautiful dark theme optimized for trading
- ⚡ **Fast & Responsive**: Built with Next.js 15 and React 19
- 📈 **TradingView Charts**: Professional-grade charting library
- 🎨 **Modern UI**: Tailwind CSS with gradient effects

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Production Build

```bash
npm run build
npm start
```

## Data Integration

The dashboard automatically loads data from:

1. **API Route**: `/api/data` - Serves CSV files from the `data/` directory
2. **Sample Data**: Falls back to generated sample data if no CSV files are found

### CSV Format

Place your CSV files in the `data/` directory with the following columns:

- `date` (required)
- `time` (optional)
- `open` (required)
- `high` (required)
- `low` (required)
- `close` (required)
- `volume` (optional)

Example CSV format:

```csv
date,time,open,high,low,close,volume
2024-01-01,09:00:00,45000,45500,44800,45200,1000000
```

## Chart Types

Switch between different chart types using the buttons at the top:

- **Candlestick**: Shows OHLC data with green/red candles
- **Bar**: Shows OHLC data as bars
- **Line**: Shows closing prices as a line
- **Area**: Shows closing prices with filled area

## Technology Stack

- **Next.js 15**: React framework with App Router
- **React 19**: Latest React with Server Components
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lightweight Charts**: TradingView's charting library

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── data/
│   │       └── route.ts       # API endpoint for data
│   ├── globals.css            # Global styles
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Home page
├── components/
│   └── TradingChart.tsx       # Chart component
├── public/                    # Static assets
└── package.json
```

## Customization

### Chart Colors

Edit the chart colors in `components/TradingChart.tsx`:

```typescript
upColor: "#26a69a",    // Green for bullish
downColor: "#ef5350",  // Red for bearish
```

### Theme Colors

Edit the theme in `app/globals.css`:

```css
:root {
  --background: #0a0e27;
  --foreground: #e4e4e7;
}
```

## Performance

- Charts are optimized for 1000+ data points
- Automatic responsive sizing
- Efficient re-rendering on chart type changes

## License

MIT
