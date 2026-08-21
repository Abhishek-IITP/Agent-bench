"use client";
import { motion } from "framer-motion";
import { staggerContainer, fadeUp } from "@/lib/motion";

const questions = [
  "Was it reproducible?",
  "Was the task flaky?",
  "Was the model consistent?",
  "Was evaluation deterministic?",
  "How much did it cost?",
  "Is the benchmark itself still healthy?",
];

const leaderboard = [
  { model: "GPT-5",   score: "91%" },
  { model: "Claude",  score: "89%" },
  { model: "Gemini",  score: "84%" },
];

export function Problem() {
  return (
    <section id="why" className="py-18 relative overflow-hidden bg-bg-void">
      <div className="max-w-6xl mx-auto px-6">

        {/* Section header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="max-w-3xl mx-auto text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-label-mono mb-6">
            The Problem
          </motion.p>
          <motion.h2
            variants={fadeUp}
            className="font-display text-display-l text-text-primary"
          >
            Every benchmark shows you a number. None of them tell you if you can trust it.
          </motion.h2>
        </motion.div>

        {/* Two column layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 lg:gap-20 items-start">

          {/* Left — fake leaderboard */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ type: "spring", stiffness: 100, damping: 20 }}
          >
            <p className="text-label-mono mb-4">Current benchmarks report</p>
            <div className="glass-card overflow-hidden p-0">
              <div className="flex items-center gap-2 px-5 py-3 border-b border-border-subtle">
                <span className="w-2.5 h-2.5 rounded-full bg-status-broken opacity-70" />
                <span className="w-2.5 h-2.5 rounded-full bg-status-flaky opacity-70" />
                <span className="w-2.5 h-2.5 rounded-full bg-status-healthy opacity-70" />
                <span className="font-mono-custom text-xs text-text-muted ml-2">benchmark_results.json</span>
              </div>
              <div className="p-5 space-y-3">
                {leaderboard.map((row, i) => (
                  <motion.div
                    key={row.model}
                    initial={{ opacity: 0, x: -16 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 + 0.2 }}
                    className="flex items-center justify-between"
                  >
                    <span className="font-mono-custom text-sm text-text-secondary">{row.model}</span>
                    <span className="font-mono-custom text-sm font-bold text-text-primary">{row.score}</span>
                  </motion.div>
                ))}
                <div className="pt-3 border-t border-border-subtle">
                  <span className="font-mono-custom text-xs text-text-muted">And nothing else.</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right — unanswered questions */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-60px" }}
          >
            <p className="text-label-mono mb-4">What this doesn&apos;t tell you</p>
            <div>
              {questions.map((q, i) => (
                <motion.div
                  key={i}
                  variants={fadeUp}
                  className="flex items-center gap-3 py-3 border-b border-border-subtle last:border-0"
                >
                  <span className="text-sm font-mono-custom shrink-0 text-status-broken">?</span>
                  <span className="text-sm text-text-secondary">{q}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
