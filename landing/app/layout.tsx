import type { Metadata } from "next";
import { Geist, Geist_Mono, Instrument_Serif } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AgentBench — Reliability-First AI Agent Benchmarking",
  description:
    "AgentBench measures how consistently AI agents solve real terminal tasks — across repeated runs, isolated Docker environments, and full replay traces.",
  openGraph: {
    title: "AgentBench — Reliability-First AI Agent Benchmarking",
    description:
      "Solving it once isn't solving it. AgentBench measures consistency, reproducibility, and benchmark health — not just accuracy.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AgentBench — Reliability-First AI Agent Benchmarking",
    description: "Solving it once isn't solving it.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${instrumentSerif.variable}`}
        style={{
          backgroundColor: "#0a0a0f",
          color: "#efefef",
          fontFamily: "var(--font-geist-sans)",
          WebkitFontSmoothing: "antialiased",
          overflowX: "hidden",
          margin: 0,
        }}
      >
        {/* Film grain overlay */}
        <div
          aria-hidden="true"
          style={{
            position: "fixed",
            inset: 0,
            pointerEvents: "none",
            zIndex: 9999,
            opacity: 0.035,
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C%2Fsvg%3E\")",
            backgroundRepeat: "repeat",
            backgroundSize: "180px 180px",
          }}
        />
        {children}
      </body>
    </html>
  );
}
