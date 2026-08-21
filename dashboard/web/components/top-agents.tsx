'use client';

import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';
import type { AgentScore } from '@/lib/types';
import { formatCost } from '@/lib/utils';
import Link from 'next/link';
import { Trophy, ArrowUpRight, Cpu, Target, Landmark } from 'lucide-react';

interface TopAgentsProps {
  agents: AgentScore[];
}

export default function TopAgents({ agents }: TopAgentsProps) {
  const topAgents = agents.slice(0, 3); // Display top 3 models as collectible card files
  
  return (
    <section className="min-h-screen flex items-center justify-center bg-black px-8 py-24">
      <div className="max-w-5xl w-full space-y-16">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4"
        >
          <span className="text-[9px] font-mono text-white/35 uppercase tracking-widest block">
            03 / Performance Rankings
          </span>
          <h2 className="chapter-title text-white select-text">
            Champion Agents
          </h2>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            The highest scoring agent entities evaluated within the benchmark. Profiles rank agents based on systemic cost efficiency, capabilities, and reliability.
          </p>
        </motion.div>
        
        {/* Champions Grid */}
        <motion.div
          variants={staggerContainer(0.08, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {topAgents.map((agent, idx) => (
            <AgentCard key={agent.agent_name} agent={agent} rank={idx + 1} />
          ))}
        </motion.div>
        
        {/* Leaderboard link */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="pt-4 border-t border-white/5 flex justify-end"
        >
          <Link
            href="/leaderboard"
            className="inline-flex items-center gap-2 text-[10px] font-mono text-white/50 hover:text-white uppercase tracking-widest transition-colors group no-underline"
          >
            <span>Compare All Agent Entities</span>
            <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

function AgentCard({ agent, rank }: { agent: AgentScore; rank: number }) {
  const rankColors = {
    1: 'text-yellow-500',
    2: 'text-slate-300',
    3: 'text-amber-600',
  };
  
  const trophyColor = rankColors[rank as keyof typeof rankColors] || 'text-white/30';
  
  return (
    <motion.div
      variants={slideUp}
      className="p-6 bg-[#050505] border border-white/5 hover:border-white/10 rounded-xl transition-all duration-300 relative overflow-hidden flex flex-col justify-between h-[360px]"
    >
      {/* Ambient soft glow for Rank 1 */}
      {rank === 1 && (
        <div className="absolute -inset-10 bg-emerald-500/5 filter blur-3xl pointer-events-none -z-10 animate-[pulse-dot_3s_infinite]" />
      )}
      
      {/* Card header */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="font-display text-2xl text-white">#{rank}</span>
          <Trophy className={`w-4 h-4 ${trophyColor}`} />
        </div>
        <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest">
          Champion Profile
        </span>
      </div>
      
      {/* Agent details */}
      <div className="space-y-4 my-6">
        <div className="space-y-1">
          <h3 className="font-sans text-base font-semibold text-white truncate">
            {agent.agent_name}
          </h3>
          <p className="text-[10px] font-mono text-white/35 uppercase">
            Model Evaluation Profile
          </p>
        </div>

        {/* Giant score display */}
        <div className="space-y-1">
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">
            Capability Score
          </span>
          <div className="text-4xl font-bold font-mono text-white leading-none">
            {agent.score.toFixed(1)}
          </div>
        </div>
      </div>
      
      {/* Stats list */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5 shrink-0">
        <div className="space-y-0.5">
          <div className="flex items-center gap-1 text-[8px] font-mono text-white/35 uppercase">
            <Target className="w-3 h-3 text-emerald-400" />
            <span>Reliability</span>
          </div>
          <p className="font-mono text-xs font-semibold text-white">
            {(agent.reliability * 100).toFixed(0)}%
          </p>
        </div>
        
        <div className="space-y-0.5">
          <div className="flex items-center gap-1 text-[8px] font-mono text-white/35 uppercase">
            <Landmark className="w-3 h-3 text-white/40" />
            <span>Avg Cost</span>
          </div>
          <p className="font-mono text-xs font-semibold text-white">
            {formatCost(agent.avg_cost)}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
