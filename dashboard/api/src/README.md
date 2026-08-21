# AgentBench API - Database Integration

This directory contains the TypeScript types and database client for the AgentBench API.

## Files

- **`types.ts`** - TypeScript type definitions matching the PostgreSQL database schema
- **`db.ts`** - DatabaseClient class with connection pooling and query methods
- **`types.test.ts`** - Unit tests for type definitions
- **`db.test.ts`** - Unit tests for DatabaseClient
- **`index.ts`** - Main API server with Elysia endpoints

## TypeScript Types

The `types.ts` file defines interfaces that match the database schema:

- `Task` - Task metadata
- `Agent` - Agent configuration
- `Run` - Execution record
- `RunDetails` - Detailed run with results and metrics
- `TaskStats` - Task statistics aggregation
- `AgentStats` - Agent statistics
- `LeaderboardEntry` - Leaderboard ranking
- `TaskHealth` - Task health classification
- `BenchmarkHealth` - Overall benchmark health
- `ReplayTrace` - Execution replay data

## DatabaseClient

The `DatabaseClient` class provides typed database access with the following features:

### Connection Management

```typescript
import { DatabaseClient } from './db';

// Use environment variables
const db = new DatabaseClient();

// Or provide custom connection string
const db = new DatabaseClient('postgresql://user:pass@localhost:5432/agentbench');

// Check health
const healthy = await db.healthCheck();

// Close connection
await db.close();
```

### Query Methods

#### Tasks

```typescript
// Get all tasks
const tasks = await db.getTasks();

// Get task by ID
const task = await db.getTaskById('find-database-files');

// Get task statistics
const stats = await db.getTaskStats('find-database-files');
```

#### Runs

```typescript
// Get runs with pagination
const runs = await db.getRuns({ page: 1, limit: 50 });

// Get runs filtered by task
const taskRuns = await db.getRuns({ task_id: 'find-database-files' });

// Get run details with results and metrics
const runDetails = await db.getRunById('run-123');
```

#### Agents

```typescript
// Get all agents
const agents = await db.getAgents();

// Get agent statistics
const stats = await db.getAgentStats(1);
```

#### Health & Leaderboard

```typescript
// Get task health classifications
const taskHealths = await db.getTaskHealth();

// Get overall benchmark health
const health = await db.getBenchmarkHealth();

// Get leaderboard
const leaderboard = await db.getLeaderboard();
```

#### Replays

```typescript
// Get replay trace for a run
const trace = await db.getReplayTrace('run-123');
```

## Configuration

The database client reads connection parameters from environment variables:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agentbench
DB_USER=postgres
DB_PASSWORD=postgres
```

## Connection Pooling

The client uses a connection pool with a maximum of 10 connections. This is configured automatically when the client is initialized.

## Error Handling

All query methods implement error handling:

- Catch database errors and log them
- Throw descriptive error messages
- Return `null` for non-existent resources (e.g., task not found)
- Return empty arrays/default objects when no data exists

## Parameterized Queries

All queries use parameterized queries via the `postgres` library to prevent SQL injection:

```typescript
// Safe - parameterized
const task = await this.sql`SELECT * FROM tasks WHERE id = ${id}`;

// Never do this - SQL injection risk
const task = await this.sql`SELECT * FROM tasks WHERE id = '${id}'`;
```

## Testing

Run the test suite:

```bash
bun test
```

Tests will skip database-dependent tests if the database is not available.

## Requirements Coverage

This implementation satisfies the following requirements:

- **REQ-1.4.1**: API connects to PostgreSQL using `postgres` library
- **REQ-1.4.2**: API reads connection parameters from environment variables
- **REQ-1.4.6**: All queries use parameterized queries
- **REQ-1.4.7**: Connection pooling with maximum 10 connections

## Type Safety

All methods are fully typed with TypeScript interfaces. The compiler will catch type mismatches at build time.

Example:

```typescript
// Type-safe query
const task: Task | null = await db.getTaskById('my-task');

// TypeScript enforces the type
if (task) {
  console.log(task.name); // ✓ Valid
  console.log(task.invalid); // ✗ Compile error
}
```
