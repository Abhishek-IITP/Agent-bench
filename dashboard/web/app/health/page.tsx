'use client';

import React, { useMemo } from 'react';
import { useBenchmarkHealth } from '@/lib/hooks';
import { ShieldAlert, Terminal, Activity, HelpCircle, AlertCircle, ArrowUpRight, Award } from 'lucide-react';
import type { TaskHealth } from '@/lib/types';
import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';
import Link from 'next/link';

export default function HealthPage() {
  const { data: benchmarkHealth, loading, error, refetch } = useBenchmarkHealth();

  const stats = useMemo(() => {
    if (!benchmarkHealth?.task_healths) return null;
    const tasks = benchmarkHealth.task_healths;
    const total = tasks.length;
    const healthy = tasks.filter(t => t.health_status === 'healthy').length;
    const flaky = tasks.filter(t => t.health_status === 'flaky').length;
    const broken = tasks.filter(t => t.health_status === 'broken').length;
    const trivial = tasks.filter(t => t.health_status === 'trivial').length;
    const saturated = tasks.filter(t => t.health_status === 'saturated').length;
    
    // Weighted global index
    const healthIndex = total > 0 ? (healthy / total) * 100 : 0;
    
    return { total, healthy, flaky, broken, trivial, saturated, healthIndex };
  }, [benchmarkHealth]);

  const problematicTasks = useMemo(() => {
    if (!benchmarkHealth?.task_healths) return [];
    
    const priority = { broken: 0, flaky: 1, trivial: 2, saturated: 3, healthy: 4 };
    
    return [...benchmarkHealth.task_healths]
      .filter(t => t.health_status !== 'healthy')
      .sort((a, b) => {
        const priorityA = priority[a.health_status as keyof typeof priority] ?? 5;
        const priorityB = priority[b.health_status as keyof typeof priority] ?? 5;
        return priorityA - priorityB;
      });
  }, [benchmarkHealth]);

  if (loading && !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center space-y-4 font-mono text-xs text-white/35">
          <div className="w-8 h-8 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mx-auto" />
          <span>ASSEMBLING HEALTH DIAGNOSTICS...</span>
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
        <p className="font-mono text-xs text-red-400">DIAGNOSTICS ORACLE BUSY OR UNREACHABLE</p>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-black p-6 lg:p-12 space-y-16">
      
      {/* Editorial Navigation Brief */}
      <div className="border-b border-white/5 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-4">
          <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest block font-semibold">
            Chapter 05 // Systemic Diagnostics
          </span>
          <h1 className="font-display text-5xl text-white tracking-tight leading-none">
            Health Landscape
          </h1>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Overall reliability metrics of active benchmark parameters. Identify flaky sandboxes, regression spikes, and accuracy variances.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 border border-white/5 bg-[#050505] rounded-xl text-white/50 text-[10px] font-mono hover:text-white transition-all hover:border-white/15"
        >
          <Activity className="w-3.5 h-3.5" />
          <span>RECHECK HEALTH</span>
        </button>
      </div>

      {stats && (
        <>
          {/* System Diagnostics Header (Giant Index + Status distribution stream) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center border border-white/5 bg-[#050505] p-8 rounded-xl">
            <div className="lg:col-span-4 space-y-2">
              <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">System Diagnostics Index</span>
              <div className="flex items-baseline gap-2">
                <span className="font-display text-6xl text-white font-bold leading-none select-text">
                  {stats.healthIndex.toFixed(0)}%
                </span>
                <span className="text-[10px] font-mono text-white/35 uppercase">healthy scenarios</span>
              </div>
            </div>

            <div className="lg:col-span-8 space-y-3">
              <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Operational Scenario distribution</span>
              <div className="h-4 w-full bg-[#111111] rounded border border-white/5 flex overflow-hidden">
                <div className="bg-emerald-400 h-full" style={{ width: `${(stats.healthy / stats.total) * 100}%` }} title="Healthy" />
                <div className="bg-amber-500 h-full" style={{ width: `${(stats.flaky / stats.total) * 100}%` }} title="Flaky" />
                <div className="bg-red-500 h-full" style={{ width: `${(stats.broken / stats.total) * 100}%` }} title="Broken" />
                <div className="bg-white/20 h-full" style={{ width: `${(stats.trivial / stats.total) * 100}%` }} title="Trivial" />
                <div className="bg-blue-400 h-full" style={{ width: `${(stats.saturated / stats.total) * 100}%` }} title="Saturated" />
              </div>
              <div className="flex flex-wrap gap-4 text-[9px] font-mono text-white/35 uppercase">
                <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /><span>{stats.healthy} Healthy</span></div>
                <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-amber-500" /><span>{stats.flaky} Flaky</span></div>
                <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-red-500" /><span>{stats.broken} Broken</span></div>
                <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-white/20" /><span>{stats.trivial} Trivial</span></div>
                <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-400" /><span>{stats.saturated} Saturated</span></div>
              </div>
            </div>
          </div>

          {/* Problem Landscape (Visual Priority Grid) */}
          <div className="space-y-6">
            <div className="border-b border-white/5 pb-3">
              <span className="text-[9px] font-mono text-white/25 uppercase tracking-widest block">01 / Priority Diagnostics Required</span>
            </div>

            {problematicTasks.length === 0 ? (
              <div className="p-8 border border-white/5 bg-[#050505] rounded-xl text-center font-mono text-xs text-white/35">
                No active scenario anomalies logged. Overall landscape operation normal.
              </div>
            ) : (
              <motion.div
                variants={staggerContainer(0.08, 0.05)}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {problematicTasks.map(task => (
                  <HealthDiagnosticCard key={task.task_id} task={task} />
                ))}
              </motion.div>
            )}
          </div>
        </>
      )}

    </div>
  );
}

function HealthDiagnosticCard({ task }: { task: TaskHealth }) {
  const configs = {
    broken: {
      border: 'border-red-500/20 hover:border-red-500/40',
      label: 'Critical Error',
      labelStyle: 'text-red-500 border-red-500/20 bg-red-500/5',
      icon: <AlertCircle className="w-4 h-4 text-red-500" />,
      action: 'Check sandbox read/write bounds & file descriptors.'
    },
    flaky: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      label: 'Flakiness Alert',
      labelStyle: 'text-amber-500 border-amber-500/20 bg-amber-500/5',
      icon: <HelpCircle className="w-4 h-4 text-amber-500" />,
      action: 'Verify latency timeouts and initialization flags.'
    },
    trivial: {
      border: 'border-white/5 hover:border-white/10',
      label: 'Trivial Target',
      labelStyle: 'text-white/40 border-white/10 bg-white/5',
      icon: <HelpCircle className="w-4 h-4 text-white/35" />,
      action: 'Introduce multi-step constraints or harder bounds.'
    },
    saturated: {
      border: 'border-blue-500/20 hover:border-blue-500/40',
      label: 'Saturated Baseline',
      labelStyle: 'text-blue-400 border-blue-500/20 bg-blue-500/5',
      icon: <HelpCircle className="w-4 h-4 text-blue-400" />,
      action: 'Mark task as solved and leverage as baseline.'
    }
  };

  const config = configs[task.health_status as keyof typeof configs] || configs.trivial;

  return (
    <motion.div
      variants={slideUp}
      className={`p-5 bg-[#050505] border ${config.border} rounded-xl transition-all duration-300 flex flex-col justify-between h-48`}
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <span className="font-mono text-xs text-white group-hover:text-emerald-400 transition-colors font-bold truncate">
            {task.task_id}
          </span>
          <Link href={`/tasks/${task.task_id}`} className="text-white/35 hover:text-white transition-colors">
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <span className={`inline-block px-1.5 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${config.labelStyle}`}>
          {task.health_status}
        </span>

        <p className="font-sans text-xs text-white/55 font-light leading-relaxed line-clamp-2">
          {config.action}
        </p>
      </div>

      <div className="flex items-end justify-between pt-4 border-t border-white/5 shrink-0">
        <div>
          <span className="font-mono text-base font-bold text-white block">
            {(task.success_rate * 100).toFixed(0)}%
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
        </div>

        <div className="text-right">
          <span className="font-mono text-base font-bold text-white block">
            {task.variance.toFixed(2)}
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Variance index</span>
        </div>
      </div>
    </motion.div>
  );
}
