'use client';

import React from 'react';
import { AlertCircle, CheckCircle, AlertTriangle, HelpCircle, Zap } from 'lucide-react';

export type HealthStatus = 'healthy' | 'flaky' | 'broken' | 'trivial' | 'saturated';

interface HealthStatusBadgeProps {
  /** Health status type */
  status: HealthStatus;
  /** Optional label text */
  label?: string;
  /** Optional size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Optional className for additional styling */
  className?: string;
  /** Show label with status */
  showLabel?: boolean;
}

const statusConfig: Record<HealthStatus, { color: string; bgColor: string; icon: React.ReactNode; label: string }> = {
  healthy: {
    color: 'text-green-400',
    bgColor: 'bg-green-500/10 border border-green-500/30',
    icon: <CheckCircle className="w-4 h-4" />,
    label: 'Healthy',
  },
  flaky: {
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10 border border-yellow-500/30',
    icon: <AlertTriangle className="w-4 h-4" />,
    label: 'Flaky',
  },
  broken: {
    color: 'text-red-400',
    bgColor: 'bg-red-500/10 border border-red-500/30',
    icon: <AlertCircle className="w-4 h-4" />,
    label: 'Broken',
  },
  trivial: {
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10 border border-gray-500/30',
    icon: <HelpCircle className="w-4 h-4" />,
    label: 'Trivial',
  },
  saturated: {
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 border border-blue-500/30',
    icon: <Zap className="w-4 h-4" />,
    label: 'Saturated',
  },
};

const sizeConfig = {
  sm: 'px-2 py-1 text-xs gap-1',
  md: 'px-3 py-2 text-sm gap-2',
  lg: 'px-4 py-2 text-base gap-2',
};

/**
 * HealthStatusBadge Component
 * 
 * Displays the health status of a task with color coding and icon.
 * Health statuses:
 * - Healthy: Green - all runs pass consistently
 * - Flaky: Yellow - inconsistent pass rates
 * - Broken: Red - most/all runs fail
 * - Trivial: Gray - too easy/not useful for benchmarking
 * - Saturated: Blue - agents solve it too easily
 * 
 * @example
 * ```tsx
 * <HealthStatusBadge status="healthy" size="md" showLabel />
 * <HealthStatusBadge status="broken" />
 * ```
 */
export default function HealthStatusBadge({
  status,
  label,
  size = 'md',
  className = '',
  showLabel = true,
}: HealthStatusBadgeProps) {
  const config = statusConfig[status];
  const sizeClass = sizeConfig[size];

  return (
    <div
      className={`flex items-center ${sizeClass} ${config.bgColor} rounded-lg transition-all duration-200 ${className}`}
      role="status"
      aria-label={`Health status: ${config.label}`}
    >
      <span className={config.color}>{config.icon}</span>
      {showLabel && <span className={`${config.color} font-semibold`}>{label || config.label}</span>}
    </div>
  );
}
