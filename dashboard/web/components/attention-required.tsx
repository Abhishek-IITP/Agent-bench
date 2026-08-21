'use client';

import { motion } from 'framer-motion';
import { slideUp, staggerContainer } from '@/lib/motion';
import type { TaskHealth } from '@/lib/types';
import { AlertCircle, AlertTriangle, ArrowUpRight, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

interface AttentionRequiredProps {
  taskHealths: TaskHealth[];
}

export default function AttentionRequired({ taskHealths }: AttentionRequiredProps) {
  // Find tasks that need attention
  const brokenTasks = taskHealths.filter(t => t.health_status === 'broken');
  const flakyTasks = taskHealths.filter(t => t.health_status === 'flaky');
  const highVariance = taskHealths
    .filter(t => t.variance > 0.3 && t.health_status !== 'broken')
    .slice(0, 3);
  
  const hasIssues = brokenTasks.length > 0 || flakyTasks.length > 0 || highVariance.length > 0;
  
  if (!hasIssues) {
    return (
      <section className="min-h-screen flex items-center justify-center bg-black px-8 py-24">
        <div className="max-w-md w-full text-center space-y-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-4"
          >
            <div className="w-12 h-12 mx-auto rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>
            <h2 className="text-xl font-bold text-white">
              All Systems Healthy
            </h2>
            <p className="font-sans text-white/55 text-sm font-light leading-relaxed">
              No task regressions or flakiness observed in this active benchmark suite run.
            </p>
          </motion.div>
        </div>
      </section>
    );
  }
  
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
          <span className="text-[9px] font-mono text-red-400 uppercase tracking-widest block font-semibold">
            04 / Priority Diagnostics
          </span>
          <h2 className="chapter-title text-white select-text">
            Attention Required
          </h2>
          <p className="font-sans text-white/55 text-sm font-light max-w-lg leading-relaxed">
            Critical anomalies, high-variance regressions, and timeout spikes requiring system maintenance or task tuning.
          </p>
        </motion.div>
        
        {/* Issues list (Graphite diagnostic blocks) */}
        <motion.div
          variants={staggerContainer(0.08, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="space-y-4"
        >
          {brokenTasks.map(task => (
            <IssueCard key={task.task_id} task={task} severity="critical" />
          ))}
          
          {flakyTasks.map(task => (
            <IssueCard key={task.task_id} task={task} severity="warning" />
          ))}
          
          {highVariance.map(task => (
            <IssueCard key={task.task_id} task={task} severity="info" />
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function IssueCard({ 
  task, 
  severity 
}: { 
  task: TaskHealth; 
  severity: 'critical' | 'warning' | 'info';
}) {
  const configs = {
    critical: {
      border: 'border-red-500/20 hover:border-red-500/40',
      label: 'Critical Error',
      labelColor: 'text-red-500 bg-red-500/10 border-red-500/20',
      icon: <AlertCircle className="w-4 h-4 text-red-500" />
    },
    warning: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      label: 'Flakiness Alert',
      labelColor: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
      icon: <AlertTriangle className="w-4 h-4 text-amber-500" />
    },
    info: {
      border: 'border-white/5 hover:border-white/15',
      label: 'High Variance',
      labelColor: 'text-white/40 bg-white/5 border-white/10',
      icon: <AlertTriangle className="w-4 h-4 text-white/40" />
    }
  };

  const config = configs[severity];

  return (
    <motion.div
      variants={slideUp}
      className={`p-5 bg-[#050505] border ${config.border} rounded-xl transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-6`}
    >
      <div className="flex items-start gap-4">
        <div className="mt-0.5">{config.icon}</div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm font-semibold text-white">
              {task.task_id}
            </span>
            <span className={`px-1.5 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${config.labelColor}`}>
              {config.label}
            </span>
          </div>
          
          {/* Diagnostic reasoning details */}
          <div className="space-y-1">
            {(task.reasons || []).slice(0, 1).map((reason, idx) => (
              <p key={idx} className="font-sans text-xs text-white/55 font-light">
                {reason}
              </p>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6 shrink-0 self-start md:self-auto pl-8 md:pl-0">
        <div>
          <span className="font-mono text-base font-bold text-white block">
            {(task.success_rate * 100).toFixed(0)}%
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
        </div>
        
        <div>
          <span className="font-mono text-base font-bold text-white block">
            {(task.variance * 100).toFixed(0)}%
          </span>
          <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Variance</span>
        </div>

        <Link
          href={`/tasks/${task.task_id}`}
          className="p-2.5 border border-white/5 hover:border-white/15 rounded-lg text-white/40 hover:text-white transition-all no-underline"
        >
          <ArrowUpRight className="w-4 h-4" />
        </Link>
      </div>
    </motion.div>
  );
}
