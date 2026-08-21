"use client";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { DASHBOARD_ROUTES } from "@/lib/config";
import { ExternalLink, PlayCircle, Trophy, BarChart3 } from "lucide-react";

export function CTA() {
  return (
    <section id="dashboard-cta" className="py-20 bg-bg-void relative overflow-hidden">


      <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="rounded-3xl border border-white/10 bg-white/[0.02] p-8 md:p-14 backdrop-blur-2xl shadow-2xl relative"
        >
          <motion.p variants={fadeUp} className="text-xs font-mono uppercase tracking-widest text-emerald-400 mb-4">
            Production Benchmark Suite Ready
          </motion.p>

          <motion.h2 variants={fadeUp} className="font-display text-4xl md:text-5xl text-white mb-6 tracking-tight leading-tight">
            Ready to test your AI agents with empirical precision?
          </motion.h2>

          <motion.p variants={fadeUp} className="text-white/60 text-base md:text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
            Run deterministic benchmark evaluations, track reliability variance across repeated runs, and explore live agent rankings on the AgentBench dashboard.
          </motion.p>

          <motion.div
            variants={fadeUp}
            className="flex flex-wrap items-center justify-center gap-4"
          >
            <a
              href={DASHBOARD_ROUTES.home}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full text-base font-semibold transition-all duration-200 hover:scale-[1.03] active:scale-[0.98] shadow-xl shadow-emerald-500/20 no-underline"
              style={{
                backgroundColor: "#4ade80",
                color: "#050508",
              }}
            >
              <BarChart3 size={18} />
              Launch Web Dashboard
              <ExternalLink size={16} />
            </a>

            <a
              href={DASHBOARD_ROUTES.test}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-base font-medium text-white border border-white/20 hover:border-emerald-400/50 hover:bg-white/5 transition-all duration-200 no-underline"
            >
              <PlayCircle size={18} className="text-emerald-400" />
              Test Your Model
            </a>

            <a
              href={DASHBOARD_ROUTES.leaderboard}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-base font-medium text-white/80 hover:text-white border border-white/10 hover:border-white/20 hover:bg-white/5 transition-all duration-200 no-underline"
            >
              <Trophy size={18} className="text-amber-400" />
              View Leaderboard
            </a>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
