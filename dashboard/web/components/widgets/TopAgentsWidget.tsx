'use client';

import React from 'react';
import Link from 'next/link';
import { Leaderboard } from '@/lib/types';

interface TopAgentsWidgetProps {
  /** Leaderboard data containing ranked agents */
  leaderboard: Leaderboard | null;
  /** Loading state */
  loading?: boolean;
  /** Error state */
  error?: Error | null;
  /** Callback to retry loading */
  onRetry?: () => void;
  /** Number of agents to display (default: 3) */
  limit?: number;
}

/**
 * TopAgentsWidget Component
 * 
 * Displays a card with the top 3 agents ranked by overall score.
 * Shows agent name, score, tasks solved, and reliability.
 */
export default function TopAgentsWidget({
  leaderboard,
  loading = false,
  error,
  onRetry,
  limit = 3,
}: TopAgentsWidgetProps) {
  if (loading) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Agents</h3>
        <div className="space-y-2 sm:space-y-3">
          {[...Array(limit)].map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-slate-700/20 animate-pulse gap-2"
            >
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-slate-600/50 rounded w-1/3 mb-2" />
                <div className="h-3 bg-slate-600/50 rounded w-1/2" />
              </div>
              <div className="h-8 bg-slate-600/50 rounded w-16 shrink-0" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Agents</h3>
        <div className="flex flex-col items-center justify-center py-6 sm:py-8">
          <p className="text-red-400 text-xs sm:text-sm mb-4">Failed to load leaderboard</p>
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

  if (!leaderboard || !leaderboard.agents || leaderboard.agents.length === 0) {
    return (
      <div className="glass p-4 sm:p-6 rounded-xl">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4 sm:mb-6">Top Agents</h3>
        <p className="text-slate-400 text-xs sm:text-sm py-6 sm:py-8 text-center">
          No agent data available yet.
        </p>
      </div>
    );
  }

  const topAgents = leaderboard.agents.slice(0, limit);

  return (
    <div className="glass p-4 sm:p-6 rounded-xl">
      <div className="flex items-center justify-between mb-4 sm:mb-6 gap-2">
        <h3 className="text-lg sm:text-xl font-bold text-white">Top Agents</h3>
        <Link
          href="/leaderboard"
          className="text-xs text-blue-400 hover:text-blue-300 transition-colors font-medium whitespace-nowrap"
        >
          View All
        </Link>
      </div>

      <div className="space-y-2 sm:space-y-3">
        {topAgents.map((agent, index) => (
          <div
            key={agent.agent_name}
            className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-slate-700/20 hover:bg-slate-700/40 transition-colors group cursor-pointer gap-2"
          >
            <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
              {/* Rank Badge */}
              <div className="flex items-center justify-center w-7 sm:w-8 h-7 sm:h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 font-bold text-white text-xs sm:text-sm shrink-0">
                {index + 1}
              </div>

              <div className="flex-1 min-w-0">
                <Link
                  href="/leaderboard"
                  className="text-white font-semibold group-hover:text-blue-400 transition-colors text-xs sm:text-sm block truncate"
                >
                  {agent.agent_name}
                </Link>
                <p className="text-xs text-slate-500 mt-0.5">
                  {agent.tasks_solved} task{agent.tasks_solved !== 1 ? 's' : ''}
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-2 sm:gap-6 text-right shrink-0">
              <div className="hidden sm:block">
                <p className="text-base sm:text-lg font-bold text-white">{agent.score.toFixed(0)}</p>
                <p className="text-xs text-slate-500">Score</p>
              </div>
              <div>
                <p className="text-sm sm:text-lg font-bold text-green-400">
                  {(agent.reliability * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-slate-500">Reliability</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View All Link */}
      <Link
        href="/leaderboard"
        className="flex items-center justify-center mt-3 sm:mt-4 py-2 rounded-lg bg-slate-700/20 hover:bg-slate-700/40 transition-colors text-slate-400 hover:text-blue-400 text-xs sm:text-sm font-medium"
      >
        View Full Leaderboard
      </Link>
    </div>
  );
}
