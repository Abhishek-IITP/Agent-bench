/**
 * Database Client for AgentBench API
 *
 * Provides typed database access with connection pooling and parameterized queries.
 * Implements all query methods needed by the API endpoints.
 */

import postgres from "postgres";
import type {
  Task,
  Run,
  RunDetails,
  Agent,
  TaskStats,
  AgentStats,
  LeaderboardEntry,
  TaskHealth,
  BenchmarkHealth,
  ReplayTrace,
  RunFilters,
  PaginatedRuns,
} from "./types";

export class DatabaseClient {
  private sql: postgres.Sql;

  /**
   * Initialize database client with connection pooling
   * @param connectionString Optional custom connection string
   */
  constructor(connectionString?: string) {
    if (connectionString) {
      this.sql = postgres(connectionString, {
        max: 10, // Maximum 10 connections in pool
      });
    } else {
      this.sql = postgres({
        host: process.env.DB_HOST || "127.0.0.1",
        port: parseInt(process.env.DB_PORT || "5433"),
        database: process.env.DB_NAME || "agentbench",
        user: process.env.DB_USER || "postgres",
        password: process.env.DB_PASSWORD || "postgres",
        max: 10, // Maximum 10 connections in pool
      });
    }
  }

  /**
   * Get all tasks
   */
  async getTasks(): Promise<Task[]> {
    try {
      const rows = await this.sql<Task[]>`
        SELECT 
          id, name, category, difficulty, version,
          description, timeout, docker_image,
          created_at::text as created_at,
          updated_at::text as updated_at
        FROM tasks
        ORDER BY created_at DESC
      `;
      return rows;
    } catch (error) {
      console.error("Error fetching tasks:", error);
      throw new Error("Failed to fetch tasks from database");
    }
  }

  /**
   * Get task by ID
   */
  async getTaskById(id: string): Promise<Task | null> {
    try {
      const rows = await this.sql<Task[]>`
        SELECT 
          id, name, category, difficulty, version,
          description, timeout, docker_image,
          created_at::text as created_at,
          updated_at::text as updated_at
        FROM tasks
        WHERE id = ${id}
      `;
      return rows.length > 0 ? rows[0] : null;
    } catch (error) {
      console.error(`Error fetching task ${id}:`, error);
      throw new Error(`Failed to fetch task ${id}`);
    }
  }

  /**
   * Get task statistics
   */
  async getTaskStats(id: string): Promise<TaskStats> {
    try {
      const rows = await this.sql<
        Array<{
          total_runs: number;
          passes: number;
          failures: number;
          pass_rate: number;
          avg_duration: number;
          std_duration: number;
        }>
      >`
        SELECT 
          COUNT(*) as total_runs,
          SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as passes,
          SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as failures,
          AVG(CASE WHEN success = true THEN 1.0 ELSE 0.0 END) as pass_rate,
          AVG(duration) as avg_duration,
          STDDEV(duration) as std_duration
        FROM runs
        WHERE task_id = ${id} AND ended_at IS NOT NULL
      `;

      if (rows.length === 0 || rows[0].total_runs === 0) {
        return {
          total_runs: 0,
          passes: 0,
          failures: 0,
          pass_rate: 0,
          avg_duration: 0,
          std_duration: 0,
        };
      }

      const row = rows[0];
      return {
        total_runs: Number(row.total_runs),
        passes: Number(row.passes),
        failures: Number(row.failures),
        pass_rate: Number(row.pass_rate || 0),
        avg_duration: Number(row.avg_duration || 0),
        std_duration: Number(row.std_duration || 0),
      };
    } catch (error) {
      console.error(`Error fetching stats for task ${id}:`, error);
      throw new Error(`Failed to fetch task statistics for ${id}`);
    }
  }

  /**
   * Get runs with filtering and pagination
   */
  async getRuns(filters: RunFilters = {}): Promise<PaginatedRuns> {
    try {
      const limit = filters.limit || 50;
      const page = filters.page || 1;
      const offset = filters.offset || (page - 1) * limit;

      // Execute query with parameterized filters
      const items = await this.sql<Run[]>`
        SELECT 
          r.id, r.task_id, r.agent_id,
          r.started_at::text as started_at,
          r.ended_at::text as ended_at,
          r.duration, r.success,
          r.created_at::text as created_at,
          a.name as agent_name,
          COALESCE(res.score, CASE WHEN r.success THEN 1.0 ELSE 0.0 END)::float as score
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        LEFT JOIN results res ON res.run_id = r.id
        ${filters.task_id ? this.sql`WHERE r.task_id = ${filters.task_id}` : this.sql``}
        ${filters.task_id && filters.agent_id ? this.sql`AND r.agent_id = ${filters.agent_id}` : !filters.task_id && filters.agent_id ? this.sql`WHERE r.agent_id = ${filters.agent_id}` : this.sql``}
        ${(filters.task_id || filters.agent_id) && filters.success !== undefined ? this.sql`AND r.success = ${filters.success}` : !filters.task_id && !filters.agent_id && filters.success !== undefined ? this.sql`WHERE r.success = ${filters.success}` : this.sql``}
        ORDER BY r.started_at DESC, r.created_at DESC
        LIMIT ${limit}
        OFFSET ${offset}
      `;

      // Get total count
      const countResult = await this.sql<Array<{ count: number }>>`
        SELECT COUNT(*) as count
        FROM runs r
        ${filters.task_id ? this.sql`WHERE r.task_id = ${filters.task_id}` : this.sql``}
        ${filters.task_id && filters.agent_id ? this.sql`AND r.agent_id = ${filters.agent_id}` : !filters.task_id && filters.agent_id ? this.sql`WHERE r.agent_id = ${filters.agent_id}` : this.sql``}
        ${(filters.task_id || filters.agent_id) && filters.success !== undefined ? this.sql`AND r.success = ${filters.success}` : !filters.task_id && !filters.agent_id && filters.success !== undefined ? this.sql`WHERE r.success = ${filters.success}` : this.sql``}
      `;

      const total = Number(countResult[0]?.count || 0);

      return {
        items,
        total,
        page,
        limit,
      };
    } catch (error) {
      console.error("Error fetching runs:", error);
      throw new Error("Failed to fetch runs from database");
    }
  }

  /**
   * Get run details by ID with results and metrics
   */
  async getRunById(id: string): Promise<RunDetails | null> {
    try {
      const rows = await this.sql<Array<any>>`
        SELECT 
          r.id, r.task_id, r.agent_id,
          r.started_at::text as started_at,
          r.ended_at::text as ended_at,
          r.duration, r.success,
          r.created_at::text as created_at,
          a.name as agent_name,
          res.passed, res.score, res.test_output, res.test_details, res.error_message,
          m.commands_executed, m.files_created, m.files_modified,
          m.tokens_used, m.cost, m.memory_peak_mb
        FROM runs r
        JOIN agents a ON r.agent_id = a.id
        LEFT JOIN results res ON r.id = res.run_id
        LEFT JOIN execution_metrics m ON r.id = m.run_id
        WHERE r.id = ${id}
      `;

      if (rows.length === 0) {
        return null;
      }

      const row = rows[0];

      const runDetails: RunDetails = {
        id: row.id,
        task_id: row.task_id,
        agent_id: row.agent_id,
        agent_name: row.agent_name,
        started_at: row.started_at,
        ended_at: row.ended_at,
        duration: row.duration,
        success: row.success,
        created_at: row.created_at,
        result: {
          passed: row.passed ?? false,
          score: row.score ?? 0,
          test_output: row.test_output ?? "",
          test_details: row.test_details ?? {},
          error_message: row.error_message,
        },
      };

      // Add metrics if available
      if (row.commands_executed !== null) {
        runDetails.metrics = {
          commands_executed: row.commands_executed,
          files_created: row.files_created,
          files_modified: row.files_modified,
          tokens_used: row.tokens_used,
          cost: row.cost,
          memory_peak_mb: row.memory_peak_mb,
        };
      }

      return runDetails;
    } catch (error) {
      console.error(`Error fetching run ${id}:`, error);
      throw new Error(`Failed to fetch run details for ${id}`);
    }
  }

  /**
   * Get all agents
   */
  async getAgents(): Promise<Agent[]> {
    try {
      const rows = await this.sql<Agent[]>`
        SELECT 
          id, name, type, model, config,
          created_at::text as created_at
        FROM agents
        ORDER BY created_at DESC
      `;
      return rows;
    } catch (error) {
      console.error("Error fetching agents:", error);
      throw new Error("Failed to fetch agents from database");
    }
  }

  /**
   * Get agent statistics
   */
  async getAgentStats(id: number): Promise<AgentStats> {
    try {
      const rows = await this.sql<Array<AgentStats>>`
        SELECT 
          a.name as agent_name,
          COUNT(r.id) as total_runs,
          COUNT(DISTINCT r.task_id) as tasks_solved,
          AVG(CASE WHEN r.success THEN 1.0 ELSE 0.0 END) as success_rate,
          AVG(m.cost) as avg_cost,
          AVG(m.tokens_used) as avg_tokens
        FROM agents a
        LEFT JOIN runs r ON a.id = r.agent_id
        LEFT JOIN execution_metrics m ON r.id = m.run_id
        WHERE a.id = ${id}
        GROUP BY a.id, a.name
      `;

      if (rows.length === 0) {
        return {
          agent_name: "",
          total_runs: 0,
          tasks_solved: 0,
          success_rate: 0,
          avg_cost: 0,
          avg_tokens: 0,
        };
      }

      const row = rows[0];
      return {
        agent_name: row.agent_name,
        total_runs: Number(row.total_runs),
        tasks_solved: Number(row.tasks_solved),
        success_rate: Number(row.success_rate || 0),
        avg_cost: Number(row.avg_cost || 0),
        avg_tokens: Number(row.avg_tokens || 0),
      };
    } catch (error) {
      console.error(`Error fetching stats for agent ${id}:`, error);
      throw new Error(`Failed to fetch agent statistics for ${id}`);
    }
  }

  /**
   * Get overall benchmark health
   */
  async getBenchmarkHealth(): Promise<BenchmarkHealth> {
    try {
      const taskHealths = await this.getTaskHealth();

      // Calculate overall score
      const totalTasks = taskHealths.length;
      if (totalTasks === 0) {
        return {
          overall_status: "unknown",
          overall_score: 0,
          task_healths: [],
        };
      }

      const healthyCount = taskHealths.filter(
        (t) => t.health_status === "healthy",
      ).length;
      const overallScore = Math.round((healthyCount / totalTasks) * 100);

      let overallStatus = "healthy";
      if (overallScore < 50) {
        overallStatus = "critical";
      } else if (overallScore < 75) {
        overallStatus = "warning";
      }

      return {
        overall_status: overallStatus,
        overall_score: overallScore,
        task_healths: taskHealths,
      };
    } catch (error) {
      console.error("Error fetching benchmark health:", error);
      throw new Error("Failed to fetch benchmark health");
    }
  }

  /**
   * Get task health classifications
   */
  async getTaskHealth(): Promise<TaskHealth[]> {
    try {
      const rows = await this.sql<Array<any>>`
        SELECT 
          task_id,
          health_status,
          success_rate,
          variance,
          n_agents,
          n_runs_total,
          evidence,
          recommendations,
          analyzed_at::text as analyzed_at
        FROM task_health
        ORDER BY analyzed_at DESC
      `;

      return rows.map((row) => ({
        task_id: row.task_id,
        health_status: row.health_status,
        success_rate: Number(row.success_rate),
        variance: Number(row.variance),
        n_agents: row.n_agents,
        n_runs_total: row.n_runs_total,
        evidence: row.evidence ? row.evidence.split("\n").filter(Boolean) : [],
        recommendations: row.recommendations
          ? row.recommendations.split("\n").filter(Boolean)
          : [],
        analyzed_at: row.analyzed_at,
      }));
    } catch (error) {
      console.error("Error fetching task health:", error);
      throw new Error("Failed to fetch task health data");
    }
  }

  /**
   * Get leaderboard rankings
   */
  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    try {
      const rows = await this.sql<Array<any>>`
        SELECT 
          a.name as agent_name,
          COUNT(DISTINCT r.task_id) as tasks_solved,
          COUNT(r.id) as total_runs,
          AVG(CASE WHEN r.success THEN 1.0 ELSE 0.0 END) as success_rate,
          AVG(m.cost) as avg_cost,
          AVG(m.tokens_used) as avg_tokens
        FROM agents a
        LEFT JOIN runs r ON a.id = r.agent_id AND r.ended_at IS NOT NULL
        LEFT JOIN execution_metrics m ON r.id = m.run_id
        GROUP BY a.id, a.name
        HAVING COUNT(r.id) > 0
        ORDER BY success_rate DESC, avg_cost ASC
      `;

      return rows.map((row) => ({
        agent_name: row.agent_name,
        score: Number(row.success_rate || 0) * 100,
        reliability: Number(row.success_rate || 0),
        success_rate: Number(row.success_rate || 0),
        avg_cost: Number(row.avg_cost || 0),
        avg_tokens: Number(row.avg_tokens || 0),
        total_runs: Number(row.total_runs),
        tasks_solved: Number(row.tasks_solved),
      }));
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      throw new Error("Failed to fetch leaderboard data");
    }
  }

  /**
   * Get replay trace for a run
   */
  async getReplayTrace(runId: string): Promise<ReplayTrace | null> {
    try {
      const rows = await this.sql<Array<{ data: any }>>`
        SELECT data
        FROM replays
        WHERE run_id = ${runId}
      `;

      if (rows.length === 0) {
        return null;
      }

      const replayData = rows[0].data;

      return {
        run_id: runId,
        events: replayData.events || [],
      };
    } catch (error) {
      console.error(`Error fetching replay trace for run ${runId}:`, error);
      throw new Error(`Failed to fetch replay trace for ${runId}`);
    }
  }

  /**
   * Check database connection health
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.sql`SELECT 1 as health`;
      return true;
    } catch (error) {
      console.error("Database health check failed:", error);
      return false;
    }
  }

  /**
   * Close database connection pool
   */
  async close(): Promise<void> {
    await this.sql.end();
  }
}
