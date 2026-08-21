'use client';

import React, { useState, useMemo } from 'react';
import { useLeaderboard, useTasks } from '@/lib/hooks';
import { RefreshCw, Trophy, Target, Landmark, Award, ShieldAlert, Cpu, Sparkles } from 'lucide-react';
import { formatCost } from '@/lib/utils';
import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';

export default function LeaderboardPage() {
  const { data: leaderboard, loading, error, refetch } = useLeaderboard();
  const { data: tasks } = useTasks();
  const [sortBy, setSortBy] = useState<'score' | 'reliability' | 'cost'>('score');

  const agents = leaderboard?.agents || [];
  
  const sorted = useMemo(() => {
    return [...agents].sort((a, b) => {
      switch (sortBy) {
        case 'reliability':
          return b.reliability - a.reliability;
        case 'cost':
          return a.avg_cost - b.avg_cost;
        case 'score':
        default:
          return b.score - a.score;
      }
    });
  }, [agents, sortBy]);

  const summaryStats = useMemo(() => {
    if (agents.length === 0) return null;
    const total = agents.length;
    const top = Math.max(...agents.map(a => a.score));
    const avg = agents.reduce((sum, a) => sum + a.score, 0) / agents.length;
    return { total, top, avg };
  }, [agents]);

  if (loading && agents.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center space-y-4 font-mono text-xs text-white/35">
          <div className="w-8 h-8 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mx-auto" />
          <span>CATALOGUING CHAMPION AGENT RECORDS...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-24 text-center space-y-6">
        <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto text-red-500">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <p className="font-mono text-xs text-red-400">LEADERBOARD SERVER TEMPORARILY OFFLINE</p>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-black p-6 lg:p-12 space-y-16">
      
      {/* Editorial Navigation Brief */}
      <div className="border-b border-white/5 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-4">
          <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest block font-semibold">
            Chapter 04 // Champion Agents
          </span>
          <h1 className="font-display text-5xl text-white tracking-tight leading-none">
            Model Ledger
          </h1>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Leaderboard evaluating model capability accuracy, average API execution costs, and general reliability.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 border border-white/5 bg-[#050505] rounded-xl text-white/50 text-[10px] font-mono hover:text-white transition-all hover:border-white/15"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>REFRESH LEDGER</span>
        </button>
      </div>

      {/* State Sort filters */}
      <div className="flex items-center gap-2 bg-[#050505] border border-white/5 p-1.5 rounded-xl self-start w-fit">
        {(['score', 'reliability', 'cost'] as const).map((option) => (
          <button
            key={option}
            onClick={() => setSortBy(option)}
            className={`px-3 py-1.5 rounded-lg text-[9px] font-mono uppercase tracking-wider transition-all border ${
              sortBy === option
                ? 'bg-white text-black border-white font-semibold'
                : 'bg-transparent text-white/40 border-transparent hover:text-white'
            }`}
          >
            Sort by {option}
          </button>
        ))}
      </div>

      {/* Collectible Profile Dossiers Grid */}
      <motion.div
        variants={staggerContainer(0.08, 0.05)}
        initial="hidden"
        animate="visible"
        className="space-y-8"
      >
        {sorted.map((agent, index) => (
          <AgentDossierCard
            key={agent.agent_name}
            agent={agent}
            rank={index + 1}
            tasksCount={tasks?.length || 10}
          />
        ))}
      </motion.div>

      {/* Summary Metrics at bottom */}
      {summaryStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 border-t border-white/5 w-full">
          <div className="p-6 bg-[#050505] border border-white/5 rounded-xl space-y-2">
            <span className="text-[8px] font-mono text-white/25 uppercase tracking-widest block">Total Models</span>
            <p className="font-mono text-2xl font-bold text-white leading-none">{summaryStats.total}</p>
          </div>
          <div className="p-6 bg-[#050505] border border-white/5 rounded-xl space-y-2">
            <span className="text-[8px] font-mono text-white/25 uppercase tracking-widest block">Peak Ensemble Score</span>
            <p className="font-mono text-2xl font-bold text-emerald-400 leading-none">{summaryStats.top.toFixed(1)}</p>
          </div>
          <div className="p-6 bg-[#050505] border border-white/5 rounded-xl space-y-2">
            <span className="text-[8px] font-mono text-white/25 uppercase tracking-widest block">Average ensemble accuracy</span>
            <p className="font-mono text-2xl font-bold text-white/70 leading-none">{summaryStats.avg.toFixed(1)}</p>
          </div>
        </div>
      )}

    </div>
  );
}

function AgentDossierCard({ agent, rank, tasksCount }: { agent: any; rank: number; tasksCount: number }) {
  const isTopThree = rank <= 3;
  const rankColors = {
    1: 'text-yellow-500 border-yellow-500/20 bg-yellow-500/5',
    2: 'text-slate-300 border-slate-500/20 bg-slate-500/5',
    3: 'text-amber-600 border-amber-500/20 bg-amber-500/5',
  };
  const rankStyle = rankColors[rank as keyof typeof rankColors] || 'text-white/40 border-white/5 bg-white/[0.02]';

  return (
    <motion.div
      variants={slideUp}
      className="p-6 bg-[#050505] border border-white/5 rounded-xl space-y-6 relative overflow-hidden transition-all duration-300 hover:border-white/10"
    >
      {/* Background ambient glow for Rank 1 */}
      {rank === 1 && (
        <div className="absolute -left-20 -top-20 bg-emerald-500/5 w-60 h-60 rounded-full filter blur-3xl pointer-events-none -z-10" />
      )}

      {/* Card Header info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${rankStyle}`}>
            RANK #{rank}
          </span>
          <span className="font-sans text-base font-semibold text-white">
            {agent.agent_name}
          </span>
        </div>

        <div className="flex items-center gap-3 text-[9px] font-mono text-white/25">
          <span>MODEL ID: {agent.agent_name.toLowerCase().replace('-', '_')}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-white/5" />
          <span>EVALS CAPTURED: {agent.tasks_solved}</span>
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Col 1: Numerical capability score (Col Span 4) */}
        <div className="lg:col-span-4 grid grid-cols-3 gap-6">
          <div className="space-y-1 col-span-1">
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
            <span className="font-mono text-2xl font-bold text-white block">
              {agent.score.toFixed(1)}
            </span>
          </div>

          <div className="space-y-1 col-span-1">
            <div className="flex items-center gap-1 text-[8px] font-mono text-white/20 uppercase tracking-widest">
              <Target className="w-3 h-3 text-emerald-400" />
              <span>Reliability</span>
            </div>
            <span className="font-mono text-base font-semibold text-white block">
              {(agent.reliability * 100).toFixed(0)}%
            </span>
          </div>

          <div className="space-y-1 col-span-1">
            <div className="flex items-center gap-1 text-[8px] font-mono text-white/20 uppercase tracking-widest">
              <Landmark className="w-3 h-3 text-white/40" />
              <span>Avg Cost</span>
            </div>
            <span className="font-mono text-base font-semibold text-emerald-400 block">
              {formatCost(agent.avg_cost)}
            </span>
          </div>
        </div>

        {/* Col 2: Relative performance progress bar (Col Span 4) */}
        <div className="lg:col-span-4 space-y-2">
          <div className="flex justify-between text-[8px] font-mono text-white/25 uppercase">
            <span>Accuracy Comparison Index</span>
            <span>{agent.score.toFixed(1)} / 100</span>
          </div>
          <div className="h-2 w-full bg-[#111111] rounded border border-white/5 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${agent.score}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full bg-white rounded"
            />
          </div>
        </div>

        {/* Col 3: Scenario Success Heatmap Grid (Col Span 4) */}
        <div className="lg:col-span-4 space-y-2">
          <div className="flex justify-between text-[8px] font-mono text-white/25 uppercase tracking-widest">
            <span>Scenario success matrix</span>
            <span>{agent.tasks_solved} / {tasksCount} Tasks</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {Array.from({ length: tasksCount }).map((_, i) => {
              // Simulated success color
              const passed = i < agent.tasks_solved;
              const isFlaky = !passed && i % 4 === 0;
              const colorClass = passed 
                ? 'bg-emerald-400 border-emerald-500/20' 
                : isFlaky 
                ? 'bg-amber-500 border-amber-500/20' 
                : 'bg-red-500 border-red-500/20';

              return (
                <div
                  key={i}
                  className={`w-3.5 h-3.5 rounded border transition-all duration-300 ${colorClass}`}
                  title={passed ? 'Scenario Completed' : isFlaky ? 'Flaky execution' : 'Scenario Failure'}
                />
              );
            })}
          </div>
        </div>

      </div>

    </motion.div>
  );
}
