"use client";

/**
 * Custom React hooks for fetching data from AgentBench API
 * All hooks follow the same pattern: { data, loading, error, refetch }
 */

import { useEffect, useState, useCallback } from "react";
import { fetchAPI, fetchList, fetchById, ApiError } from "./api-client";
import type {
  Task,
  Run,
  TaskHealth,
  BenchmarkHealth,
  Leaderboard,
  ReplayTrace,
  PaginatedResponse,
} from "./types";

/**
 * Generic hook state interface
 */
export interface UseDataState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

/**
 * Fetch all tasks
 * @returns Hook state with array of tasks
 *
 * @example
 * const { data: tasks, loading, error, refetch } = useTasks();
 */
export function useTasks(): UseDataState<Task[]> {
  const [data, setData] = useState<Task[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<{ tasks: Task[] }>("/api/tasks");
      setData(response.tasks);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    data,
    loading,
    error,
    refetch: fetchTasks,
  };
}

/**
 * Fetch a single task by ID
 * @param id - Task ID to fetch
 * @returns Hook state with task details
 *
 * @example
 * const { data: task, loading, error } = useTask("task-123");
 */
export function useTask(id: string): UseDataState<Task> {
  const [data, setData] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTask = useCallback(async () => {
    if (!id) {
      setData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<{ task: Task }>(`/api/tasks/${id}`);
      setData(response.task);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchTask();
  }, [fetchTask, id]);

  return {
    data,
    loading,
    error,
    refetch: fetchTask,
  };
}

/**
 * Runs filter options
 */
export interface RunsFilters {
  task_id?: string;
  agent_name?: string;
  status?: string;
  page?: number;
  limit?: number;
}

/**
 * Fetch runs with optional filtering and pagination
 * @param filters - Filter options (task_id, agent_name, status, page)
 * @returns Hook state with paginated runs
 *
 * @example
 * const { data: runs, loading, error, refetch } = useRuns({ task_id: "find-files", page: 1 });
 */
export function useRuns(
  filters?: RunsFilters
): UseDataState<PaginatedResponse<Run>> {
  const [data, setData] = useState<PaginatedResponse<Run> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Stringify filters to create a stable dependency
  const filtersKey = JSON.stringify(filters || {});

  const fetchRuns = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const parsedFilters = JSON.parse(filtersKey);
      const queryParams: Record<string, string | number | boolean> = {
        limit: parsedFilters?.limit || 50,
        page: parsedFilters?.page || 1,
      };

      if (parsedFilters?.task_id) queryParams.task_id = parsedFilters.task_id;
      if (parsedFilters?.agent_name) queryParams.agent_name = parsedFilters.agent_name;
      if (parsedFilters?.status) queryParams.status = parsedFilters.status;

      const response = await fetchList<PaginatedResponse<Run>>(
        "runs",
        queryParams
      );
      setData(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filtersKey]);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  return {
    data,
    loading,
    error,
    refetch: fetchRuns,
  };
}

/**
 * Fetch a single run by ID
 * @param id - Run ID to fetch
 * @returns Hook state with run details including results and metrics
 *
 * @example
 * const { data: run, loading, error } = useRun("run-abc-123");
 */
export function useRun(id: string): UseDataState<Run> {
  const [data, setData] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchRun = useCallback(async () => {
    if (!id) {
      setData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<any>(`/api/runs/${id}`);
      setData(response?.run || response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchRun();
  }, [fetchRun, id]);

  return {
    data,
    loading,
    error,
    refetch: fetchRun,
  };
}

/**
 * Fetch health status for all tasks
 * @returns Hook state with array of task health statuses
 *
 * @example
 * const { data: taskHealths, loading, error, refetch } = useTaskHealth();
 */
export function useTaskHealth(): UseDataState<TaskHealth[]> {
  const [data, setData] = useState<TaskHealth[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTaskHealth = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<{ task_healths: TaskHealth[] }>(
        "/api/health/tasks"
      );
      setData(response.task_healths);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTaskHealth();
  }, [fetchTaskHealth]);

  return {
    data,
    loading,
    error,
    refetch: fetchTaskHealth,
  };
}

/**
 * Fetch overall benchmark health status
 * @returns Hook state with benchmark health data
 *
 * @example
 * const { data: benchmarkHealth, loading, error, refetch } = useBenchmarkHealth();
 */
export function useBenchmarkHealth(): UseDataState<BenchmarkHealth> {
  const [data, setData] = useState<BenchmarkHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchBenchmarkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<BenchmarkHealth>(
        "/api/health/benchmark"
      );
      setData(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBenchmarkHealth();
  }, [fetchBenchmarkHealth]);

  return {
    data,
    loading,
    error,
    refetch: fetchBenchmarkHealth,
  };
}

/**
 * Fetch agent leaderboard rankings
 * @returns Hook state with leaderboard data containing ranked agents
 *
 * @example
 * const { data: leaderboard, loading, error, refetch } = useLeaderboard();
 */
export function useLeaderboard(): UseDataState<Leaderboard> {
  const [data, setData] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchLeaderboard = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<Leaderboard>("/api/leaderboard");
      setData(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  return {
    data,
    loading,
    error,
    refetch: fetchLeaderboard,
  };
}

/**
 * Fetch execution replay trace for a run
 * @param runId - ID of the run to get replay for
 * @returns Hook state with replay trace events
 *
 * @example
 * const { data: replay, loading, error } = useReplay("run-123");
 */
export function useReplay(runId: string): UseDataState<ReplayTrace> {
  const [data, setData] = useState<ReplayTrace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchReplay = useCallback(async () => {
    if (!runId) {
      setData(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchAPI<ReplayTrace>(`/api/replays/${runId}`);
      setData(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    fetchReplay();
  }, [fetchReplay, runId]);

  return {
    data,
    loading,
    error,
    refetch: fetchReplay,
  };
}
