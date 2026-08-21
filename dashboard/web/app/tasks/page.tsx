'use client';

import React, { useState, useMemo } from 'react';
import { useTasks, useTaskHealth } from '@/lib/hooks';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUpRight, Search, Terminal, Activity, HelpCircle, HardDrive, Mail, FileSpreadsheet } from 'lucide-react';
import Link from 'next/link';
import { slideUp, staggerContainer } from '@/lib/motion';

export default function TasksPage() {
  const { data: tasks, loading: tasksLoading, error: tasksError } = useTasks();
  const { data: taskHealths, loading: healthLoading, error: healthError } = useTaskHealth();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const isLoading = tasksLoading || healthLoading;
  const isError = tasksError || healthError;

  // Build health map
  const healthMap = useMemo(() => {
    const map = new Map<string, any>();
    if (taskHealths) {
      taskHealths.forEach((health) => {
        map.set(health.task_id, health);
      });
    }
    return map;
  }, [taskHealths]);

  // Group tasks by category
  const groupedTasks = useMemo(() => {
    if (!tasks) return {};
    const groups: Record<string, any[]> = {};
    
    tasks.forEach((task) => {
      // Group by category tag
      const cat = task.category.toLowerCase();
      if (!groups[cat]) {
        groups[cat] = [];
      }
      
      const health = healthMap.get(task.id);
      groups[cat].push({
        ...task,
        health,
      });
    });

    return groups;
  }, [tasks, healthMap]);

  // Filter grouped categories based on search query
  const filteredGroups = useMemo(() => {
    if (Object.keys(groupedTasks).length === 0) return {};
    
    const filtered: Record<string, any[]> = {};
    Object.entries(groupedTasks).forEach(([cat, list]) => {
      const matched = list.filter(task => 
        task.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.id.toLowerCase().includes(searchQuery.toLowerCase())
      );
      if (matched.length > 0) {
        filtered[cat] = matched;
      }
    });
    
    return filtered;
  }, [groupedTasks, searchQuery]);

  const categories = Object.keys(groupedTasks);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center space-y-4 font-mono text-xs text-white/35">
          <div className="w-8 h-8 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mx-auto" />
          <span>SYNCHRONIZING BENCHMARK CATALOG...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-24 text-center space-y-6">
        <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto text-red-500">
          <Terminal className="w-6 h-6" />
        </div>
        <p className="font-mono text-xs text-red-400">FAILED TO ACCESS SCENARIOS DATABASE</p>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-black p-6 lg:p-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
        
        {/* LEFT DUAL-PANE CHAMBER: Sticky Dossier Info (Col Span 4) */}
        <div className="lg:col-span-4 lg:sticky lg:top-12 h-fit space-y-8 lg:space-y-12">
          <div className="space-y-4">
            <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest block font-semibold">
              Chapter 02 // Scenario Registry
            </span>
            <h1 className="font-display text-5xl text-white tracking-tight leading-tight select-text">
              Benchmark Scenarios
            </h1>
            <p className="font-sans text-white/55 text-sm font-light leading-relaxed">
              Exploratory index of all sandbox evaluations. Review operational objectives, runtime limits, and target accuracy configurations.
            </p>
          </div>

          {/* Minimal prompt command search input */}
          <div className="relative group">
            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-white/20 group-focus-within:text-emerald-400 transition-colors">
              <Terminal className="w-4 h-4" />
            </div>
            <input
              type="text"
              placeholder="agentbench:~ explore [query]"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#050505] border border-white/5 focus:border-emerald-500/20 rounded-xl py-3 pl-10 pr-4 text-xs font-mono text-white placeholder-white/20 outline-none transition-all"
            />
          </div>

          {/* Stats spread */}
          <div className="grid grid-cols-2 gap-6 border-t border-white/5 pt-8">
            <div className="space-y-1">
              <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Active Domains</span>
              <span className="font-mono text-2xl font-bold text-white leading-none">{categories.length}</span>
            </div>
            <div className="space-y-1">
              <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Evaluations Catalogued</span>
              <span className="font-mono text-2xl font-bold text-white leading-none">
                {tasks?.length || 0}
              </span>
            </div>
          </div>
        </div>

        {/* RIGHT DUAL-PANE CHAMBER: Scrollable Scenario Folders (Col Span 8) */}
        <div className="lg:col-span-8 space-y-12 min-h-0">
          <AnimatePresence mode="popLayout">
            {Object.keys(filteredGroups).length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="p-12 text-center border border-white/5 bg-[#050505] rounded-xl font-mono text-xs text-white/35"
              >
                No active scenarios matched the query.
              </motion.div>
            ) : (
              <motion.div
                variants={staggerContainer(0.08, 0.05)}
                initial="hidden"
                animate="visible"
                className="space-y-12"
              >
                {Object.entries(filteredGroups).map(([cat, list]) => (
                  <CategorySection key={cat} name={cat} list={list} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}

function CategorySection({ name, list }: { name: string; list: any[] }) {
  const iconConfig = {
    database: <HardDrive className="w-4 h-4 text-emerald-400" />,
    emails: <Mail className="w-4 h-4 text-amber-500" />,
    csv: <FileSpreadsheet className="w-4 h-4 text-blue-400" />,
  };
  
  const icon = iconConfig[name.toLowerCase() as keyof typeof iconConfig] || <HelpCircle className="w-4 h-4 text-white/40" />;

  return (
    <motion.div variants={slideUp} className="space-y-4">
      {/* Editorial category bar */}
      <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-mono text-xs text-white/80 font-bold uppercase tracking-wider">
            {name} scenarios
          </span>
        </div>
        <span className="text-[9px] font-mono text-white/35 uppercase">{list.length} tasks</span>
      </div>

      {/* Grid List */}
      <div className="space-y-3">
        {list.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </motion.div>
  );
}

function TaskCard({ task }: { task: any }) {
  const successRate = task.health?.success_rate ?? 0;
  
  const difficultyBadge = {
    easy: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    medium: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    hard: 'text-red-500 bg-red-500/10 border-red-500/20',
  };
  const diffStyle = difficultyBadge[task.difficulty as keyof typeof difficultyBadge] || 'text-white/40 border-white/10';

  const healthBadge = {
    healthy: 'bg-emerald-500',
    flaky: 'bg-amber-500',
    broken: 'bg-red-500',
  };
  const dotColor = healthBadge[task.health?.health_status as keyof typeof healthBadge] || 'bg-white/30';

  return (
    <Link href={`/tasks/${task.id}`} className="no-underline block group">
      <div className="p-5 bg-[#121212] border border-white/10 hover:border-white/20 rounded-xl transition-all duration-300 flex items-center justify-between gap-6">
        
        <div className="min-w-0 flex-1 space-y-1.5">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs font-bold text-white group-hover:text-emerald-400 transition-colors truncate">
              {task.name}
            </span>
            <span className={`inline-block px-1.5 py-0.5 rounded text-[8px] font-mono uppercase tracking-wider border ${diffStyle}`}>
              {task.difficulty}
            </span>
          </div>
          <p className="font-sans text-xs text-white/45 font-light leading-relaxed truncate max-w-lg">
            {task.description || 'Verification scenario for testing model sandbox executions.'}
          </p>
        </div>

        {/* Right Stats block */}
        <div className="flex items-center gap-6 shrink-0">
          <div className="text-right">
            <span className="font-mono text-base font-bold text-white block">
              {(successRate * 100).toFixed(0)}%
            </span>
            <span className="text-[8px] font-mono text-white/20 uppercase tracking-widest block">Accuracy</span>
          </div>

          <div className="flex items-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
            <span className="text-[9px] font-mono text-white/35 uppercase hidden sm:inline">{task.health?.health_status || 'stable'}</span>
          </div>

          <div className="p-2 border border-white/5 hover:border-white/15 rounded-lg text-white/30 hover:text-white transition-all">
            <ArrowUpRight className="w-4 h-4" />
          </div>
        </div>

      </div>
    </Link>
  );
}
