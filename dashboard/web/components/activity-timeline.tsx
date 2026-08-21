'use client';

import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';
import type { Run } from '@/lib/types';
import { formatDistanceToNow } from '@/lib/utils';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

interface ActivityTimelineProps {
  runs: Run[];
}

export default function ActivityTimeline({ runs }: ActivityTimelineProps) {
  const recentRuns = runs.slice(0, 5); // Focus on top 5 for visual clarity and pacing
  
  return (
    <section className="min-h-screen flex items-center justify-center bg-black px-8 py-24">
      <div className="max-w-4xl w-full space-y-16">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4"
        >
          <span className="text-[9px] font-mono text-white/35 uppercase tracking-widest block">
            01 / Live Activity Ledger
          </span>
          <h2 className="chapter-title text-white select-text">
            What happened while you were away
          </h2>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Real-time feed observing agent evaluations. Chronological stream tracking runtime success, failures, and execution latencies.
          </p>
        </motion.div>
        
        {/* Timeline thread */}
        <motion.div
          variants={staggerContainer(0.08, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="relative pl-8 space-y-8"
        >
          {/* Timeline center line */}
          <div className="absolute left-[3px] top-4 bottom-4 w-px bg-white/10" />
          
          {recentRuns.map((run, idx) => (
            <ActivityItem key={run.id} run={run} index={idx} />
          ))}
        </motion.div>
        
        {/* Observatory log anchor */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="pt-4 border-t border-white/5 flex justify-end"
        >
          <Link
            href="/runs"
            className="inline-flex items-center gap-2 text-[10px] font-mono text-white/50 hover:text-white uppercase tracking-widest transition-colors group no-underline"
          >
            <span>View Full Chronological Stream</span>
            <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

function ActivityItem({ run, index }: { run: Run; index: number }) {
  const statusConfig = {
    success: { color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400', label: 'Success' },
    failure: { color: 'text-red-500 bg-red-500/10 border-red-500/20', dot: 'bg-red-500', label: 'Failed' },
    timeout: { color: 'text-amber-500 bg-amber-500/10 border-amber-500/20', dot: 'bg-amber-400', label: 'Timeout' },
    error: { color: 'text-red-500 bg-red-500/10 border-red-500/20', dot: 'bg-red-500', label: 'Error' },
  };
  
  const statusKey = (run.status === 'success' || run.success) ? 'success' : (run.status === 'timeout' ? 'timeout' : 'failure');
  const config = statusConfig[statusKey] || statusConfig.failure;
  const accuracyPercentage = (run.score !== null && run.score !== undefined)
    ? Math.round(Number(run.score) * 100)
    : (run.success ? 100 : 0);

  return (
    <motion.div
      variants={slideUp}
      className="relative flex items-start gap-6 group"
    >
      {/* Timeline Node marker */}
      <div className="absolute -left-[32px] top-1.5 flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-black border-2 border-white/20 group-hover:border-white transition-all duration-300" />
      </div>

      {/* Content wrapper */}
      <div className="flex-1 flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 bg-[#050505] border border-white/5 hover:border-white/10 rounded-xl transition-all duration-300">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <span className="font-sans text-sm font-semibold text-white">
              {run.agent_name}
            </span>
            <span className="text-white/25 font-mono text-[10px]">→</span>
            <span className="font-mono text-xs text-white/55 truncate">
              {run.task_id}
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-[10px] font-mono text-white/35">
            <span>RUN ID: {run.id.substring(0, 8)}</span>
            <span className="w-1 h-1 rounded-full bg-white/10" />
            <span>DURATION: {run.duration.toFixed(1)}s</span>
            <span className="w-1 h-1 rounded-full bg-white/10" />
            <span>{formatDistanceToNow(new Date(run.created_at))}</span>
          </div>
        </div>

        {/* Status indicator and Investigation trigger */}
        <div className="flex items-center gap-4 self-start md:self-auto shrink-0">
          <span className={`px-2 py-0.5 rounded text-[9px] font-mono uppercase tracking-wider border ${config.color}`}>
            {config.label}
          </span>
          <div className="text-right">
            <span className="font-mono text-lg font-bold text-white block">
              {accuracyPercentage}%
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
          </div>
          <Link
            href={`/runs/${run.id}`}
            className="p-2 border border-white/5 hover:border-white/15 bg-transparent rounded-lg text-white/40 hover:text-white transition-all no-underline"
            title="Investigate Execution Trace"
          >
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
