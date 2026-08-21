'use client';

import React, { useState, useMemo } from 'react';
import { useRuns } from '@/lib/hooks';
import { formatCost, formatDistanceToNow } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpRight, Play, Terminal, ChevronDown, ChevronUp, Cpu, HelpCircle, Activity } from 'lucide-react';
import Link from 'next/link';
import { slideUp, staggerContainer } from '@/lib/motion';

export default function RunsPage() {
  const { data: runsData, loading, error, refetch } = useRuns({
    limit: 50,
    page: 1,
  });

  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  const runs = runsData?.items || [];

  // Filter runs based on selected status tag
  const filteredRuns = useMemo(() => {
    if (!filterStatus) return runs;
    return runs.filter(run => run.status === filterStatus);
  }, [runs, filterStatus]);

  if (loading && runs.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center space-y-4 font-mono text-xs text-white/35">
          <div className="w-8 h-8 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mx-auto" />
          <span>ESTABLISHING TELEMETRY FEED...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-24 text-center space-y-6">
        <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto text-red-500">
          <Terminal className="w-6 h-6" />
        </div>
        <p className="font-mono text-xs text-red-400">CONNECTION TO OBSERVATORY LOGS OFFLINE</p>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-black p-6 lg:p-12 space-y-12">
      
      {/* Editorial Navigation Brief */}
      <div className="border-b border-white/5 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-4">
          <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest block font-semibold">
            Chapter 03 // Execution Ledger
          </span>
          <h1 className="font-display text-5xl text-white tracking-tight leading-none">
            Observatory Streams
          </h1>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Live telemetry feed capturing agent execution runs. Deep dive into system step profiles, sandbox diagnostics, and token logs.
          </p>
        </div>

        {/* State Indicators (Minimal filtering controls) */}
        <div className="flex items-center gap-2 bg-[#050505] border border-white/5 p-1.5 rounded-xl self-start">
          {([null, 'success', 'failure', 'timeout'] as const).map((status) => (
            <button
              key={status ?? 'all'}
              onClick={() => setFilterStatus(status)}
              className={`px-3 py-1.5 rounded-lg text-[9px] font-mono uppercase tracking-wider transition-all border ${
                filterStatus === status
                  ? 'bg-white text-black border-white font-semibold'
                  : 'bg-transparent text-white/40 border-transparent hover:text-white'
              }`}
            >
              {status ?? 'All streams'}
            </button>
          ))}
        </div>
      </div>

      {/* Throughput Waveform (NASA Space Waveform) */}
      <div className="border border-white/5 bg-[#050505] p-5 rounded-xl space-y-4">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">Real-time throughput waveform</span>
        </div>
        <div className="h-16 flex items-end gap-1 opacity-20 pointer-events-none">
          {Array.from({ length: 120 }).map((_, i) => {
            const h = Math.abs(Math.sin(i * 0.1) * Math.cos(i * 0.04)) * 50 + Math.random() * 14;
            return (
              <div
                key={i}
                className="flex-1 bg-emerald-400 rounded-t"
                style={{ height: `${h}%` }}
              />
            );
          })}
        </div>
      </div>

      {/* Main Execution Log Streams */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-[9px] font-mono text-white/25 uppercase tracking-widest px-2">
          <span>Observed Streams</span>
          <span>{filteredRuns.length} Runs logged</span>
        </div>

        <motion.div
          variants={staggerContainer(0.06, 0.03)}
          initial="hidden"
          animate="visible"
          className="space-y-3"
        >
          {filteredRuns.map((run) => (
            <RunStreamCard
              key={run.id}
              run={run}
              isExpanded={expandedRunId === run.id}
              onToggle={() => setExpandedRunId(expandedRunId === run.id ? null : run.id)}
            />
          ))}
        </motion.div>
      </div>

    </div>
  );
}

function RunStreamCard({ run, isExpanded, onToggle }: { run: any; isExpanded: boolean; onToggle: () => void }) {
  const statusColors = {
    success: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
    failure: 'text-red-500 border-red-500/20 bg-red-500/5',
    timeout: 'text-amber-500 border-amber-500/20 bg-amber-500/5',
    error: 'text-red-500 border-red-500/20 bg-red-500/5',
  };
  const statusColor = statusColors[run.status as keyof typeof statusColors] || 'text-white/40 border-white/5';

  const accuracyPercentage = useMemo(() => {
    if (run.score !== undefined && run.score !== null) {
      return Math.round(Number(run.score) * 100);
    }
    return run.status === 'success' || run.success ? 100 : 0;
  }, [run.score, run.status, run.success]);

  return (
    <motion.div
      variants={slideUp}
      className="p-5 bg-[#050505] border border-white/5 hover:border-white/10 rounded-xl transition-all duration-300"
    >
      <div className="flex items-center justify-between gap-6 cursor-pointer" onClick={onToggle}>
        <div className="flex items-center gap-4 min-w-0">
          <div className="space-y-0.5">
            <span className="font-sans text-sm font-semibold text-white group-hover:text-emerald-400 transition-colors block">
              {run.agent_name}
            </span>
            <span className="font-mono text-[9px] text-white/35 block">
              RUN ID: {run.id.substring(0, 8)} • TASK: {run.task_id}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-6 shrink-0">
          <span className={`px-2 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${statusColor}`}>
            {run.status}
          </span>
          <div className="text-right hidden sm:block">
            <span className="font-mono text-sm font-semibold text-white block">
              {run.duration.toFixed(1)}s
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Runtime</span>
          </div>
          <div className="text-right">
            <span className="font-mono text-sm font-semibold text-white block">
              {accuracyPercentage}%
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
          </div>
          <button className="p-1 border border-white/5 hover:border-white/15 rounded text-white/30 hover:text-white transition-all bg-transparent">
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Expandable detailed content wrapper */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="pt-5 mt-5 border-t border-white/5 grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Column 1: Metadata details */}
              <div className="space-y-3 font-mono text-[10px] text-white/55">
                <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Operational specs</span>
                <div className="flex justify-between">
                  <span>EVALUATION TIME</span>
                  <span className="text-white">{formatDistanceToNow(new Date(run.created_at))}</span>
                </div>
                <div className="flex justify-between">
                  <span>ACCURACY SCORE</span>
                  <span className="text-white">{(run.score || 0).toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span>ACCUMULATED COST</span>
                  <span className="text-emerald-400">{formatCost(run.cost)}</span>
                </div>
              </div>

              {/* Column 2: Run Metrics */}
              <div className="space-y-3 font-mono text-[10px] text-white/55">
                <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Execution metrics</span>
                <div className="flex justify-between">
                  <span>COMMANDS EXECUTED</span>
                  <span className="text-white">{run.metrics?.commands_executed || 0} execs</span>
                </div>
                <div className="flex justify-between">
                  <span>FILES MODIFIED</span>
                  <span className="text-white">{run.metrics?.files_modified || 0} files</span>
                </div>
                <div className="flex justify-between">
                  <span>TOKENS CONSUMED</span>
                  <span className="text-white">{run.metrics?.tokens_used?.toLocaleString() || 0} tokens</span>
                </div>
              </div>

              {/* Column 3: Forensic deep-dive action */}
              <div className="flex flex-col justify-between items-end p-2 bg-[#0a0a0a] rounded-lg border border-white/5">
                <div className="space-y-1 w-full">
                  <span className="text-[7px] font-mono text-white/20 uppercase tracking-widest block">Observatory deep-dive</span>
                  <p className="font-sans text-[10px] text-white/40 font-light leading-relaxed">
                    Access the interactive synchronized trace log viewer to inspect standard CLI sandbox outputs.
                  </p>
                </div>
                <Link
                  href={`/runs/${run.id}`}
                  className="w-full py-2 bg-white text-black hover:bg-white/90 rounded-md font-semibold text-center text-[10px] font-mono uppercase tracking-wider transition-all no-underline flex items-center justify-center gap-1.5"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Investigate Trace</span>
                </Link>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
}
