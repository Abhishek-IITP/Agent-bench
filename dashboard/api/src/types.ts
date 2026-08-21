/**
 * TypeScript type definitions matching the database schema
 * These types correspond to the PostgreSQL tables in runner/db/schema.sql
 */

/**
 * Task metadata from tasks table
 */
export interface Task {
  id: string;
  name: string;
  category: string;
  difficulty: string;
  version: string;
  description?: string;
  timeout: number;
  docker_image: string;
  created_at: string;
  updated_at?: string;
}

/**
 * Agent configuration from agents table
 */
export interface Agent {
  id: number;
  name: string;
  type: string;
  model: string;
  config: Record<string, any>;
  created_at: string;
}

/**
 * Run execution record from runs table
 */
export interface Run {
  id: string;
  task_id: string;
  agent_id: number;
  agent_name?: string; // Joined from agents table
  started_at: string;
  ended_at?: string;
  duration?: number;
  success?: boolean;
  created_at: string;
}

/**
 * Detailed run information with joined results and metrics
 */
export interface RunDetails extends Run {
  result: {
    passed: boolean;
    score: number;
    test_output: string;
    test_details: Record<string, any>;
    error_message?: string;
  };
  metrics?: {
    commands_executed: number;
    files_created: number;
    files_modified: number;
    tokens_used: number;
    cost: number;
    memory_peak_mb?: number;
  };
}

/**
 * Task statistics aggregation
 */
export interface TaskStats {
  total_runs: number;
  passes: number;
  failures: number;
  pass_rate: number;
  avg_duration: number;
  std_duration: number;
}

/**
 * Agent statistics for leaderboard
 */
export interface AgentStats {
  agent_name: string;
  total_runs: number;
  tasks_solved: number;
  success_rate: number;
  avg_cost: number;
  avg_tokens: number;
}

/**
 * Leaderboard entry
 */
export interface LeaderboardEntry {
  agent_name: string;
  score: number;
  reliability: number;
  success_rate: number;
  avg_cost: number;
  avg_tokens: number;
  total_runs: number;
  tasks_solved: number;
}

/**
 * Task health classification from task_health table
 */
export interface TaskHealth {
  task_id: string;
  health_status: "healthy" | "flaky" | "broken" | "trivial" | "saturated";
  success_rate: number;
  variance: number;
  n_agents: number;
  n_runs_total: number;
  evidence: string[];
  recommendations: string[];
  analyzed_at?: string;
}

/**
 * Overall benchmark health summary
 */
export interface BenchmarkHealth {
  overall_status: string;
  overall_score: number;
  task_healths: TaskHealth[];
}

/**
 * Replay trace data from replays table
 */
export interface ReplayTrace {
  run_id: string;
  events: Array<{
    timestamp: number;
    type: string;
    content: string;
  }>;
}

/**
 * Multi-run metrics from multi_run_metrics table
 */
export interface MultiRunMetrics {
  id: string;
  task_id: string;
  agent_name: string;
  n_runs: number;
  success_rate: number;
  confidence_interval_lower?: number;
  confidence_interval_upper?: number;
  variance?: number;
  mean_runtime?: number;
  mean_tokens: number;
  mean_cost: number;
  reliability_score?: number;
  computed_at: string;
}

/**
 * Filters for querying runs
 */
export interface RunFilters {
  task_id?: string;
  agent_id?: number;
  success?: boolean;
  limit?: number;
  offset?: number;
  page?: number;
}

/**
 * Paginated runs response
 */
export interface PaginatedRuns {
  items: Run[];
  total: number;
  page: number;
  limit: number;
}
