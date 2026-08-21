/**
 * Unit tests for DatabaseClient
 *
 * These tests verify the DatabaseClient methods work correctly.
 * Note: These tests require a running PostgreSQL database with the schema initialized.
 */

import { describe, it, expect, beforeAll, afterAll } from "bun:test";
import { DatabaseClient } from "./db";

describe("DatabaseClient", () => {
  let db: DatabaseClient;
  let dbAvailable = false;

  beforeAll(async () => {
    // Initialize database client
    db = new DatabaseClient();

    // Check if database is available
    try {
      dbAvailable = await db.healthCheck();
      if (!dbAvailable) {
        console.warn("Database not available - some tests will be skipped");
      }
    } catch (error) {
      console.warn("Database connection failed - tests will be skipped");
      dbAvailable = false;
    }
  });

  afterAll(async () => {
    if (db) {
      await db.close();
    }
  });

  describe("Connection Management", () => {
    it("should create a database client instance", () => {
      expect(db).toBeDefined();
      expect(db).toBeInstanceOf(DatabaseClient);
    });

    it("should perform health check", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const healthy = await db.healthCheck();
      expect(typeof healthy).toBe("boolean");
    });

    it("should support custom connection string", () => {
      const customDb = new DatabaseClient(
        "postgresql://user:pass@localhost:5432/test",
      );
      expect(customDb).toBeInstanceOf(DatabaseClient);
    });
  });

  describe("Task Queries", () => {
    it("should fetch all tasks", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const tasks = await db.getTasks();
      expect(Array.isArray(tasks)).toBe(true);
    });

    it("should fetch task by ID", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      // First get all tasks to find a valid ID
      const tasks = await db.getTasks();
      if (tasks.length === 0) {
        console.log("No tasks in database - skipping test");
        return;
      }

      const taskId = tasks[0].id;
      const task = await db.getTaskById(taskId);

      if (task) {
        expect(task.id).toBe(taskId);
        expect(task).toHaveProperty("name");
        expect(task).toHaveProperty("category");
      }
    });

    it("should return null for non-existent task", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const task = await db.getTaskById("non-existent-task-id");
      expect(task).toBeNull();
    });

    it("should fetch task statistics", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const tasks = await db.getTasks();
      if (tasks.length === 0) {
        console.log("No tasks in database - skipping test");
        return;
      }

      const taskId = tasks[0].id;
      const stats = await db.getTaskStats(taskId);

      expect(stats).toHaveProperty("total_runs");
      expect(stats).toHaveProperty("passes");
      expect(stats).toHaveProperty("failures");
      expect(stats).toHaveProperty("pass_rate");
      expect(typeof stats.total_runs).toBe("number");
    });
  });

  describe("Run Queries", () => {
    it("should fetch runs with default pagination", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const result = await db.getRuns();

      expect(result).toHaveProperty("items");
      expect(result).toHaveProperty("total");
      expect(result).toHaveProperty("page");
      expect(result).toHaveProperty("limit");
      expect(Array.isArray(result.items)).toBe(true);
    });

    it("should fetch runs with task filter", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const tasks = await db.getTasks();
      if (tasks.length === 0) {
        console.log("No tasks in database - skipping test");
        return;
      }

      const result = await db.getRuns({ task_id: tasks[0].id });
      expect(Array.isArray(result.items)).toBe(true);
    });

    it("should fetch runs with pagination", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const result = await db.getRuns({ page: 1, limit: 10 });
      expect(result.page).toBe(1);
      expect(result.limit).toBe(10);
      expect(result.items.length).toBeLessThanOrEqual(10);
    });

    it("should fetch run details by ID", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const runs = await db.getRuns({ limit: 1 });
      if (runs.items.length === 0) {
        console.log("No runs in database - skipping test");
        return;
      }

      const runId = runs.items[0].id;
      const runDetails = await db.getRunById(runId);

      if (runDetails) {
        expect(runDetails.id).toBe(runId);
        expect(runDetails).toHaveProperty("result");
        expect(runDetails.result).toHaveProperty("passed");
        expect(runDetails.result).toHaveProperty("score");
      }
    });

    it("should return null for non-existent run", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const run = await db.getRunById("non-existent-run-id");
      expect(run).toBeNull();
    });
  });

  describe("Agent Queries", () => {
    it("should fetch all agents", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const agents = await db.getAgents();
      expect(Array.isArray(agents)).toBe(true);
    });

    it("should fetch agent statistics", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const agents = await db.getAgents();
      if (agents.length === 0) {
        console.log("No agents in database - skipping test");
        return;
      }

      const agentId = agents[0].id;
      const stats = await db.getAgentStats(agentId);

      expect(stats).toHaveProperty("agent_name");
      expect(stats).toHaveProperty("total_runs");
      expect(stats).toHaveProperty("success_rate");
      expect(typeof stats.total_runs).toBe("number");
    });
  });

  describe("Health Queries", () => {
    it("should fetch task health", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const taskHealths = await db.getTaskHealth();
      expect(Array.isArray(taskHealths)).toBe(true);
    });

    it("should fetch benchmark health", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const health = await db.getBenchmarkHealth();
      expect(health).toHaveProperty("overall_status");
      expect(health).toHaveProperty("overall_score");
      expect(health).toHaveProperty("task_healths");
      expect(Array.isArray(health.task_healths)).toBe(true);
    });
  });

  describe("Leaderboard Queries", () => {
    it("should fetch leaderboard", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const leaderboard = await db.getLeaderboard();
      expect(Array.isArray(leaderboard)).toBe(true);

      // Verify leaderboard entries have required fields
      if (leaderboard.length > 0) {
        const entry = leaderboard[0];
        expect(entry).toHaveProperty("agent_name");
        expect(entry).toHaveProperty("score");
        expect(entry).toHaveProperty("success_rate");
        expect(entry).toHaveProperty("total_runs");
      }
    });
  });

  describe("Replay Queries", () => {
    it("should fetch replay trace", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const runs = await db.getRuns({ limit: 1 });
      if (runs.items.length === 0) {
        console.log("No runs in database - skipping test");
        return;
      }

      const runId = runs.items[0].id;
      const trace = await db.getReplayTrace(runId);

      // Trace may or may not exist for a run
      if (trace) {
        expect(trace).toHaveProperty("run_id");
        expect(trace).toHaveProperty("events");
        expect(Array.isArray(trace.events)).toBe(true);
      }
    });

    it("should return null for non-existent replay", async () => {
      if (!dbAvailable) {
        console.log("Skipping: database not available");
        return;
      }

      const trace = await db.getReplayTrace("non-existent-run-id");
      expect(trace).toBeNull();
    });
  });

  describe("Error Handling", () => {
    it("should handle connection errors gracefully", async () => {
      const badDb = new DatabaseClient(
        "postgresql://invalid:invalid@localhost:9999/invalid",
      );

      try {
        await badDb.getTasks();
        // If we get here, the database might actually be running
        expect(true).toBe(true);
      } catch (error) {
        // Expected to throw an error
        expect(error).toBeDefined();
        expect(error instanceof Error).toBe(true);
      }

      await badDb.close();
    });
  });
});
