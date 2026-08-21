'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Play, Eye } from 'lucide-react';
import type { Run } from '@/lib/types';
import { formatDistanceToNow, formatCost } from '@/lib/utils';

interface RunsTableProps {
  runs: Run[] | null;
  loading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  taskName?: string;
}

type SortField = 'id' | 'task_id' | 'agent_name' | 'status' | 'duration' | 'cost' | 'created_at' | 'score';
type SortOrder = 'asc' | 'desc';

type StatusFilter = 'success' | 'failure' | 'timeout' | 'error' | 'all';

export default function RunsTable({ runs, loading = false, error, onRetry, taskName }: RunsTableProps) {
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  const itemsPerPage = 50;

  // Filter runs
  const filteredRuns = useMemo(() => {
    if (!runs) return [];

    return runs.filter((run) => {
      if (statusFilter !== 'all' && run.status !== statusFilter) {
        return false;
      }
      return true;
    });
  }, [runs, statusFilter]);

  // Sort runs
  const sortedRuns = useMemo(() => {
    const sorted = [...filteredRuns].sort((a, b) => {
      let aVal: string | number = '';
      let bVal: string | number = '';

      switch (sortField) {
        case 'id':
          aVal = a.id;
          bVal = b.id;
          break;
        case 'task_id':
          aVal = a.task_id;
          bVal = b.task_id;
          break;
        case 'agent_name':
          aVal = a.agent_name.toLowerCase();
          bVal = a.agent_name.toLowerCase();
          break;
        case 'status':
          aVal = a.status;
          bVal = b.status;
          break;
        case 'duration':
          aVal = a.duration;
          bVal = b.duration;
          break;
        case 'cost':
          aVal = a.cost;
          bVal = b.cost;
          break;
        case 'score':
          aVal = a.score;
          bVal = b.score;
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
  }, [filteredRuns, sortField, sortOrder]);

  // Paginated runs
  const paginatedRuns = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedRuns.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedRuns, currentPage]);

  const totalPages = Math.ceil(sortedRuns.length / itemsPerPage);

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

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'failure':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'timeout':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      default:
        return 'text-white/55 bg-white/5 border-white/10';
    }
  };

  if (error && !loading) {
    return (
      <div className="p-12 text-center border border-red-500/10 bg-red-500/5 rounded-xl">
        <p className="text-red-400 mb-4 font-mono text-sm">Failed to connect to execution logs: {error.message}</p>
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
    <div className="space-y-6">
      {/* Filtering Control Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-[#050505] border border-[#111111] p-4 rounded-xl">
        <div className="flex flex-wrap items-center gap-2">
          {(['all', 'success', 'failure', 'timeout'] as const).map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => { setStatusFilter(status); setCurrentPage(1); }}
              className={`px-3.5 py-1.5 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all border ${
                statusFilter === status
                  ? 'bg-white text-black border-white'
                  : 'bg-transparent text-white/50 border-white/5 hover:text-white hover:border-white/20'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        <div className="text-[10px] font-mono text-white/35">
          LEDGER: <span className="text-white font-semibold">{sortedRuns.length} runs</span> logged
        </div>
      </div>

      {/* Runs Table container */}
      <div className="bg-[#050505] border border-[#111111] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-[#111111] bg-[#080808]/50">
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('id')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Run ID <SortIcon field="id" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('agent_name')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Agent Name <SortIcon field="agent_name" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('status')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Status <SortIcon field="status" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('score')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Score <SortIcon field="score" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('duration')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Duration <SortIcon field="duration" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('cost')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Cost <SortIcon field="cost" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <button onClick={() => handleSort('created_at')} className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider text-white/35 hover:text-white transition-colors cursor-pointer border-none bg-transparent">
                    Timestamp <SortIcon field="created_at" />
                  </button>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-white/35">Replay</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b border-[#111111] animate-pulse">
                    <td colSpan={8} className="px-6 py-5">
                      <div className="h-4 bg-white/5 rounded w-full" />
                    </td>
                  </tr>
                ))
              ) : paginatedRuns.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-white/35 font-mono text-xs">
                    No runs found inside records.
                  </td>
                </tr>
              ) : (
                paginatedRuns.map((run) => (
                  <tr
                    key={run.id}
                    className="border-b border-[#111111] hover:bg-white/[0.015] transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <Link href={`/runs/${run.id}`} className="no-underline">
                        <span className="font-mono text-xs text-white/40 group-hover:text-emerald-400 transition-colors">
                          {run.id.substring(0, 8)}
                        </span>
                      </Link>
                    </td>
                    <td className="px-6 py-4 font-sans text-sm font-semibold text-white">
                      {run.agent_name}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono uppercase border ${getStatusStyle(run.status)}`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-sm font-semibold text-white">
                      {(run.score !== null && run.score !== undefined) ? (run.score * 100).toFixed(0) : '0'}%
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-white/50">
                      {run.duration.toFixed(1)}s
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-white/50">
                      {formatCost(run.cost)}
                    </td>
                    <td className="px-6 py-4 text-xs text-white/30 font-mono">
                      {formatDistanceToNow(new Date(run.created_at))}
                    </td>
                    <td className="px-6 py-4">
                      <Link href={`/runs/${run.id}`} className="no-underline">
                        <button
                          type="button"
                          className="flex items-center gap-1 px-3 py-1 bg-[#111111] border border-white/5 text-white/60 hover:text-white rounded-md text-[10px] font-mono transition-colors group-hover:border-emerald-500/20"
                          aria-label={`Replay run ${run.id}`}
                        >
                          <Play className="w-3 h-3 text-emerald-400" />
                          <span>INVESTIGATE</span>
                        </button>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination navigation */}
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
