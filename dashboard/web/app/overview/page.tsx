'use client';

import React from 'react';
import { useTasks, useRuns, useBenchmarkHealth, useLeaderboard, useTaskHealth } from '@/lib/hooks';
import MissionBrief from '@/components/mission-brief';
import ActivityTimeline from '@/components/activity-timeline';
import BenchmarkMap from '@/components/benchmark-map';
import TopAgents from '@/components/top-agents';
import AttentionRequired from '@/components/attention-required';

/**
 * Dashboard Overview - AI Benchmark Intelligence Center
 * 
 * Cinematic experience flowing through:
 * 1. Mission Brief (100vh) - Massive reliability score with live pulse
 * 2. Activity Timeline (80vh) - Living event stream, not table
 * 3. Benchmark Map (100vh) - Visual task health representation
 * 4. Top Agents (80vh) - Expandable premium cards
 * 5. Attention Required (60vh) - Urgent issues
 */
export default function DashboardPage() {
  // Fetch all data
  const { data: tasks } = useTasks();
  const { data: runsData } = useRuns({ limit: 20 });
  const { data: benchmarkHealth } = useBenchmarkHealth();
  const { data: leaderboard } = useLeaderboard();
  const { data: taskHealths } = useTaskHealth();
  
  // Loading state
  if (!tasks || !runsData || !benchmarkHealth || !leaderboard || !taskHealths) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60 text-sm uppercase tracking-wider">Loading Intelligence Center...</p>
        </div>
      </div>
    );
  }
  
  // Calculate overview metrics
  const totalTasks = tasks.length || 0;
  const totalRuns = runsData.total || 0;
  const activeAgents = leaderboard.agents?.length || 0;
  
  // Calculate reliability score (weighted average of task success rates)
  const reliabilityScore = taskHealths && taskHealths.length > 0
    ? (taskHealths.reduce((sum, t) => sum + t.success_rate, 0) / taskHealths.length) * 100
    : 0;
  
  return (
    <main className="min-h-screen">
      {/* 1. Mission Brief - Cinematic opening */}
      <MissionBrief
        score={reliabilityScore}
        totalTasks={totalTasks}
        totalRuns={totalRuns}
        activeAgents={activeAgents}
      />
      
      {/* 2. Activity Timeline - What happened while you were away */}
      {runsData.items && runsData.items.length > 0 && (
        <ActivityTimeline runs={runsData.items} />
      )}
      
      {/* 3. Benchmark Map - Visual task health landscape */}
      {taskHealths && taskHealths.length > 0 && (
        <BenchmarkMap taskHealths={taskHealths} />
      )}
      
      {/* 4. Top Agents - Premium expandable cards */}
      {leaderboard.agents && leaderboard.agents.length > 0 && (
        <TopAgents agents={leaderboard.agents} />
      )}
      
      {/* 5. Attention Required - Urgent issues */}
      {taskHealths && taskHealths.length > 0 && (
        <AttentionRequired taskHealths={taskHealths} />
      )}
    </main>
  );
}
