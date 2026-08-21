'use client';

import React from 'react';
import Link from 'next/link';
import { Run } from '@/lib/types';

interface RecentRunsWidgetProps {
  /** Array of runs to display */
  runs: Run[] | null;
  /** Loading state */
  loading?: boolean;
  /** Error state */
  error?: Error | null;
  /** Callback to retry loading */
  onRetry?: () => void;
}

/**
 * Status badge color mapping
 */
const getStatusBadgeColor = (status: string): string => {
  switch (status) {
    case 'success':
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'failure':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    case 'timeout':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    case 'error':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
};

/**
 * Format date to readable format
 */
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
};

/**
 * RecentRunsWidget Component
 * 
 * Displays a table of the most recent runs with status badges and links to run details.
 * Shows last 5 runs by default with loading and error states.
 */
export default function RecentRunsWidget({
  runs,
  loading = false,
  error,
  onRetry,
}: RecentRunsWidgetProps) {
  if (loading) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Recent Runs</h3>
        <div className="space-y-2 sm:space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 sm:p-4 rounded-lg bg-slate-700/20 animate-pulse gap-2"
            >
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-slate-600/50 rounded w-1/3 mb-2" />
                <div className="h-3 bg-slate-600/50 rounded w-1/2" />
              </div>
              <div className="h-6 bg-slate-600/50 rounded w-20 shrink-0" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Recent Runs</h3>
        <div className="flex flex-col items-center justify-center py-6 sm:py-8">
          <p className="text-red-400 text-xs sm:text-sm mb-4">Failed to load recent runs</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="px-3 sm:px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors text-xs sm:text-sm font-medium"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  if (!runs || runs.length === 0) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Recent Runs</h3>
        <p className="text-slate-400 text-xs sm:text-sm py-6 sm:py-8 text-center">
          No runs yet. Start running tasks to see activity here.
        </p>
      </div>
    );
  }

  return (
    <div className="glass p-4 sm:p-6 rounded-xl">
      <div className="flex items-center justify-between mb-4 sm:mb-6 gap-2">
        <h3 className="text-lg sm:text-xl font-bold text-white">Recent Runs</h3>
        <Link
          href="/runs"
          className="text-xs text-blue-400 hover:text-blue-300 transition-colors font-medium whitespace-nowrap"
        >
          View All
        </Link>
      </div>

      <div className="overflow-x-auto -mx-4 sm:mx-0 sm:overflow-visible">
        <table className="w-full text-xs sm:text-sm">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Task
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Agent
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider hidden sm:table-cell">
                Date
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr
                key={run.id}
                className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors"
              >
                <td className="py-3 sm:py-4 px-3 sm:px-4">
                  <Link
                    href={`/tasks/${run.task_id}`}
                    className="text-blue-400 hover:text-blue-300 transition-colors text-xs sm:text-sm font-medium truncate inline-block max-w-[100px] sm:max-w-none"
                  >
                    {run.task_id}
                  </Link>
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4 text-xs sm:text-sm text-slate-300 truncate">
                  {run.agent_name}
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4 text-xs text-slate-400 hidden sm:table-cell">
                  {formatDate(run.created_at)}
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4">
                  <span
                    className={`inline-flex items-center px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(
                      run.status
                    )}`}
                  >
                    {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
