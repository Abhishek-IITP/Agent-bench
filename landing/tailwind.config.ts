import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "bg-void":        "#0a0a0f",
        "bg-deep":        "#0f0f1a",
        "bg-elevated":    "#15151f",
        "border-subtle":  "rgba(255,255,255,0.07)",
        "border-glow":    "rgba(255,255,255,0.18)",
        "text-primary":   "#efefef",
        "text-secondary": "rgba(255,255,255,0.55)",
        "text-muted":     "rgba(255,255,255,0.3)",
        "signal":         "#4ade80",
        "status-healthy":   "#4ade80",
        "status-flaky":     "#fbbf24",
        "status-broken":    "#f87171",
        "status-saturated": "#60a5fa",
        "status-trivial":   "#a78bfa",
      },
      fontFamily: {
        display: ["var(--font-instrument-serif)", "Georgia", "serif"],
        "mono-custom": ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
