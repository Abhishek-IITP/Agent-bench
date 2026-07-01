"use client";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { GlassCard } from "@/components/ui/glass-card";
import { Pill } from "@/components/ui/pill";

const replayLines = [
  { t: "0.0s", cmd: "ls /workspace/data" },
  { t: "0.3s", cmd: "grep -rl database ." },
  { t: "1.2s", cmd: "sort -u > output.txt" },
];

const failCategories = [
  { label: "Timeout",      pct: 38, color: "bg-status-flaky" },
  { label: "Reasoning",    pct: 27, color: "bg-status-broken" },
  { label: "Filesystem",   pct: 19, color: "bg-status-saturated" },
  { label: "Hallucination",pct: 16, color: "bg-status-trivial" },
];

export function MetricsBento() {
  return (
    <section id="metrics" className="py-20 bg-bg-void relative">
      <div className="max-w-6xl mx-auto px-6">

        {/* Header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="mb-14"
        >
          <motion.p variants={fadeUp} className="text-label-mono mb-4">
            What AgentBench measures
          </motion.p>
          <motion.h2 variants={fadeUp} className="font-display text-display-l text-text-primary max-w-2xl">
            Better measurements, not more tasks.
          </motion.h2>
        </motion.div>

        {/* Bento grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

          {/* 1 — Reliability Score (spans 2 cols) */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20 }}
            className="lg:col-span-2"
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">01 — Reliability Score</p>
              <p className="font-display text-2xl text-text-primary mb-3">
                Consistency across repeated runs, not luck.
              </p>
              <p className="text-sm text-text-secondary mb-5">
                Traditional benchmarks run a task once. AgentBench runs it 10 times and
                measures variance, confidence intervals, and consistency.
              </p>
              <div className="flex items-end gap-1.5 h-10">
                {[1,1,1,0,1,1,1,1,0,1].map((v, i) => (
                  <motion.div
                    key={i}
                    initial={{ height: 0 }}
                    whileInView={{ height: v ? "100%" : "35%" }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.05 + 0.3, type: "spring", stiffness: 200 }}
                    className={`flex-1 rounded-sm ${v ? "bg-status-healthy opacity-80" : "bg-status-broken opacity-45"}`}
                  />
                ))}
              </div>
              <div className="flex justify-between mt-2">
                <span className="font-mono-custom text-xs text-text-muted">Run 1</span>
                <span className="font-mono-custom text-xs text-signal">0.87 reliability</span>
              </div>
            </GlassCard>
          </motion.div>

          {/* 2 — Benchmark Health */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.1 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">02 — Benchmark Health</p>
              <p className="text-sm text-text-secondary mb-5">
                Tasks get classified automatically. Flaky, broken, trivial, or saturated — the benchmark evaluates itself.
              </p>
              <div className="flex flex-wrap gap-2">
                <Pill variant="healthy">Healthy</Pill>
                <Pill variant="flaky">Flaky</Pill>
                <Pill variant="broken">Broken</Pill>
                <Pill variant="trivial">Trivial</Pill>
                <Pill variant="saturated">Saturated</Pill>
              </div>
            </GlassCard>
          </motion.div>

          {/* 3 — Replay Traces */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.15 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">03 — Replay Traces</p>
              <p className="text-sm text-text-secondary mb-4">
                Every command, every output, every step. Full timeline per run.
              </p>
              <div className="rounded-lg bg-bg-void p-3 space-y-2">
                {replayLines.map((line, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className="font-mono-custom text-xs w-10 shrink-0 text-text-muted">{line.t}</span>
                    <span className="font-mono-custom text-xs text-signal">{line.cmd}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* 4 — Cost Aware */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.2 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">04 — Cost-Aware Metrics</p>
              <p className="text-sm text-text-secondary mb-5">
                Everyone compares accuracy. Nobody compares accuracy per dollar.
              </p>
              <div className="space-y-3">
                {[
                  { label: "Accuracy / $",      value: "0.87/$0.12" },
                  { label: "Accuracy / token",  value: "0.87/4.2k" },
                  { label: "Accuracy / minute", value: "0.87/1.3m" },
                ].map((row) => (
                  <div key={row.label} className="flex justify-between items-center">
                    <span className="font-mono-custom text-xs text-text-muted">{row.label}</span>
                    <span className="font-mono-custom text-xs font-bold text-text-primary">{row.value}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* 5 — Failure Taxonomy (spans 2 cols) */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.25 }}
            className="lg:col-span-2"
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">05 — Failure Taxonomy</p>
              <p className="font-display text-xl text-text-primary mb-2">
                Know <em className="not-italic">why</em> it failed, not just that it did.
              </p>
              <p className="text-sm text-text-secondary mb-5">
                Every failure is classified. Researchers can see if models consistently fail for the same reason.
              </p>
              <div className="space-y-3">
                {failCategories.map((cat, i) => (
                  <div key={cat.label} className="flex items-center gap-3">
                    <span className="w-24 text-xs font-mono-custom text-text-muted shrink-0">{cat.label}</span>
                    <div className="flex-1 h-1.5 rounded-full bg-border-subtle">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${cat.pct}%` }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.1 + 0.3, duration: 0.6 }}
                        className={`h-full rounded-full ${cat.color}`}
                      />
                    </div>
                    <span className="text-xs font-mono-custom w-8 text-right text-text-muted">{cat.pct}%</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

          {/* 6 — Benchmark Drift */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.3 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">06 — Benchmark Drift</p>
              <p className="text-sm text-text-secondary mb-4">
                When GPT goes from 40% to 95% in 6 months, AgentBench flags it.
              </p>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono-custom text-xs text-text-muted">Jan</span>
                <span className="font-mono-custom text-xs text-text-muted">Jun</span>
              </div>
              <div className="relative h-8">
                <svg viewBox="0 0 200 32" className="w-full h-full">
                  <motion.path
                    d="M 0 28 C 40 26 80 22 120 10 S 170 4 200 2"
                    stroke="#4ade80"
                    strokeWidth="1.5"
                    fill="none"
                    initial={{ pathLength: 0 }}
                    whileInView={{ pathLength: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.2, delay: 0.3 }}
                  />
                </svg>
              </div>
              <div className="mt-2">
                <span className="font-mono-custom text-xs text-status-flaky">⚠ drift detected</span>
              </div>
            </GlassCard>
          </motion.div>

          {/* 7 — Oracle / NOP */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.35 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">07 — Oracle / NOP Validation</p>
              <p className="text-sm text-text-secondary mb-4">
                Every task is validated before use. Passing requires solving it.
              </p>
              <div className="space-y-2">
                <div className="font-mono-custom text-sm text-status-healthy">✓ reference solution passes</div>
                <div className="font-mono-custom text-sm text-status-broken">✗ doing nothing fails</div>
              </div>
            </GlassCard>
          </motion.div>

          {/* 8 — Docker Isolation */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.4 }}
          >
            <GlassCard className="h-full p-6">
              <p className="text-label-mono mb-3">08 — Docker Isolation</p>
              <p className="text-sm text-text-secondary mb-5">
                Every run: same image, same filesystem, same inputs. Zero contamination.
              </p>
              <div className="space-y-2">
                {["Reproducible", "Deterministic", "Isolated", "Cheat-resistant"].map((tag) => (
                  <div key={tag} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-signal shrink-0" />
                    <span className="font-mono-custom text-xs text-text-muted">{tag}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
