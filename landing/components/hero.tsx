"use client";
import { motion } from "framer-motion";
import { ArrowDown, GitBranch } from "lucide-react";
import Image from "next/image";

export function Hero() {
  return (
    <section
      className="relative min-h-screen w-full flex flex-col justify-between overflow-hidden bg-bg-void pt-28 pb-12 lg:pt-32"
    >
      {/* Soft background ambient gradient */}
      <div
        className="absolute inset-0 pointer-events-none -z-10"
        style={{
          background: "radial-gradient(circle at 75% 25%, rgba(74,222,128,0.06) 0%, transparent 60%)",
        }}
      />

      <div className="max-w-6xl mx-auto px-6 w-full my-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          
          {/* Left Column: Heading, Subheading & CTAs (Claude-inspired minimal typography) */}
          <div className="lg:col-span-5 flex flex-col gap-6 text-left relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col gap-5"
            >
              {/* Status Badge */}
              <div>
                <span
                  className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-[10px] font-mono tracking-wider text-white/80 uppercase"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-[#4ade80] animate-pulse" />
                  In active development · Week 1 of 4
                </span>
              </div>

              {/* Title */}
              <h1
                className="font-display text-5xl md:text-6xl lg:text-7xl text-white tracking-tight leading-[1.05]"
              >
                AgentBench
              </h1>

              {/* Subheading */}
              <p
                className="font-display text-xl md:text-2xl text-white/70 leading-normal"
              >
                Solving it once isn&apos;t solving it.
              </p>

              {/* Description */}
              <p className="text-sm md:text-base text-white/55 leading-relaxed max-w-md">
                Measures how <em className="not-italic text-white/85">consistently</em> AI agents solve terminal tasks — with reliability metrics, replay traces, and benchmark health analysis.
              </p>
            </motion.div>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-wrap items-center gap-4 mt-2"
            >
              <a
                href="#waitlist"
                className="px-6 py-3 rounded-full text-sm font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-emerald-500/10 hover:shadow-emerald-500/20"
                style={{
                  backgroundColor: "#4ade80",
                  color: "#050508",
                }}
              >
                Join the waitlist →
              </a>
              <a
                href="https://github.com/Abhishek-IITP/Agent-bench"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-3 rounded-full text-sm font-medium text-white/70 hover:text-white border border-white/10 hover:border-white/20 hover:bg-white/5 transition-all duration-200"
              >
                <GitBranch size={14} />
                GitHub
              </a>
            </motion.div>
          </div>

          {/* Right Column: Hero Image with Browser Mockup Frame */}
          <div className="lg:col-span-7 w-full flex justify-center relative z-10">
            <motion.div
              initial={{ opacity: 0, scale: 0.98, y: 24 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="relative w-full rounded-2xl border border-white/10 bg-white/[0.02] p-1.5 md:p-2 backdrop-blur-3xl shadow-2xl"
            >
              {/* Soft ambient glow behind the mockup */}
              <div className="absolute -inset-4 bg-emerald-500/5 rounded-[2rem] filter blur-2xl pointer-events-none -z-10 animate-pulse" style={{ animationDuration: '4s' }} />

              {/* Browser Header Bar */}
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/5 bg-white/[0.01] rounded-t-xl">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500/40" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/40" />
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500/40" />
                </div>
                <div className="flex items-center gap-1.5 px-3 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] font-mono text-white/40 tracking-wider">
                  agentbench.ai/dashboard
                </div>
                <div className="w-12" /> {/* spacer to balance controls */}
              </div>

              {/* Image Window */}
              <div className="relative w-full overflow-hidden bg-[#0c0c14] rounded-b-xl aspect-[16/10] flex items-center justify-center p-1 md:p-2">
                <Image
                  src="/hero.png"
                  alt="AgentBench UI Screenshot"
                  width={1200}
                  height={750}
                  className="w-full h-full object-contain rounded-md"
                  priority
                />
              </div>
            </motion.div>
          </div>

        </div>
      </div>

      {/* Bottom Bar: Polaris/Claude style footer inside the hero */}
      <div className="w-full max-w-6xl mx-auto px-6 mt-12 lg:mt-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="flex flex-col sm:flex-row justify-between items-center gap-4 py-6 border-t border-white/10"
        >
          <span
            className="font-mono text-[10px] tracking-wider text-white/35 text-center sm:text-left"
          >
            A reliability-first alternative to: Terminal Bench · SWE-bench · GAIA · HumanEval
          </span>
          <span
            className="font-mono text-[10px] tracking-wider text-white/35"
          >
            AgentBench © 2026
          </span>
        </motion.div>
      </div>

      {/* Scroll cue */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        className="absolute bottom-4 left-50% -translate-x-1/2 hidden md:block text-white/50"
        style={{ left: "50%" }}
      >
        <motion.div
          animate={{ y: [0, 5, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <ArrowDown size={14} />
        </motion.div>
      </motion.div>
    </section>
  );
}
