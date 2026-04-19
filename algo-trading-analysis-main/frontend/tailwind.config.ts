import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        rajdhani: ['Rajdhani', 'sans-serif'],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        cyber: {
          black: "#0a0f0a",
          green: "#00ff7f",
          red: "#ff3232",
          darkgreen: "rgba(0, 20, 0, 0.8)",
        }
      },
    },
  },
  plugins: [],
} satisfies Config;
