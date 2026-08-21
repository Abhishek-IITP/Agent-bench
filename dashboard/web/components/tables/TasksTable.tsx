'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Grid, List, Search } from 'lucide-react';
import type { Task, TaskHealth } from '@/lib/types';

interface TasksTableProps {
  tasks: Task[] | null;
  taskHealths?: TaskHealth[] | null;
  loading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
}

type SortField = 'name' | 'difficulty' | 'category' | 'created_at' | 'pass_rate' | 'run_count' | 'health';
type SortOrder = 'asc' | 'desc';

type DifficultyFilter = 'easy' | 'medium' | 'hard' | 'all';
type HealthFilter = 'healthy' | 'flaky' | 'broken' | 'trivial' | 'saturated' | 'all';

export default function TasksTable({ tasks, taskHealths, loading = false, error, onRetry }: TasksTableProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [difficultyFilter, setDifficultyFilter] = useState<DifficultyFilter>('all');
  const [healthFilter, setHealthFilter] = useState<HealthFilter>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const itemsPerPage = viewMode === 'grid' ? 12 : 50;

  // Build health status map
  const healthMap = useMemo(() => {
    const map = new Map<string, TaskHealth>();
    if (taskHealths) {
      taskHealths.forEach((health) => {
        map.set(health.task_id, health);
      });
    }
    return map;
  }, [taskHealths]);

  // Get unique categories
  const categories = useMemo(() => {
    if (!tasks) return [];
    const set = new Set(tasks.map((t) => t.category));
    return Array.from(set).sort();
  }, [tasks]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    if (!tasks) return [];

    return tasks.filter((task) => {
      // Search Query
      if (searchQuery && !task.name.toLowerCase().includes(searchQuery.toLowerCase()) && !task.category.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      // Difficulty
      if (difficultyFilter !== 'all' && task.difficulty !== difficultyFilter) {
        return false;
      }
      // Category
      if (categoryFilter !== 'all' && task.category !== categoryFilter) {
        return false;
      }
      // Health Status
      if (healthFilter !== 'all') {
        const health = healthMap.get(task.id);
        if (!health || health.health_status !== healthFilter) {
          return false;
        }
      }
      return true;
    });
  }, [tasks, searchQuery, difficultyFilter, categoryFilter, healthFilter, healthMap]);

  // Sort tasks
  const sortedTasks = useMemo(() => {
    const sorted = [...filteredTasks].sort((a, b) => {
      let aVal: string | number = '';
      let bVal: string | number = '';

      const aHealth = healthMap.get(a.id);
      const bHealth = healthMap.get(b.id);

      switch (sortField) {
        case 'name':
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case 'category':
          aVal = a.category.toLowerCase();
          bVal = b.category.toLowerCase();
          break;
        case 'difficulty':
          aVal = a.difficulty;
          bVal = b.difficulty;
          break;
        case 'pass_rate':
          aVal = aHealth?.success_rate ?? 0;
          bVal = bHealth?.success_rate ?? 0;
          break;
        case 'run_count':
          aVal = aHealth?.n_runs_total ?? 0;
          bVal = bHealth?.n_runs_total ?? 0;
          break;
        case 'health':
          aVal = aHealth?.health_status ?? '';
          bVal = bHealth?.health_status ?? '';
          break;
        case 'created_at':
        default:
          aVal = new Date(a.created_at).getTime();
          bVal = new Date(b.created_at).getTime();
          break;
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [filteredTasks, sortField, sortOrder, healthMap]);

  // Paginated tasks
  const paginatedTasks = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedTasks.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedTasks, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedTasks.length / itemsPerPage);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <div className="w-4 h-4" />;
    return sortOrder === 'asc' ? <ChevronUp className="w-4 h-4 text-emerald-400" /> : <ChevronDown className="w-4 h-4 text-emerald-400" />;
  };

  if (error && !loading) {
    return (
      <div className="p-12 text-center border border-red-500/10 bg-red-500/5 rounded-xl">
        <p className="text-red-400 mb-4 font-mono text-sm">Error executing pipeline: {error.message || 'Failed to load tasks'}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 border border-red-500/30 text-red-400 rounded-lg text-xs font-semibold hover:bg-red-500/10 transition-colors"
          >
            Retry Connection
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-12">
      {/* Premium Filters Header */}
      <div className="bg-[#050505] border border-[#111111] p-6 rounded-xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30">
              <Search className="w-4 h-4" />
            </span>
            <input
              type="text"
              placeholder="Search code paths or category tags..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#111111] border border-white/5 text-white text-sm placeholder-white/20 focus:outline-none focus:border-emerald-500/30 transition-colors"
            />
          </div>

          <div className="flex items-center gap-3 self-end md:self-auto">
            {/* View Mode Toggle */}
            <div className="bg-[#111111] p-1 rounded-lg border border-white/5 flex gap-1">
              <button
                type="button"
                onClick={() => { setViewMode('grid'); setCurrentPage(1); }}
                className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white'}`}
                aria-label="Grid Explorer view"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => { setViewMode('table'); setCurrentPage(1); }}
                className={`p-2 rounded-md transition-colors ${viewMode === 'table' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white'}`}
                aria-label="Ledger Table view"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-white/5">
          <div>
            <label className="block text-[10px] text-white/45 font-mono uppercase tracking-wider mb-2">Difficulty</label>
            <select
              value={difficultyFilter}
              onChange={(e) => { setDifficultyFilter(e.target.value as DifficultyFilter); setCurrentPage(1); }}
              className="w-full px-3 py-2 bg-[#111111] border border-white/5 rounded-lg text-white/80 text-xs focus:outline-none focus:border-emerald-500/30 transition-colors"
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-white/45 font-mono uppercase tracking-wider mb-2">Category Tag</label>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
              className="w-full px-3 py-2 bg-[#111111] border border-white/5 rounded-lg text-white/80 text-xs focus:outline-none focus:border-emerald-500/30 transition-colors"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-white/45 font-mono uppercase tracking-wider mb-2">Health Quality</label>
            <select
              value={healthFilter}
              onChange={(e) => { setHealthFilter(e.target.value as HealthFilter); setCurrentPage(1); }}
              className="w-full px-3 py-2 bg-[#111111] border border-white/5 rounded-lg text-white/80 text-xs focus:outline-none focus:border-emerald-500/30 transition-colors"
            >
              <option value="all">All Health Statuses</option>
              <option value="healthy">Healthy</option>
              <option value="flaky">Flaky</option>
              <option value="broken">Broken</option>
              <option value="trivial">Trivial</option>
              <option value="saturated">Saturated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Exploration Space */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-60 bg-[#111111] border border-white/5 rounded-xl" />
          ))}
        </div>
      ) : sortedTasks.length === 0 ? (
        <div className="border border-white/5 bg-[#050505] p-16 rounded-xl text-center">
          <p className="text-white/40 text-sm font-mono">No intelligence tasks match selected queries.</p>
        </div>
      ) : viewMode === 'grid' ? (
        /* Asymmetric Cinematic Card Grid */
        <motion.div
          layout
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <AnimatePresence mode="popLayout">
            {paginatedTasks.map((task) => {
              const health = healthMap.get(task.id);
              const passRate = health?.success_rate ?? 0;
              const runCount = health?.n_runs_total ?? 0;
              const healthStatus = health?.health_status || 'trivial';

              return (
                <motion.div
                  key={task.id}
                  layout
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                  className="group relative"
                >
                  <Link href={`/tasks/${task.id}`} className="no-underline block">
                    <div className="bg-[#050505] border border-[#111111] group-hover:border-[#222222] p-6 rounded-xl h-64 flex flex-col justify-between transition-all duration-300 relative overflow-hidden group-hover:-translate-y-1">
                      {/* Ambient Grid overlay */}
                      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(255,255,255,0.015),transparent)] pointer-events-none" />

                      {/* Header Section */}
                      <div>
                        <div className="flex items-center justify-between mb-4">
                          <span className="text-[10px] font-mono text-white/30 uppercase tracking-widest bg-white/5 px-2.5 py-1 rounded border border-white/5">
                            {task.category}
                          </span>
                          <span className={`text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded ${
                            task.difficulty === 'hard'
                              ? 'text-red-400 bg-red-500/10'
                              : task.difficulty === 'medium'
                              ? 'text-yellow-400 bg-yellow-500/10'
                              : 'text-emerald-400 bg-emerald-500/10'
                          }`}>
                            {task.difficulty}
                          </span>
                        </div>
                        <h4 className="font-sans text-lg font-semibold text-white tracking-tight mb-2 truncate">
                          {task.name}
                        </h4>
                        <p className="text-white/40 text-xs line-clamp-2 leading-relaxed">
                          {task.description || 'No execution brief provided for this task.'}
                        </p>
                      </div>

                      {/* Metric Section */}
                      <div className="space-y-4 pt-4 border-t border-white/5">
                        <div className="flex items-end justify-between">
                          <div>
                            <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block">Pass Rate</span>
                            <span className="text-2xl font-bold text-white font-mono">
                              {(passRate * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block">Runs Executed</span>
                            <span className="text-sm font-semibold text-white/70 font-mono">
                              {runCount}
                            </span>
                          </div>
                        </div>

                        {/* Visual Pass Rate Bar */}
                        <div className="h-[2px] bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-500 ${
                              healthStatus === 'healthy' ? 'bg-emerald-500' :
                              healthStatus === 'flaky' ? 'bg-amber-500' :
                              healthStatus === 'broken' ? 'bg-red-500' : 'bg-blue-400'
                            }`}
                            style={{ width: `${passRate * 100}%` }}
                          />
                        </div>

                        {/* Health Status badge */}
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="text-white/35 font-mono">ID: {task.id.slice(0, 12)}...</span>
                          <span className={`flex items-center gap-1.5 uppercase font-mono tracking-wider font-semibold ${
                            healthStatus === 'healthy' ? 'text-emerald-400' :
                            healthStatus === 'flaky' ? 'text-amber-400' :
                            healthStatus === 'broken' ? 'text-red-400' : 'text-blue-400'
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              healthStatus === 'healthy' ? 'bg-emerald-500' :
                              healthStatus === 'flaky' ? 'bg-amber-500' :
                              healthStatus === 'broken' ? 'bg-red-500' : 'bg-blue-400'
                            }`} />
                            {healthStatus}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      ) : (
        /* Ledger Table view */
        <div className="bg-[#050505] border border-[#111111] rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-[#111111] bg-[#080808]/50">
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('name')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Task Name <SortIcon field="name" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('category')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Category <SortIcon field="category" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('difficulty')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Difficulty <SortIcon field="difficulty" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('pass_rate')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Pass Rate <SortIcon field="pass_rate" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('run_count')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Runs <SortIcon field="run_count" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('health')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Health <SortIcon field="health" />
                    </button>
                  </th>
                  <th className="px-6 py-4 text-left">
                    <button onClick={() => handleSort('created_at')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                      Created <SortIcon field="created_at" />
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedTasks.map((task) => {
                  const health = healthMap.get(task.id);
                  const passRate = health?.success_rate ?? 0;
                  const runCount = health?.n_runs_total ?? 0;
                  const healthStatus = health?.health_status || 'trivial';

                  return (
                    <tr
                      key={task.id}
                      className="border-b border-[#111111] hover:bg-white/[0.015] transition-colors cursor-pointer group"
                    >
                      <td className="px-6 py-4">
                        <Link href={`/tasks/${task.id}`} className="no-underline">
                          <span className="text-white font-medium group-hover:text-emerald-400 transition-colors">
                            {task.name}
                          </span>
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-white/40 text-xs font-mono">{task.category}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs font-mono uppercase ${
                          task.difficulty === 'hard' ? 'text-red-400' :
                          task.difficulty === 'medium' ? 'text-yellow-400' : 'text-emerald-400'
                        }`}>
                          {task.difficulty}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono text-sm text-white">
                        {(passRate * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-white/50">
                        {runCount}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-[10px] font-mono uppercase font-semibold flex items-center gap-1.5 ${
                          healthStatus === 'healthy' ? 'text-emerald-400' :
                          healthStatus === 'flaky' ? 'text-amber-400' :
                          healthStatus === 'broken' ? 'text-red-400' : 'text-blue-400'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            healthStatus === 'healthy' ? 'bg-emerald-500' :
                            healthStatus === 'flaky' ? 'bg-amber-500' :
                            healthStatus === 'broken' ? 'bg-red-500' : 'bg-blue-400'
                          }`} />
                          {healthStatus}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-white/30 font-mono">
                        {new Date(task.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-white/5 pt-6">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="flex items-center gap-2 px-4 py-2 border border-white/10 rounded-lg text-white/50 text-xs hover:text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/5 transition-all"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Prev</span>
          </button>
          <div className="flex items-center">
            <span className="text-white/40 text-xs font-mono">
              PAGE {currentPage} OF {totalPages}
            </span>
          </div>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="flex items-center gap-2 px-4 py-2 border border-white/10 rounded-lg text-white/50 text-xs hover:text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/5 transition-all"
          >
            <span>Next</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
