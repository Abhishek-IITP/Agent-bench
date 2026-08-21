/**
 * TypeScript type definitions for AgentBench API responses
 * These types match the Elysia REST API responses
 */

/**
 * Represents a benchmark task
 */
export interface Task {
  /** Unique task identifier */
  id: string;
  /** Human-readable task name */
  name: string;
  /** Category the task belongs to (e.g., "filesystem", "database") */
  category: string;
  /** Task difficulty level (easy, medium, hard) */
  difficulty: "easy" | "medium" | "hard";
  /** Maximum execution time in seconds */
  timeout: number;
  /** Task creation timestamp */
  created_at: string;
  /** Task last update timestamp */
  updated_at: string;
  /** Optional: task description */
  description?: string;
  /** Optional: Docker image used for task */
  docker_image?: string;
  /** Optional: task version */
  version?: string;
}

/**
 * Represents a single execution run of an agent on a task
 */
export interface Run {
  /** Unique run identifier */
  id: string;
  /** ID of the task being run */
  task_id: string;
  /** Name/identifier of the agent */
  agent_name: string;
  /** Execution status (success, failure, timeout, error) */
  status: "success" | "failure" | "timeout" | "error";
  /** Optional boolean success flag */
  success?: boolean;
  /** Run reliability/success score (0-1) */
  score: number;
  /** Cost of the run in dollars */
  cost: number;
  /** Execution duration in seconds */
  duration: number;
  /** Run creation timestamp */
  created_at: string;
  /** Optional: trace/execution details */
  trace?: string;
  /** Optional: test results */
  test_output?: string;
  /** Optional: detailed metrics */
  metrics?: RunMetrics;
}

/**
 * Additional metrics for a run
 */
export interface RunMetrics {
  /** Number of commands executed */
  commands_executed: number;
  /** Number of files created */
  files_created: number;
  /** Number of files modified */
  files_modified: number;
  /** Total tokens used */
  tokens_used: number;
}

/**
 * Health status of a single task
 */
export interface TaskHealth {
  /** Task ID */
  task_id: string;
  /** Health status (healthy, flaky, broken, trivial, saturated) */
  health_status: "healthy" | "flaky" | "broken" | "trivial" | "saturated";
  /** Success rate as decimal (0-1) */
  success_rate: number;
  /** Variance in success rates */
  variance: number;
  /** Number of agents tested on this task */
  n_agents: number;
  /** Total number of runs for this task */
  n_runs_total: number;
  /** Array of reasons for current health status */
  reasons: string[];
}

/**
 * Overall benchmark health status
 */
export interface BenchmarkHealth {
  /** Overall health status of the benchmark */
  overall_status: "healthy" | "flaky" | "broken";
  /** Health status for each task */
  task_healths: TaskHealth[];
  /** Timestamp of the health assessment */
  timestamp: string;
  /** Summary statistics */
  summary?: {
    healthy_count: number;
    flaky_count: number;
    broken_count: number;
    trivial_count: number;
    saturated_count: number;
  };
}

/**
 * Agent score/ranking information
 */
export interface AgentScore {
  /** Agent name/identifier */
  agent_name: string;
  /** Overall score (0-100) */
  score: number;
  /** Reliability score (0-1) */
  reliability: number;
  /** Number of tasks successfully solved */
  tasks_solved: number;
  /** Average cost per run */
  avg_cost: number;
  /** Average tokens used per run */
  avg_tokens: number;
  /** Optional: total number of runs */
  total_runs?: number;
  /** Optional: success rate */
  success_rate?: number;
}

/**
 * Leaderboard with ranked agents
 */
export interface Leaderboard {
  /** Array of agents ranked by score */
  agents: AgentScore[];
  /** Timestamp of the leaderboard update */
  timestamp: string;
}

/**
 * A single event in an execution replay
 */
export interface TraceEvent {
  /** Event type (command, output, error, etc.) */
  type: "command" | "output" | "error" | "tool_call" | "step_start" | "step_end";
  /** Event timestamp */
  timestamp: number;
  /** Event content (command text, output, error message) */
  content: string;
  /** Optional: status of the event */
  status?: "pending" | "success" | "failure";
  /** Optional: duration if applicable */
  duration?: number;
}

/**
 * Complete replay trace for a run
 */
export interface ReplayTrace {
  /** Array of events in execution order */
  events: TraceEvent[];
  /** Metadata about the replay */
  metadata: {
    task_id: string;
    agent_name: string;
    agent_type: string;
    model: string;
    started_at: string;
    ended_at: string;
    duration: number;
    success: boolean;
    total_iterations: number;
    commands_executed: number;
    files_created: number;
    tokens_used: number;
    cost: number;
  };
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  error?: string;
  timestamp?: string;
}

/**
 * Paginated API response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
