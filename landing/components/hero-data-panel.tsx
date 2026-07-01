"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const runResults = [1, 1, 1, 0, 1, 1, 1, 1, 0, 1];

const replaySteps = [
  { t: "0.0s", cmd: "ls /workspace/data" },
  { t: "0.3s", cmd: "cat instruction.md" },
  { t: "1.2s", cmd: "grep -rl database ." },
  { t: "2.1s", cmd: "sort > output.txt" },
  { t: "2.5s", cmd: "✓ output.txt written" },
];

function CountUp({ target, duration = 1400 }: { target: number; duration?: number }) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [target, duration]);
  return <>{value}</>;
}

export function HeroDataPanel() {
  const [activeStep, setActiveStep] = useState(0);
  const [bars, setBars] = useState<number[]>(new Array(10).fill(0));
  const successRate = runResults.filter(Boolean).length;

  useEffect(() => {
    const t = setTimeout(() => setBars(runResults), 500);
    const interval = setInterval(() => setActiveStep((s) => (s + 1) % replaySteps.length), 1400);
    return () => { clearTimeout(t); clearInterval(interval); };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: 32, scale: 0.96 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 90, damping: 20, delay: 0.5 }}
      style={{
        background: "rgba(18,22,31,0.8)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        border: "1px solid var(--border-subtle)",
        borderRadius: 12,
        padding: "1.5rem",
        width: "100%",
        maxWidth: 360,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <span className="text-label-mono font-mono-custom">find-database-files</span>
        <span className="pill pill-healthy">● Healthy</span>
      </div>

      {/* Reliability score */}
      <div style={{ marginBottom: "1.25rem" }}>
        <span className="text-label-mono font-mono-custom" style={{ display: "block", marginBottom: 4 }}>
          reliability score
        </span>
        <span
          className="font-mono-custom"
          style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--signal)", display: "block" }}
        >
          0.<CountUp target={87} />
        </span>
      </div>

      {/* Histogram */}
      <div style={{ marginBottom: "1.25rem" }}>
        <span className="text-label-mono font-mono-custom" style={{ display: "block", marginBottom: 8 }}>
          10 independent runs
        </span>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 48 }}>
          {bars.map((passed, i) => (
            <motion.div
              key={i}
              initial={{ height: 0 }}
              animate={{ height: passed ? "100%" : "35%" }}
              transition={{ type: "spring", stiffness: 200, damping: 20, delay: i * 0.06 + 0.5 }}
              style={{
                flex: 1,
                borderRadius: 3,
                backgroundColor: passed ? "var(--status-healthy)" : "var(--status-broken)",
                opacity: passed ? 0.85 : 0.5,
              }}
            />
          ))}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6 }}>
          <span className="font-mono-custom" style={{ fontSize: "0.6875rem", color: "var(--status-healthy)" }}>
            {successRate} passed
          </span>
          <span className="font-mono-custom" style={{ fontSize: "0.6875rem", color: "var(--status-broken)" }}>
            {10 - successRate} failed
          </span>
        </div>
      </div>

      {/* Replay trace */}
      <div>
        <span className="text-label-mono font-mono-custom" style={{ display: "block", marginBottom: 8 }}>
          replay trace
        </span>
        <div
          style={{
            backgroundColor: "var(--bg-void)",
            borderRadius: 8,
            padding: "0.75rem",
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          {replaySteps.map((step, i) => (
            <motion.div
              key={i}
              animate={{ opacity: activeStep === i ? 1 : 0.3 }}
              transition={{ duration: 0.3 }}
              style={{ display: "flex", alignItems: "center", gap: 12 }}
            >
              <span
                className="font-mono-custom"
                style={{ fontSize: "0.6875rem", color: "var(--text-muted)", width: 36, flexShrink: 0 }}
              >
                {step.t}
              </span>
              <span
                className="font-mono-custom"
                style={{
                  fontSize: "0.6875rem",
                  color: activeStep === i ? "var(--signal)" : "var(--text-muted)",
                }}
              >
                {step.cmd}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
