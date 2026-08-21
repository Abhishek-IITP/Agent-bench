# API Client & Hooks

This directory contains the data layer for the AgentBench dashboard, including a generic API client, type definitions, and custom React hooks for fetching data from the Elysia REST API.

## Files

### `api-client.ts`
Generic fetch wrapper for the Elysia REST API with the following features:
- **Type-safe responses**: Uses TypeScript generics for response typing
- **Error handling**: Network errors, timeouts (30s default), non-200 status codes
- **Retry logic**: Automatic retry on network failures (1 retry max)
- **Request/response logging**: Dev-only logging for debugging
- **Custom headers**: Automatic Content-Type header with support for extensions
- **Timeout handling**: Configurable per-request, defaults to 30 seconds

**Key Functions:**
- `fetchAPI<T>(endpoint, options)` - Generic fetch wrapper
- `fetchList<T>(resource, params)` - Fetch list with pagination
- `fetchById<T>(resource, id)` - Fetch single resource
- `createResource<T>(resource, data)` - POST create
- `updateResource<T>(resource, id, data)` - PATCH update
- `deleteResource(resource, id)` - DELETE resource
- `ApiError` - Custom error class with code, status, message

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` - Base API URL (defaults to http://localhost:3001)
- `NODE_ENV` - Set to "development" to enable logging

### `types.ts`
Complete TypeScript type definitions matching Elysia API responses:
- `Task` - Benchmark task with metadata
- `Run` - Single execution with results and metrics
- `RunMetrics` - Execution metrics (commands, files, tokens, cost)
- `TaskHealth` - Health status with success rate and variance
- `BenchmarkHealth` - Overall benchmark with summary
- `Leaderboard` - Agent rankings with scores
- `AgentScore` - Individual agent metrics
- `ReplayTrace` - Execution trace with events and metadata
- `TraceEvent` - Single event in execution timeline
- `PaginatedResponse<T>` - Generic paginated response wrapper
- `ApiResponse<T>` - Generic response wrapper

### `hooks.ts`
8 custom React hooks for data fetching from the API:

1. **`useTasks()`** - Fetch all tasks
   - Returns: `{ data: Task[] | null, loading: boolean, error: Error | null, refetch: () => void }`

2. **`useTask(id: string)`** - Fetch single task by ID
   - Skips fetch if id is empty
   - Re-fetches when ID changes

3. **`useRuns(filters?: RunsFilters)`** - Fetch runs with pagination
   - Supports filters: task_id, agent_name, status, page, limit
   - Default limit: 50 per page

4. **`useRun(id: string)`** - Fetch single run by ID

5. **`useTaskHealth()`** - Fetch health status for all tasks
   - Returns array of TaskHealth objects

6. **`useBenchmarkHealth()`** - Fetch overall benchmark health
   - Returns single BenchmarkHealth object

7. **`useLeaderboard()`** - Fetch agent rankings
   - Returns Leaderboard with agents sorted by score

8. **`useReplay(runId: string)`** - Fetch execution replay trace
   - For step-by-step replay of agent execution

**Hook Pattern:**
All hooks follow the same pattern:
```typescript
const { data, loading, error, refetch } = useHook(...);

// Use loading to show skeleton
// Use error to show error message
// Use refetch to manually refresh
// Use data when ready
```

**Hook Lifecycle:**
- On mount: Sets loading=true, fetches data
- On success: Sets data, loading=false, error=null
- On error: Sets error, loading=false, data=null
- On unmount: Cleans up (prevents memory leaks)
- On dependency change: Re-fetches data

## Usage Examples

### Fetch all tasks
```tsx
import { useTasks } from '@/lib/hooks';

export function TasksList() {
  const { data: tasks, loading, error, refetch } = useTasks();
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {tasks?.map(task => (
        <div key={task.id}>{task.name}</div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### Fetch single task with details
```tsx
import { useTask } from '@/lib/hooks';

export function TaskDetail({ taskId }: { taskId: string }) {
  const { data: task, loading, error } = useTask(taskId);
  
  if (loading) return <div>Loading task...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!task) return <div>Task not found</div>;
  
  return (
    <div>
      <h1>{task.name}</h1>
      <p>Category: {task.category}</p>
      <p>Difficulty: {task.difficulty}</p>
      <p>Timeout: {task.timeout}s</p>
    </div>
  );
}
```

### Fetch runs with filters
```tsx
import { useRuns } from '@/lib/hooks';

export function RunsPage() {
  const { data: runsPage, loading, error, refetch } = useRuns({
    task_id: 'task-123',
    agent_name: 'gpt-4',
    page: 1,
    limit: 50
  });
  
  if (loading) return <div>Loading runs...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <p>Total: {runsPage?.total} runs</p>
      <p>Page: {runsPage?.page} of {runsPage?.total_pages}</p>
      {/* Display runs */}
    </div>
  );
}
```

### Compare agent performance
```tsx
import { useLeaderboard } from '@/lib/hooks';

export function Leaderboard() {
  const { data: leaderboard, loading, error } = useLeaderboard();
  
  if (loading) return <div>Loading leaderboard...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <table>
      <thead>
        <tr>
          <th>Agent</th>
          <th>Score</th>
          <th>Reliability</th>
          <th>Tasks Solved</th>
          <th>Avg Cost</th>
        </tr>
      </thead>
      <tbody>
        {leaderboard?.agents.map(agent => (
          <tr key={agent.agent_name}>
            <td>{agent.agent_name}</td>
            <td>{agent.score}</td>
            <td>{(agent.reliability * 100).toFixed(1)}%</td>
            <td>{agent.tasks_solved}</td>
            <td>${agent.avg_cost.toFixed(4)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## API Endpoints

The hooks call the following Elysia API endpoints:

- `GET /api/tasks` → All tasks
- `GET /api/tasks/:id` → Single task
- `GET /api/runs` → Runs with filters & pagination
- `GET /api/runs/:id` → Single run
- `GET /api/health/tasks` → All task health
- `GET /api/health/benchmark` → Benchmark health
- `GET /api/leaderboard` → Agent rankings
- `GET /api/replays/:runId` → Execution replay

## Error Handling

All API calls are wrapped in try-catch. Errors are typed as `ApiError`:

```typescript
export class ApiError extends Error {
  code: string;      // e.g., "NETWORK_ERROR", "TIMEOUT", "HTTP_404"
  status: number;    // HTTP status or 0 for network errors
  message: string;   // User-friendly error message
}
```

## Best Practices

1. **Always handle loading state** - Show skeleton or spinner
2. **Always handle error state** - Show user-friendly error message
3. **Use refetch for manual updates** - Don't create new hook instances
4. **Guard against undefined data** - Check data exists before accessing properties
5. **Be mindful of dependencies** - Changing hook arguments triggers refetch
6. **Use pagination for large lists** - useRuns supports page/limit params

## Testing

Tests are in `__tests__/` directory (Note: Vitest integration tests are configured but currently skipped due to Next.js tsconfig plugin conflicts. Tests can be run after removing Next.js plugins from tsconfig for test builds):

- `types.test.ts` - Type definition validation
- (Additional integration tests to be added)

## Performance Optimization

- Request timeout: 30 seconds (configurable)
- Retry logic: Network errors only, max 1 retry with 500ms backoff
- Dev logging: Only in development mode
- Memoization ready: All hooks are compatible with useCallback/useMemo

## Future Enhancements

- [ ] Cache management (stale-while-revalidate)
- [ ] Optimistic updates
- [ ] Request deduplication
- [ ] Offline support
- [ ] Real-time updates (WebSocket)
- [ ] Request cancellation
- [ ] Rate limiting
