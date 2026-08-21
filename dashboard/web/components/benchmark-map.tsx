'use client';

import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';
import type { TaskHealth } from '@/lib/types';
import { getHealthColor } from '@/lib/utils';
import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';

interface BenchmarkMapProps {
  taskHealths: TaskHealth[];
}

function groupByCategory(tasks: TaskHealth[]): Record<string, TaskHealth[]> {
  const groups: Record<string, TaskHealth[]> = {};
  tasks.forEach((task) => {
    // Map tasks to simple mock category tags based on IDs if not explicitly present
    const category = task.task_id.split('-')[1] || 'core';
    const cleanCategory = category.charAt(0).toUpperCase() + category.slice(1);
    if (!groups[cleanCategory]) {
      groups[cleanCategory] = [];
    }
    groups[cleanCategory].push(task);
  });
  return groups;
}

export default function BenchmarkMap({ taskHealths }: BenchmarkMapProps) {
  const categories = groupByCategory(taskHealths);
  
  return (
    <section className="min-h-screen flex items-center justify-center bg-black px-8 py-24">
      <div className="max-w-6xl w-full space-y-16">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="space-y-4"
        >
          <span className="text-[9px] font-mono text-white/35 uppercase tracking-widest block">
            02 / Diagnostic Health Landscape
          </span>
          <h2 className="chapter-title text-white select-text">
            Global Benchmark Map
          </h2>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Systemic health metrics across all scenario categories. Observe active flakiness, regression spikes, and accuracy variances.
          </p>
        </motion.div>
        
        {/* Category lists (Visual cards) */}
        <motion.div
          variants={staggerContainer(0.08, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="space-y-10"
        >
          {Object.entries(categories).map(([category, tasks]) => (
            <CategorySection key={category} category={category} tasks={tasks} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function CategorySection({ category, tasks }: { category: string; tasks: TaskHealth[] }) {
  return (
    <motion.div variants={slideUp} className="space-y-4">
      {/* Category visual header */}
      <div className="flex items-center justify-between border-b border-white/5 pb-3">
        <span className="font-mono text-xs text-white/80 font-semibold tracking-wide capitalize">
          {category}
        </span>
        <span className="text-[10px] font-mono text-white/30 uppercase">{tasks.length} scenarios</span>
      </div>
      
      {/* Cards list */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {tasks.map((task) => (
          <TaskCell key={task.task_id} task={task} />
        ))}
      </div>
    </motion.div>
  );
}

function TaskCell({ task }: { task: TaskHealth }) {
  const healthColor = getHealthColor(task.health_status);
  
  // Custom display styles based on status
  const badgeConfig = {
    healthy: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    flaky: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    broken: 'text-red-500 bg-red-500/10 border-red-500/20',
    trivial: 'text-white/40 bg-white/5 border-white/10',
    saturated: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  };
  const statusBadge = badgeConfig[task.health_status as keyof typeof badgeConfig] || badgeConfig.trivial;

  return (
    <Link href={`/tasks/${task.task_id}`} className="no-underline block group">
      <div className="p-5 bg-[#050505] border border-white/5 group-hover:border-white/15 rounded-xl transition-all duration-300 flex flex-col justify-between h-36">
        <div className="space-y-1">
          <div className="flex items-start justify-between gap-4">
            <span className="font-mono text-xs text-white/90 group-hover:text-emerald-400 transition-colors font-bold truncate">
              {task.task_id}
            </span>
            <ArrowUpRight className="w-3.5 h-3.5 text-white/20 group-hover:text-white transition-colors shrink-0" />
          </div>
          <span className={`inline-block px-1.5 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${statusBadge}`}>
            {task.health_status}
          </span>
        </div>

        <div className="flex items-end justify-between pt-4 border-t border-white/5">
          <div>
            <span className="text-[15px] font-mono font-bold text-white block">
              {(task.success_rate * 100).toFixed(0)}%
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Pass Rate</span>
          </div>

          <div className="text-right">
            <span className="text-xs font-mono font-semibold text-white/55 block">
              {task.n_runs_total} runs
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Evaluations</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
