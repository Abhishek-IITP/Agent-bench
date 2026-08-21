/**
 * Unit tests for TypeScript type definitions
 */

import { describe, it, expect } from "bun:test";
import type {
  Task,
  Agent,
  Run,
  RunDetails,
  TaskStats,
  LeaderboardEntry,
  TaskHealth,
  BenchmarkHealth,
  ReplayTrace,
} from "./types";

describe("Type Definitions", () => {
  it("should create a valid Task object", () => {
    const task: Task = {
      id: "test-task",
      name: "Test Task",
      category: "test",
      difficulty: "easy",
      version: "1.0.0",
      timeout: 300,
      docker_image: "ubuntu:22.04",
      created_at: new Date().toISOString(),
    };

    expect(task.id).toBe("test-task");
    expect(task.name).toBe("Test Task");
    expect(task.category).toBe("test");
  });

  it("should create a valid Agent object", () => {
    const agent: Agent = {
      id: 1,
      name: "test-agent",
      type: "openai",
      model: "gpt-4",
      config: { temperature: 0.7 },
      created_at: new Date().toISOString(),
    };

    expect(agent.id).toBe(1);
    expect(agent.name).toBe("test-agent");
    expect(agent.config).toHaveProperty("temperature");
  });

  it("should create a valid Run object", () => {
    const run: Run = {
      id: "run-123",
      task_id: "test-task",
      agent_id: 1,
      started_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    };

    expect(run.id).toBe("run-123");
    expect(run.task_id).toBe("test-task");
    expect(run.agent_id).toBe(1);
  });

  it("should create a valid RunDetails object", () => {
    const runDetails: RunDetails = {
      id: "run-123",
      task_id: "test-task",
      agent_id: 1,
      agent_name: "test-agent",
      started_at: new Date().toISOString(),
      ended_at: new Date().toISOString(),
      duration: 45.2,
      success: true,
      created_at: new Date().toISOString(),
      result: {
        passed: true,
        score: 0.95,
        test_output: "All tests passed",
        test_details: { tests_run: 5 },
      },
      metrics: {
        commands_executed: 12,
        files_created: 3,
        files_modified: 2,
        tokens_used: 1847,
        cost: 0.0487,
      },
    };

    expect(runDetails.result.passed).toBe(true);
    expect(runDetails.metrics?.cost).toBe(0.0487);
  });

  it("should create a valid TaskStats object", () => {
    const stats: TaskStats = {
      total_runs: 10,
      passes: 8,
      failures: 2,
      pass_rate: 0.8,
      avg_duration: 45.2,
      std_duration: 5.3,
    };

    expect(stats.total_runs).toBe(10);
    expect(stats.pass_rate).toBe(0.8);
  });

  it("should create a valid LeaderboardEntry object", () => {
    const entry: LeaderboardEntry = {
      agent_name: "gpt-4",
      score: 85.5,
      reliability: 0.855,
      success_rate: 0.855,
      avg_cost: 0.05,
      avg_tokens: 1800,
      total_runs: 50,
      tasks_solved: 15,
    };

    expect(entry.agent_name).toBe("gpt-4");
    expect(entry.score).toBe(85.5);
  });

  it("should create a valid TaskHealth object", () => {
    const health: TaskHealth = {
      task_id: "test-task",
      health_status: "healthy",
      success_rate: 0.87,
      variance: 0.05,
      n_agents: 3,
      n_runs_total: 45,
      evidence: ["Stable performance across agents"],
      recommendations: ["Continue monitoring"],
    };

    expect(health.health_status).toBe("healthy");
    expect(health.evidence).toBeArrayOfSize(1);
  });

  it("should create a valid BenchmarkHealth object", () => {
    const benchmarkHealth: BenchmarkHealth = {
      overall_status: "healthy",
      overall_score: 85,
      task_healths: [],
    };

    expect(benchmarkHealth.overall_status).toBe("healthy");
    expect(benchmarkHealth.overall_score).toBe(85);
  });

  it("should create a valid ReplayTrace object", () => {
    const trace: ReplayTrace = {
      run_id: "run-123",
      events: [
        { timestamp: 0, type: "command", content: "ls -la" },
        { timestamp: 0.5, type: "output", content: "[output]" },
      ],
    };

    expect(trace.run_id).toBe("run-123");
    expect(trace.events).toBeArrayOfSize(2);
  });
});
