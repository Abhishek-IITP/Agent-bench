'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { spring } from '@/lib/motion';

interface MissionBriefProps {
  score: number;
  totalTasks: number;
  totalRuns: number;
  activeAgents: number;
}

function Counter({ to, duration = 1500, decimals = 1 }: { to: number; duration?: number; decimals?: number }) {
  const [val, setVal] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const step = (timestamp: number) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 5); // Smooth quintic easing
      setVal(ease * to);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [to, duration]);
  
  return <>{val.toFixed(decimals)}</>;
}

export default function MissionBrief({ score, totalTasks, totalRuns, activeAgents }: MissionBriefProps) {
  return (
    <section className="relative h-screen max-h-screen flex flex-col justify-between overflow-hidden bg-black px-8 py-16">
      {/* Background Pulse Waveform */}
      <div className="absolute inset-0 flex items-center justify-center opacity-[0.03] pointer-events-none">
        <div className="flex items-end gap-1.5 w-full max-w-6xl px-12">
          {Array.from({ length: 80 }).map((_, i) => {
            const height = Math.abs(Math.sin(i * 0.12) * Math.cos(i * 0.05)) * 240 + Math.random() * 40 + 20;
            return (
              <motion.div
                key={i}
                className="flex-1 bg-white rounded-t"
                initial={{ height: 0 }}
                animate={{ height: `${height}px` }}
                transition={{
                  height: { delay: i * 0.008, duration: 1.2, ease: [0.16, 1, 0.3, 1] }
                }}
              />
            );
          })}
        </div>
      </div>
      
      {/* Top Header info */}
      <div className="flex items-center justify-between shrink-0">
        <span className="text-[9px] font-mono text-white/35 uppercase tracking-widest block">
          AgentBench System Briefing
        </span>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="text-[9px] font-mono uppercase tracking-widest text-emerald-400 font-semibold">
            System Live
          </span>
        </div>
      </div>

      {/* Hero Display Metric (Central block) */}
      <div className="flex-1 flex flex-col justify-center items-center text-center space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="text-[10px] font-mono text-white/20 uppercase tracking-widest">
            Composite System Reliability
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, ...spring }}
          className="relative"
        >
          <h1 className="metric-giant text-white select-text">
            <Counter to={score} decimals={1} />
            <span className="font-sans text-2xl font-light text-white/30 ml-2">%</span>
          </h1>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <p className="font-sans text-white/55 text-sm tracking-wide font-light max-w-md leading-relaxed">
            Composite accuracy metric calculated dynamically from all concurrent active task benchmarks.
          </p>
        </motion.div>
      </div>

      {/* Footer stat metrics */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-16 border-t border-white/5 pt-8 shrink-0 w-full max-w-5xl mx-auto"
      >
        <StatItem label="Scenarios Catalogued" value={totalTasks} suffix="tasks" />
        <StatItem label="Evaluations Observed" value={totalRuns.toLocaleString()} suffix="runs" />
        <StatItem label="Active Model Entities" value={activeAgents} suffix="models" />
      </motion.div>
    </section>
  );
}

function StatItem({ label, value, suffix }: { label: string; value: string | number; suffix: string }) {
  return (
    <div className="space-y-1 text-center md:text-left">
      <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest block">{label}</span>
      <div className="flex items-baseline justify-center md:justify-start gap-1">
        <span className="font-mono text-2xl font-bold text-white leading-none">{value}</span>
        <span className="text-[10px] font-mono text-white/30 uppercase">{suffix}</span>
      </div>
    </div>
  );
}
