'use client';

import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface StatsCardProps {
  /** Display label for the stat */
  label: string;
  /** The main value to display */
  value: string | number;
  /** React component for the icon */
  icon: React.ReactNode;
  /** Optional trend percentage (positive or negative) */
  trend?: number | null;
  /** Optional trend label (e.g., "vs last week") */
  trendLabel?: string;
  /** Optional color for the icon (blue, green, yellow, red, purple) */
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  /** Optional loading state */
  loading?: boolean;
}

const colorMap = {
  blue: 'text-blue-400',
  green: 'text-green-400',
  yellow: 'text-yellow-400',
  red: 'text-red-400',
  purple: 'text-purple-400',
};

const trendColorMap = {
  positive: 'text-green-400',
  negative: 'text-red-400',
};

/**
 * StatsCard Component
 * 
 * A reusable card component for displaying metrics with optional trend indicators.
 * Features glass morphism design with smooth animations and responsive layout.
 * 
 * @example
 * ```tsx
 * <StatsCard
 *   label="Total Tasks"
 *   value="156"
 *   icon={<TaskIcon />}
 *   trend={5}
 *   trendLabel="vs last week"
 *   color="blue"
 * />
 * ```
 */
export default function StatsCard({
  label,
  value,
  icon,
  trend,
  trendLabel,
  color = 'blue',
  loading = false,
}: StatsCardProps) {
  const trendDirection = trend && trend > 0 ? 'positive' : 'negative';
  const trendColor = trendColorMap[trendDirection];

  if (loading) {
    return (
      <div className="glass p-6 rounded-xl hover:border-blue-500/50 transition-all duration-200 h-full animate-pulse">
        <div className="h-4 bg-slate-700/50 rounded w-1/2 mb-3" />
        <div className="h-8 bg-slate-700/50 rounded w-2/3 mb-3" />
        <div className="h-3 bg-slate-700/50 rounded w-1/3" />
      </div>
    );
  }

  return (
    <div className="glass p-6 rounded-xl hover:border-blue-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/10 cursor-pointer group h-full animate-fade-in-up">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Label */}
          <p className="text-slate-400 text-sm mb-2 font-medium">{label}</p>

          {/* Value */}
          <p className="text-3xl font-bold text-white mb-3 group-hover:text-blue-300 transition-colors">
            {value}
          </p>

          {/* Trend Indicator */}
          {trend !== undefined && trend !== null && (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {trend > 0 ? (
                  <ArrowUp className={`w-4 h-4 ${trendColor}`} />
                ) : (
                  <ArrowDown className={`w-4 h-4 ${trendColor}`} />
                )}
                <span className={`text-xs font-semibold ${trendColor}`}>
                  {Math.abs(trend)}%
                </span>
              </div>
              {trendLabel && <span className="text-xs text-slate-500">{trendLabel}</span>}
            </div>
          )}
        </div>

        {/* Icon */}
        <div className={`${colorMap[color]} text-2xl group-hover:scale-110 transition-transform duration-200`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
