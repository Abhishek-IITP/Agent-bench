# AgentBench REST API

The AgentBench API provides endpoints for accessing benchmark data, runs, results, and statistics.

## Server Setup

### Prerequisites
- Node.js/Bun 18+
- PostgreSQL database
- Python API running (for task data)

### Installation

```bash
cd dashboard/api
bun install
```

### Configuration

Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=agentbench
export DB_USER=postgres
export DB_PASSWORD=postgres
export PORT=3000
```

### Running

Development:
```bash
bun run dev
```

Production:
```bash
bun run build
bun start
```

## Endpoints

### Health Check
```
GET /api/health
```

Returns server status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-07-03T12:00:00Z"
}
```

### List Tasks
```
GET /api/tasks
```

Lists all benchmark tasks.

**Response:**
```json
{
  "tasks": [
    {
      "id": "find-database-files",
      "name": "Find Database Files",
      "category": "filesystem",
      "difficulty": "easy",
      "version": "1.0.0",
      "timeout": 300,
      "created_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

### Get Task Details
```
GET /api/tasks/:id
```

Get detailed information about a task including statistics.

**Response:**
```json
{
  "task": {
    "id": "find-database-files",
    "name": "Find Database Files",
    "category": "filesystem",
    "difficulty": "easy",
    "version": "1.0.0",
    "timeout": 300,
    "description": "Find all database files in the environment",
    "docker_image": "ubuntu:22.04",
    "created_at": "2026-07-01T10:00:00Z"
  },
  "stats": {
    "total_runs": 42,
    "passes": 38,
    "failures": 4,
    "pass_rate": 0.9047619047619048,
    "avg_duration": 12.5,
    "std_duration": 2.3
  }
}
```

### List Runs
```
GET /api/runs?task_id=find-database-files&agent_id=1&limit=50
```

List execution runs with optional filtering.

**Query Parameters:**
- `task_id` (optional): Filter by task
- `agent_id` (optional): Filter by agent
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
{
  "runs": [
    {
      "id": "run-uuid-123",
      "task_id": "find-database-files",
      "agent_id": 1,
      "started_at": "2026-07-03T10:00:00Z",
      "ended_at": "2026-07-03T10:00:15Z",
      "duration": 15.2,
      "success": true
    }
  ]
}
```

### Get Run Details
```
GET /api/runs/:id
```

Get detailed information about a specific run.

**Response:**
```json
{
  "run": {
    "id": "run-uuid-123",
    "task_id": "find-database-files",
    "agent_id": 1,
    "started_at": "2026-07-03T10:00:00Z",
    "ended_at": "2026-07-03T10:00:15Z",
    "duration": 15.2,
    "success": true
  },
  "result": {
    "id": 1,
    "run_id": "run-uuid-123",
    "passed": true,
    "score": 1.0,
    "test_output": "✓ PASS: test_output.py",
    "test_details": {
      "test_results": [
        {
          "test": "test_output.py",
          "exit_code": 0,
          "stdout": "All tests passed"
        }
      ]
    }
  },
  "metrics": {
    "commands_executed": 5,
    "files_created": 2,
    "files_modified": 0,
    "tokens_used": 2500,
    "cost": 0.042
  }
}
```

### Get Replay Trace
```
GET /api/replays/:run_id
```

Get the execution replay trace for replay and debugging.

**Response:**
```json
{
  "task_id": "find-database-files",
  "agent_name": "gpt-4",
  "agent_type": "openai",
  "model": "gpt-4",
  "started_at": "2026-07-03T10:00:00Z",
  "ended_at": "2026-07-03T10:00:15Z",
  "duration": 15.2,
  "success": true,
  "total_iterations": 3,
  "commands_executed": 5,
  "files_created": 2,
  "tokens_used": 2500,
  "cost": 0.042,
  "events": [
    {
      "timestamp": 1688000000.0,
      "type": "command_start",
      "content": "find / -name *.db",
      "duration": 0.5
    }
  ]
}
```

### Task Statistics
```
GET /api/stats/tasks
```

Get aggregated statistics for all tasks.

**Response:**
```json
{
  "stats": [
    {
      "task_id": "find-database-files",
      "task_name": "Find Database Files",
      "total_runs": 42,
      "passes": 38,
      "failures": 4,
      "pass_rate": 0.9047619047619048,
      "avg_duration": 12.5,
      "avg_cost": 0.021
    }
  ]
}
```

### Agent Statistics
```
GET /api/stats/agents
```

Get aggregated statistics for all agents.

**Response:**
```json
{
  "stats": [
    {
      "agent_id": 1,
      "agent_name": "gpt-4",
      "model": "gpt-4",
      "total_runs": 50,
      "passes": 45,
      "failures": 5,
      "pass_rate": 0.9,
      "avg_duration": 11.2,
      "total_cost": 2.15
    }
  ]
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Description of what went wrong",
  "code": "INTERNAL_SERVER_ERROR"
}
```

HTTP Status Codes:
- `200`: Success
- `404`: Resource not found
- `500`: Server error

## CORS

The API has CORS enabled for all origins. Customize in production:

```typescript
"Access-Control-Allow-Origin": "https://yourdomain.com"
```

## Authentication

Currently no authentication required. For production, implement:
- API key validation
- JWT tokens
- Rate limiting

See `src/index.ts` for middleware pattern.
