'use client';

import React, { useMemo } from 'react';
import Link from 'next/link';
import { Task, TaskHealth } from '@/lib/types';

interface TopTasksWidgetProps {
  /** Array of tasks with basic info */
  tasks: Task[] | null;
  /** Array of task health data */
  taskHealths: TaskHealth[] | null;
  /** Loading state */
  loading?: boolean;
  /** Error state */
  error?: Error | null;
  /** Callback to retry loading */
  onRetry?: () => void;
}

/**
 * Difficulty badge color mapping
 */
const getDifficultyBadgeColor = (difficulty: string): string => {
  switch (difficulty) {
    case 'easy':
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'medium':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    case 'hard':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
};

/**
 * Health status badge color mapping
 */
const getHealthBadgeColor = (status: string): string => {
  switch (status) {
    case 'healthy':
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'flaky':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    case 'broken':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    case 'saturated':
      return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    case 'trivial':
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    default:
      return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
};

/**
 * Calculate reliability score (0-100) based on success rate and task run count
 * Tasks with more runs are more reliable
 */
const calculateReliabilityScore = (health: TaskHealth): number => {
  // Reliability = success_rate (0-1) scaled to 0-100
  // Can be enhanced with other factors like variance or n_runs
  return health.success_rate * 100;
};

/**
 * TopTasksWidget Component
 * 
 * Displays top 5 tasks with highest reliability scores.
 * Shows task name, reliability score, success rate, difficulty badge, and health status.
 * Clicking a row navigates to task details page.
 */
export default function TopTasksWidget({
  tasks,
  taskHealths,
  loading = false,
  error,
  onRetry,
}: TopTasksWidgetProps) {
  // Combine and sort tasks by reliability
  const topTasks = useMemo(() => {
    if (!tasks || !taskHealths || tasks.length === 0 || taskHealths.length === 0) {
      return [];
    }

    // Create a map of task health by task_id for quick lookup
    const healthMap = new Map(taskHealths.map((h) => [h.task_id, h]));

    // Combine tasks with their health data
    const combined = tasks
      .map((task) => ({
        task,
        health: healthMap.get(task.id),
      }))
      .filter((item) => item.health !== undefined)
      .map((item) => ({
        ...item,
        reliabilityScore: calculateReliabilityScore(item.health!),
      }))
      // Sort by reliability score descending
      .sort((a, b) => b.reliabilityScore - a.reliabilityScore)
      // Take top 5
      .slice(0, 5);

    return combined;
  }, [tasks, taskHealths]);

  if (loading) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Tasks (Highest Reliability)</h3>
        <div className="space-y-2 sm:space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-slate-700/20 animate-pulse gap-2"
            >
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-slate-600/50 rounded w-1/3 mb-2" />
                <div className="h-3 bg-slate-600/50 rounded w-1/2" />
              </div>
              <div className="flex gap-2 shrink-0">
                <div className="h-6 bg-slate-600/50 rounded w-14" />
                <div className="hidden sm:block h-6 bg-slate-600/50 rounded w-14" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Tasks (Highest Reliability)</h3>
        <div className="flex flex-col items-center justify-center py-6 sm:py-8">
          <p className="text-red-400 text-xs sm:text-sm mb-4">Failed to load top tasks</p>
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

  if (topTasks.length === 0) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Tasks (Highest Reliability)</h3>
        <p className="text-slate-400 text-xs sm:text-sm py-6 sm:py-8 text-center">
          No task data available yet.
        </p>
      </div>
    );
  }

  return (
    <div className="glass p-4 sm:p-6 rounded-xl">
      <div className="flex items-center justify-between mb-4 sm:mb-6 gap-2">
        <h3 className="text-lg sm:text-xl font-bold text-white">Top Tasks (Highest Reliability)</h3>
        <Link
          href="/tasks"
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
                Reliability
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider hidden md:table-cell">
                Success Rate
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell">
                Difficulty
              </th>
              <th className="text-left py-2 sm:py-3 px-3 sm:px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {topTasks.map(({ task, health, reliabilityScore }) => (
              <tr
                key={task.id}
                className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors"
              >
                <td className="py-3 sm:py-4 px-3 sm:px-4">
                  <Link
                    href={`/tasks/${task.id}`}
                    className="text-blue-400 hover:text-blue-300 transition-colors text-xs sm:text-sm font-medium truncate inline-block max-w-[80px] sm:max-w-none"
                  >
                    {task.name}
                  </Link>
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <div className="hidden sm:flex flex-1 h-2 bg-slate-700/50 rounded-full overflow-hidden max-w-[60px]">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                        style={{ width: `${reliabilityScore}%` }}
                      />
                    </div>
                    <span className="text-xs sm:text-sm font-semibold text-white min-w-[28px]">
                      {reliabilityScore.toFixed(0)}%
                    </span>
                  </div>
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4 text-xs text-slate-300 hidden md:table-cell">
                  {(health!.success_rate * 100).toFixed(0)}%
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4 hidden lg:table-cell">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${getDifficultyBadgeColor(
                      task.difficulty
                    )}`}
                  >
                    {task.difficulty.charAt(0).toUpperCase() + task.difficulty.slice(1)}
                  </span>
                </td>
                <td className="py-3 sm:py-4 px-3 sm:px-4">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${getHealthBadgeColor(
                      health!.health_status
                    )}`}
                  >
                    {health!.health_status.charAt(0).toUpperCase() +
                      health!.health_status.slice(1)}
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
