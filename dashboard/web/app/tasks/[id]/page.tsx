'use client';

import React, { use, useMemo } from 'react';
import Link from 'next/link';
import { useTask, useRuns } from '@/lib/hooks';
import { ArrowLeft, Clock, ShieldAlert, Cpu, Award, Terminal, Activity, ArrowUpRight } from 'lucide-react';
import { formatCost, formatDistanceToNow } from '@/lib/utils';
import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';

interface TaskDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function TaskDetailPage({ params }: TaskDetailPageProps) {
  const resolvedParams = use(params);
  const { data: task, loading: taskLoading, error: taskError } = useTask(resolvedParams.id);
  const { data: runsData, loading: runsLoading, error: runsError } = useRuns({
    task_id: resolvedParams.id,
    limit: 50,
    page: 1,
  });

  const runs = runsData?.items || [];
  const totalRuns = runsData?.total || 0;
  
  const stats = useMemo(() => {
    if (runs.length === 0) return { passRate: 0, failRate: 0, avgDuration: 0, stdDev: 0 };
    const successCount = runs.filter(r => r.status === 'success' || r.success === true || (r.score !== undefined && Number(r.score) >= 0.7)).length;
    const passRate = runs.length > 0 ? (successCount / runs.length) * 100 : 0;
    const failRate = 100 - passRate;
    const avgDuration = runs.reduce((sum, r) => sum + (r.duration || 0), 0) / runs.length;
    const variance = runs.reduce((sum, r) => sum + Math.pow((r.duration || 0) - avgDuration, 2), 0) / runs.length;
    const stdDev = Math.sqrt(variance);
    
    return { passRate, failRate, avgDuration, stdDev };
  }, [runs]);

  const isHealthy = stats.passRate > 75;
  const isBroken = stats.passRate < 25;
  const healthStatus = isHealthy ? 'healthy' : isBroken ? 'broken' : 'flaky';

  if (!taskLoading && !task) {
    return (
      <div className="max-w-xl mx-auto px-6 py-24 text-center space-y-6">
        <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto text-red-500">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-display text-2xl text-white">Scenario Unresolved</h1>
          <p className="text-white/40 text-xs mt-2">The target task identifier does not correspond to an active benchmark task.</p>
        </div>
        <Link
          href="/tasks"
          className="inline-block px-5 py-2 bg-white text-black rounded-lg text-xs font-semibold hover:bg-white/90 transition-all no-underline"
        >
          Return to Registry
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-black p-6 lg:p-12 space-y-16">
      {/* Back Navigator */}
      <div className="flex items-center justify-between shrink-0">
        <Link href="/tasks" className="text-white/40 hover:text-white transition-colors text-xs font-mono no-underline flex items-center gap-2">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>BACK TO SCENARIO REGISTRY</span>
        </Link>
        <span className="text-[9px] font-mono text-white/35 uppercase">
          Scenario Brief // {resolvedParams.id}
        </span>
      </div>

      {/* 1. COVER BRIEFING: Asymmetrical Title & Health Stamp */}
      <div className="border-b border-white/5 pb-12 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest border border-emerald-500/20 bg-emerald-500/5 px-2 py-0.5 rounded">
              {task?.category}
            </span>
            <span className="text-[9px] font-mono text-white/20 uppercase">SCENARIO OBJECTIVE</span>
          </div>
          <h1 className="font-display text-4xl md:text-6xl text-white tracking-tight leading-none">
            {task?.name}
          </h1>
          <p className="font-sans text-white/55 text-sm font-light leading-relaxed max-w-xl">
            {task?.description || 'Operational baseline test verifying capabilities on system filepaths.'}
          </p>
        </div>

        <div className="lg:col-span-4 lg:text-right space-y-1">
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Systemic Status</span>
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-mono uppercase tracking-wider border ${
            healthStatus === 'healthy' ? 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5' :
            healthStatus === 'broken' ? 'text-red-500 border-red-500/20 bg-red-500/5' : 'text-amber-500 border-amber-500/20 bg-amber-500/5'
          }`}>
            {healthStatus}
          </span>
        </div>
      </div>

      {/* 2. CORE METRICS: Massive Numerical Indicators */}
      <div className="space-y-6">
        <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest block">01 / Performance Stats</span>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <MetricCell label="Observed Runs" value={totalRuns} suffix="evals" />
          <MetricCell label="Solution Accuracy" value={`${stats.passRate.toFixed(0)}%`} suffix="success" highlight="emerald" />
          <MetricCell label="Average Duration" value={`${stats.avgDuration.toFixed(1)}s`} suffix="runtime" />
          <MetricCell label="Duration StdDev" value={`${stats.stdDev.toFixed(1)}s`} suffix="variance" />
        </div>
      </div>

      {/* 3. DIAGNOSTICS & RECOMMENDATIONS: Large graphite panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8">
        <div className="border border-white/5 bg-[#050505] p-6 rounded-xl space-y-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest">Stability Assessment</span>
          </div>
          <p className="font-sans text-xs text-white/60 font-light leading-relaxed">
            {healthStatus === 'healthy'
              ? 'Task demonstrates stable characteristics. Pass rates are consistent across models, with runtime standard deviation well within nominal constraints.'
              : healthStatus === 'broken'
              ? 'Systemic failure detected. Models are timing out or crashing before resolving filesystem parameters. Environmental check recommended.'
              : 'Flaky response logs detected. Accuracy spikes indicate solution logic volatility. Verify if sandbox configurations have race conditions.'}
          </p>
        </div>

        <div className="border border-white/5 bg-[#050505] p-6 rounded-xl space-y-4">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-400" />
            <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest">Recommended Tuning</span>
          </div>
          <div className="space-y-2">
            {(healthStatus === 'healthy'
              ? ['Integrate scenario as model capability baseline.', 'Archive duplicate low-difficulty variations.']
              : healthStatus === 'broken'
              ? ['Verify docker sandboxing file permissions.', 'Ensure reference shell scripts match database path specs.']
              : ['Audit initialization step duration timeouts.', 'Increase execution latency limits to buffer flaky outputs.']
            ).map((rec, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono text-white/65">
                <span className="w-1 h-1 rounded-full bg-emerald-400 shrink-0" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 4. Telemetry Parameters (nasa layout) */}
      <div className="border border-white/5 bg-[#050505] p-6 rounded-xl space-y-6">
        <div className="flex items-center gap-2 pb-4 border-b border-white/5">
          <Cpu className="w-4 h-4 text-white/40" />
          <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest">Telemetry Sandbox Parameters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ParamBox label="Docker Environment" value={task?.docker_image || 'docker.io/sandbox:latest'} />
          <ParamBox label="Execution Timeout" value={`${task?.timeout || 300} SECONDS LIMIT`} />
          <ParamBox label="Target Difficulty" value={`${(task?.difficulty || 'easy').toUpperCase()} SCENARIO`} />
        </div>
      </div>

      {/* 5. LIVE ACTIVITY LEDGER: Expandable Chronological list */}
      <div className="space-y-6">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest block">02 / Execution History</span>
          <span className="text-[9px] font-mono text-white/20 uppercase">{runs.length} Runs logged</span>
        </div>

        {runsLoading ? (
          <div className="space-y-3 animate-pulse">
            <div className="h-12 bg-white/5 rounded-lg" />
            <div className="h-12 bg-white/5 rounded-lg" />
          </div>
        ) : (
          <div className="space-y-3">
            {runs.map((run) => (
              <RunRow key={run.id} run={run} />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}

function MetricCell({ label, value, suffix, highlight }: { label: string; value: string | number; suffix: string; highlight?: 'emerald' | 'amber' | 'red' }) {
  const highlightStyles = {
    emerald: 'text-emerald-400',
    amber: 'text-amber-500',
    red: 'text-red-500',
  };
  const colorClass = highlight ? highlightStyles[highlight] : 'text-white';

  return (
    <div className="p-5 bg-[#050505] border border-white/5 rounded-xl space-y-2">
      <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">{label}</span>
      <div className="flex items-baseline gap-1">
        <span className={`font-mono text-2xl font-bold ${colorClass} leading-none`}>{value}</span>
        <span className="text-[9px] font-mono text-white/30 uppercase">{suffix}</span>
      </div>
    </div>
  );
}

function ParamBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1">
      <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">{label}</span>
      <p className="font-mono text-xs text-white bg-[#111111] p-3 rounded-lg border border-white/5 truncate">{value}</p>
    </div>
  );
}

function RunRow({ run }: { run: any }) {
  const statusColors = {
    success: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5',
    failure: 'text-red-500 border-red-500/20 bg-red-500/5',
    timeout: 'text-amber-500 border-amber-500/20 bg-amber-500/5',
    error: 'text-red-500 border-red-500/20 bg-red-500/5',
  };
  const statusColor = statusColors[run.status as keyof typeof statusColors] || 'text-white/40 border-white/5';

  return (
    <div className="p-4 bg-[#050505] border border-white/5 hover:border-white/10 rounded-xl transition-all duration-300 flex items-center justify-between gap-6">
      <div className="flex items-center gap-4 min-w-0">
        <div className="space-y-0.5">
          <span className="font-sans text-xs font-semibold text-white truncate block">
            {run.agent_name}
          </span>
          <span className="font-mono text-[9px] text-white/30 block">
            RUN ID: {run.id.substring(0, 8)} • {formatDistanceToNow(new Date(run.created_at))}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-6 shrink-0">
        <span className={`px-2 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${statusColor}`}>
          {run.status}
        </span>
        <div className="text-right">
          <span className="font-mono text-sm font-semibold text-white block">
            {run.duration.toFixed(1)}s
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Runtime</span>
        </div>
        <div className="text-right">
          <span className="font-mono text-sm font-semibold text-white block">
            {formatCost(run.cost)}
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Cost</span>
        </div>
        <Link
          href={`/runs/${run.id}`}
          className="p-2 border border-white/5 hover:border-white/15 rounded-lg text-white/40 hover:text-white transition-all"
        >
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
