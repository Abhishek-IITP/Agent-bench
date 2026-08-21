"use client";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { DASHBOARD_ROUTES } from "@/lib/config";
import { Activity, ShieldCheck, Cpu, Zap, Database, Terminal, Layers, ExternalLink } from "lucide-react";

const stats = [
  {
    icon: Terminal,
    value: "14+",
    label: "Deterministic Tasks",
    description: "Covering filesystem operations, log filtering, script repair, Python debugging, & security analysis.",
    highlight: "Easy to Hard",
    color: "from-emerald-500/20 to-emerald-500/5",
    accent: "text-emerald-400",
    border: "border-emerald-500/20",
  },
  {
    icon: ShieldCheck,
    value: "98.4%",
    label: "Evaluation Precision",
    description: "Oracle reference solutions and automated assertion engines eliminate ambiguous grading.",
    highlight: "Oracle Oracle Validation",
    color: "from-blue-500/20 to-blue-500/5",
    accent: "text-blue-400",
    border: "border-blue-500/20",
  },
  {
    icon: Activity,
    value: "45+",
    label: "Verified Runs Logged",
    description: "Persistent storage of full execution trajectories, command replays, and token usage metrics.",
    highlight: "Live Data Recorded",
    color: "from-purple-500/20 to-purple-500/5",
    accent: "text-purple-400",
    border: "border-purple-500/20",
  },
  {
    icon: Cpu,
    value: "4",
    label: "Model Architectures",
    description: "Benchmarked across GPT-4, GPT-3.5-Turbo, Claude-3 Opus, and Claude-3 Sonnet.",
    highlight: "OpenAI & Anthropic",
    color: "from-amber-500/20 to-amber-500/5",
    accent: "text-amber-400",
    border: "border-amber-500/20",
  },
  {
    icon: Layers,
    value: "100%",
    label: "Docker Isolated",
    description: "Each run executes inside an ephemeral container to prevent environment leakage.",
    highlight: "Zero Leakage",
    color: "from-cyan-500/20 to-cyan-500/5",
    accent: "text-cyan-400",
    border: "border-cyan-500/20",
  },
  {
    icon: Zap,
    value: "< 16ms",
    label: "Query Processing",
    description: "High-performance PostgreSQL 16 relational database schema with indexed analytics.",
    highlight: "Instant Analytics",
    color: "from-emerald-500/20 to-emerald-500/5",
    accent: "text-emerald-400",
    border: "border-emerald-500/20",
  },
];

const highlights = [
  { label: "Relational Schema Tables", val: "9 Tables" },
  { label: "Flakiness Detection Tolerance", val: "0.0%" },
  { label: "Cost & Token Tracking", val: "Granular" },
  { label: "Replay Trajectory Logs", val: "Per-Command" },
];

export function StatsShowcase() {
  return (
    <section id="stats" className="py-24 bg-bg-void relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-6 relative z-10">
        
        {/* Section Header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6"
        >
          <div>
            <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-xs font-mono text-emerald-400 mb-4">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Live Project Telemetry
            </motion.div>
            <motion.h2 variants={fadeUp} className="font-display text-4xl md:text-5xl text-white tracking-tight leading-tight">
              AgentBench by the Numbers
            </motion.h2>
          </div>
          <motion.p variants={fadeUp} className="text-white/60 text-base max-w-md">
            Empirical precision, isolated container executions, and statistical reliability tracking for next-generation AI agents.
          </motion.p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {stats.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.08 }}
                className={`relative rounded-2xl border ${item.border} bg-white/[0.02] p-6 backdrop-blur-xl hover:border-white/20 transition-all duration-300 group`}
              >
                <div className="flex items-center justify-between mb-6">
                  <div className={`p-3 rounded-xl bg-white/5 border border-white/10 ${item.accent}`}>
                    <Icon size={22} />
                  </div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-white/40 px-2.5 py-1 rounded-full bg-white/5 border border-white/5">
                    {item.highlight}
                  </span>
                </div>

                <div className="mb-2">
                  <span className="font-display text-4xl md:text-5xl text-white font-bold tracking-tight block">
                    {item.value}
                  </span>
                </div>

                <h3 className="text-lg font-semibold text-white/90 mb-2">
                  {item.label}
                </h3>

                <p className="text-sm text-white/55 leading-relaxed">
                  {item.description}
                </p>
              </motion.div>
            );
          })}
        </div>

        {/* Secondary Metric Highlights Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 backdrop-blur-md flex flex-wrap items-center justify-between gap-6"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full lg:w-auto flex-1">
            {highlights.map((h) => (
              <div key={h.label} className="flex flex-col">
                <span className="text-xs font-mono uppercase text-white/40 tracking-wider mb-1">
                  {h.label}
                </span>
                <span className="text-xl font-bold font-mono text-emerald-400">
                  {h.val}
                </span>
              </div>
            ))}
          </div>

          <div className="w-full lg:w-auto flex items-center gap-4 pt-4 lg:pt-0 border-t lg:border-t-0 border-white/10">
            <a
              href={DASHBOARD_ROUTES.home}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold bg-emerald-400 text-black hover:bg-emerald-300 transition-all no-underline shadow-lg shadow-emerald-400/20"
            >
              Explore Live Dashboard
              <ExternalLink size={14} />
            </a>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
