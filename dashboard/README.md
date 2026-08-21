# AgentBench Dashboard

## Overview

The AgentBench Dashboard is a comprehensive web interface for monitoring, analyzing, and visualizing the performance of AI agents across benchmark tasks. Built with Next.js 14+, Tailwind CSS, shadcn/ui, and Apache ECharts, the dashboard provides real-time insights into agent reliability, task health, and benchmarking metrics.

**Stack:**
- **Frontend:** Next.js 14+, TypeScript, Tailwind CSS, shadcn/ui
- **Backend API:** Bun + Elysia, PostgreSQL
- **Visualizations:** Apache ECharts
- **Database:** PostgreSQL (with graceful fallback to file storage)
- **UI Components:** shadcn/ui + custom components

---

## Project Structure

```
dashboard/
├── web/                              # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx                  # Home/Overview page
│   │   ├── layout.tsx                # Root layout with sidebar
│   │   ├── globals.css               # Global styles
│   │   ├── error.tsx                 # Error boundary
│   │   ├── not-found.tsx             # 404 page
│   │   ├── tasks/
│   │   │   ├── page.tsx              # Tasks list & management
│   │   │   └── [id]/
│   │   │       └── page.tsx          # Task detail & analytics
│   │   ├── runs/
│   │   │   └── page.tsx              # Run history & filtering
│   │   ├── leaderboard/
│   │   │   └── page.tsx              # Agent rankings & comparison
│   │   ├── health/
│   │   │   └── page.tsx              # Benchmark health dashboard
│   │   └── replay/
│   │       └── page.tsx              # Replay viewer (dynamic routes)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx            # Top navigation bar
│   │   │   ├── Sidebar.tsx           # Left navigation sidebar
│   │   │   ├── Footer.tsx            # Page footer
│   │   │   └── LayoutWrapper.tsx     # Layout container
│   │   ├── cards/
│   │   │   ├── StatsCard.tsx         # KPI metric cards
│   │   │   └── HealthStatusBadge.tsx # Health status indicator
│   │   ├── tables/
│   │   │   ├── TasksTable.tsx        # Tasks data table
│   │   │   └── RunsTable.tsx         # Runs data table
│   │   ├── charts/
│   │   │   ├── SuccessRateChart.tsx  # Bar chart for success rates
│   │   │   ├── ReliabilityChart.tsx  # Line chart for reliability trends
│   │   │   ├── DifficultyChart.tsx   # Distribution of task difficulties
│   │   │   ├── AgentComparison.tsx   # Multi-agent comparison chart
│   │   │   ├── HealthOverview.tsx    # Task health grid/treemap
│   │   │   └── CostAnalysis.tsx      # Cost and token usage charts
│   │   ├── widgets/
│   │   │   ├── RecentRunsWidget.tsx  # Latest execution results
│   │   │   ├── TopAgentsWidget.tsx   # Top performing agents
│   │   │   ├── TopTasksWidget.tsx    # Most executed tasks
│   │   │   └── BenchmarkHealth.tsx   # Overall benchmark health badge
│   │   └── replay/
│   │       └── ReplayViewer.tsx      # Timeline visualization
│   ├── lib/
│   │   ├── api-client.ts             # API client wrapper
│   │   ├── hooks.ts                  # Custom React hooks (useFetch, useFilter, etc.)
│   │   └── utils.ts                  # Utility functions
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts
│
├── api/                              # Bun + Elysia backend
│   ├── src/
│   │   ├── index.ts                  # API entry point
│   │   ├── routes/
│   │   │   ├── tasks.ts              # Task endpoints
│   │   │   ├── runs.ts               # Run endpoints
│   │   │   ├── stats.ts              # Statistics endpoints
│   │   │   ├── health.ts             # Health analysis endpoints
│   │   │   ├── replays.ts            # Replay endpoints
│   │   │   └── agents.ts             # Agent endpoints
│   │   ├── db/
│   │   │   ├── schema.ts             # Drizzle ORM schema
│   │   │   └── schema.sql            # PostgreSQL schema
│   │   └── middleware/
│   │       ├── cors.ts               # CORS middleware
│   │       ├── auth.ts               # Authentication (optional)
│   │       └── logging.ts            # Request logging
│   ├── package.json
│   └── tsconfig.json
│
└── README.md                         # This file
```

---

## Pages & Features

### 1. **Home / Overview Page** (`/`)

**Purpose:** Dashboard landing page providing a high-level summary of the entire benchmark.

**Key Components:**
- **KPI Cards:** Display aggregate statistics
  - Total tasks in benchmark
  - Total runs executed
  - Overall success rate
  - Average reliability score
  - Overall benchmark health status

- **Widgets:**
  - **Recent Runs Widget:** Shows last 5-10 executed runs with status badges (✅ pass, ❌ fail, ⏱️ timeout)
  - **Top Agents Widget:** Ranked list of top 5 agents by reliability score
  - **Top Tasks Widget:** Most frequently tested tasks with success rates
  - **Benchmark Health Badge:** Single metric showing overall health (Healthy, Flaky, Broken, Saturated)

- **Quick Actions:**
  - "Start New Benchmark Run" button
  - "View All Tasks" link
  - "View Leaderboard" link
  - "Analyze Health" link

**Data Fetched:**
```
GET /api/stats/tasks        → Task statistics
GET /api/stats/agents       → Agent rankings
GET /api/runs?limit=10      → Recent runs
GET /api/health/benchmark   → Overall health
```

**Visuals:**
- Stats cards with trend indicators (↑/↓)
- Color-coded health status (Green/Yellow/Red)
- Mini widgets with scroll-able content

---

### 2. **Tasks Page** (`/tasks`)

**Purpose:** Centralized task management and monitoring dashboard.

**Key Features:**

#### Data Table
- **Columns:**
  - Task ID / Name
  - Category (filesystem, data-processing, debugging, etc.)
  - Difficulty (easy, medium, hard, expert)
  - Health Status (with color-coded badge)
  - Success Rate (0-100%, with percentage bar)
  - Total Runs Executed
  - Last Run Timestamp
  - Actions (View Details, Edit, Run)

#### Filters & Search
- **Filter by:**
  - Difficulty level (easy/medium/hard/expert)
  - Health status (healthy/flaky/broken/trivial/saturated)
  - Category (dropdown)
  - Success rate range (slider: 0-100%)
  
- **Search:**
  - Search by task name or ID (real-time filtering)

#### Sorting
- Clickable column headers to sort by any field
- Multi-column sort (Shift+click for secondary sort)

#### Bulk Actions
- Select multiple tasks with checkboxes
- Bulk re-run, bulk export, bulk calibration

#### Statistics Panel
- Total tasks
- Distribution by difficulty
- Distribution by health status
- Tasks needing attention (flaky/broken count)

**Data Fetched:**
```
GET /api/tasks                    → All tasks with metadata
GET /api/stats/tasks             → Per-task statistics
GET /api/health/tasks            → Health status for each task
```

**Visuals:**
- Paginated table (20 rows per page)
- Color-coded status badges
- Progress bars for success rates
- Filter badges showing active filters

---

### 3. **Task Detail Page** (`/tasks/[id]`)

**Purpose:** Deep dive into a specific task's performance and analytics.

**Layout:**

#### Header Section
- Task name, ID, category, difficulty
- Health status badge with explanation
- Last executed time
- Total execution count

#### Key Metrics Cards
- Success Rate (%)
- Reliability Score (0-100)
- Confidence Interval (95% CI, e.g., [75%, 95%])
- Variance (measure of consistency)
- Mean Runtime (seconds)
- Mean Cost (tokens, API cost if available)

#### Charts Section

**Success Rate by Agent (Bar Chart)**
- X-axis: Agent names
- Y-axis: Success rate (0-100%)
- Color gradient (red = low, green = high)
- Hover shows exact percentage and run count

**Reliability Over Time (Line Chart)**
- X-axis: Date/timestamp of runs
- Y-axis: Reliability score (0-100)
- Multiple lines for different agents
- Trend line showing overall trajectory
- Shaded confidence interval band

**Execution History (Table)**
- Columns: Timestamp, Agent, Status (pass/fail), Runtime, Tokens Used, Cost
- 50 most recent runs
- Sortable and filterable
- Link to replay for each run

**Test Results Distribution**
- Pie chart: Pass vs Fail breakdown
- Detailed breakdown by test case (if available)

#### Health Analysis Section
- Current health status with explanation
- Evidence for classification:
  - "FLAKY: 6 agents show >5% inter-run variance"
  - "BROKEN: Oracle validation failing since 2026-07-03"
  - etc.
- Recommendations:
  - "Increase task timeout" / "Fix test harness" / "Consider retiring"

#### Difficulty Calibration Section
- Author-assigned difficulty
- Empirical difficulty (based on agent performance)
- Mismatch indicator (⚠️ if different)
- Confidence level
- Recommendation: "Task is harder than expected, consider re-categorizing"

#### Run Comparison (Optional)
- Compare specific runs by timestamp
- Side-by-side agent performance

**Data Fetched:**
```
GET /api/tasks/:id                        → Task metadata
GET /api/stats/tasks/:id                  → Task statistics
GET /api/runs?task_id=:id&limit=50       → Execution history
GET /api/health/tasks/:id                 → Health analysis
GET /api/stats/tasks/:id/calibration     → Difficulty calibration
```

**Visuals:**
- Multiple synchronized charts
- Color-coded status indicators
- Expandable/collapsible sections
- Export button (CSV, JSON)

---

### 4. **Runs Page** (`/runs`)

**Purpose:** Complete history of all benchmark executions with advanced filtering and search.

**Key Features:**

#### Runs Table
- **Columns:**
  - Run ID (unique identifier)
  - Task Name / ID
  - Agent Name
  - Timestamp (date + time)
  - Status (pass ✅, fail ❌, timeout ⏱️, partial ⚠️)
  - Result (success rate if applicable)
  - Runtime (seconds)
  - Tokens Used
  - Cost (if tracked)
  - Actions (View Details, View Replay, Edit)

#### Advanced Filters
- **By Task:** Dropdown/search for task selection
- **By Agent:** Dropdown/search for agent selection
- **By Status:** Checkboxes (pass, fail, timeout, partial, error)
- **By Date Range:** Date picker for start/end dates
- **By Runtime:** Range slider (min-max seconds)
- **By Success Rate:** Range slider (0-100%)

#### Search
- Real-time search by run ID, task name, or agent name

#### Export & Analysis
- Export filtered results (CSV, JSON)
- Batch download replays
- Comparison tool (select 2+ runs)

#### Sorting
- Sort by any column (timestamp, status, runtime, cost, etc.)

#### Pagination
- 50 rows per page (configurable)
- Jump to page, previous/next controls

#### Statistics
- Total runs in view
- Pass rate
- Average runtime
- Total cost
- Slowest run
- Most expensive run

**Data Fetched:**
```
GET /api/runs?task=&agent=&status=&date_from=&date_to=&limit=50
GET /api/stats/tasks       → For task dropdown
GET /api/stats/agents      → For agent dropdown
```

**Visuals:**
- Paginated sortable table
- Status badges (green/red/yellow)
- Filter pills showing active filters
- Clear filters button

---

### 5. **Leaderboard Page** (`/leaderboard`)

**Purpose:** Agent ranking and comparison dashboard.

**Layout:**

#### Main Leaderboard Table
- **Columns:**
  - Rank (1, 2, 3, ...)
  - Agent Name / Model
  - Overall Reliability Score (0-100, primary sort)
  - Success Rate (%)
  - Tasks Solved (count)
  - Average Runtime (seconds)
  - Total Cost (sum of all tokens/API costs)
  - Cost Efficiency (score per dollar)
  - Consistency Score (0-100, measure of variance)
  - Trend (↑ improving, ↓ declining, → stable)

#### Filtering & Sorting
- **Sort by:** Any column (default: Reliability Score descending)
- **Filter by:**
  - Agent type (OpenAI, Ollama, custom)
  - Task category (if you want category-specific leaderboard)
  - Date range (last 7 days, 30 days, all-time)

#### Agent Comparison Tool
- **Select 2-3 agents to compare**
- Side-by-side metrics view
- **Comparison Chart:**
  - Radar chart showing 5 dimensions:
    1. Reliability Score
    2. Success Rate
    3. Cost Efficiency
    4. Consistency
    5. Speed (inverse of avg runtime)
  - Color-coded by agent
  - Legend identifying agents

#### Per-Task Breakdown (Table)
- Shows how each agent performs on each task category
- Heatmap view: Agent vs Task Category success rates
- Darker green = higher success rate

#### Statistics Panel
- Average reliability score across all agents
- Best agent
- Most consistent agent
- Most cost-efficient agent
- Fastest agent

#### Trend Analysis
- Line chart: Top 3 agents' reliability scores over time
- Shaded confidence intervals
- Volume of runs per agent

**Data Fetched:**
```
GET /api/leaderboard                 → Ranked agent list
GET /api/stats/agents                → Agent statistics
GET /api/runs?agent=:name           → Agent run history (for trends)
GET /api/stats/agents/:name/vs/     → Agent comparison data
```

**Visuals:**
- Ranked table with medal icons (🥇🥈🥉)
- Radar chart for comparison
- Heatmap for task performance
- Line chart for trends
- Color-coded badges for achievements (e.g., "Perfect Consistency")

---

### 6. **Health Dashboard Page** (`/health`)

**Purpose:** Monitor and analyze the overall health and quality of the benchmark.

**Layout:**

#### Overall Health Score
- Large metric card: 0-100 score
- Color indicator (green/yellow/red)
- Trend line (improving/declining)
- Last updated timestamp

#### Health Status Grid / Treemap
- Visual representation of all tasks
- Each task shown as a colored box
- Color coding:
  - 🟢 **Green (HEALTHY):** Stable, consistent performance
  - 🟡 **Yellow (FLAKY):** Inconsistent, needs investigation
  - 🔴 **Red (BROKEN):** Failed tests, not working
  - ⚪ **White (TRIVIAL):** All agents pass (too easy)
  - 🟣 **Purple (SATURATED):** All top agents at 100% (needs harder variant)

- **Click on a task** to drill down into details

#### Health Distribution Charts

**Pie Chart: Health Status Distribution**
- Percentage of tasks in each health category
- Legend showing counts

**Bar Chart: Health by Category**
- X-axis: Task categories (filesystem, data-processing, etc.)
- Y-axis: Count of tasks
- Stacked bars colored by health status
- Shows if certain categories have more issues

**Line Chart: Health Trend Over Time**
- X-axis: Date
- Y-axis: Overall benchmark health score
- Shows improvement/degradation over time

#### Problematic Tasks Section
- Table of tasks that need attention:
  - BROKEN tasks (with repair recommendations)
  - FLAKY tasks (with debugging suggestions)
  - SATURATED tasks (with suggestions to create harder variants)

#### Recommendations Panel
- Auto-generated action items:
  - "Task X is flaky: Consider increasing timeout"
  - "Task Y is broken: Fix test harness in Z location"
  - "Task Z is saturated: Create expert-level variant"
  - "Category A has 60% broken tasks: Investigate infrastructure"

#### Calibration Mismatches
- Table of tasks where author-assigned difficulty doesn't match empirical:
  - Task name
  - Author difficulty
  - Empirical difficulty
  - Confidence
  - Mismatch severity (low/medium/high)

**Data Fetched:**
```
GET /api/health/benchmark              → Overall health score
GET /api/health/tasks                  → Health status for all tasks
GET /api/stats/tasks                   → Task statistics
GET /api/calibration                   → Difficulty calibrations
```

**Visuals:**
- Large health score metric
- Color-coded treemap / grid
- Pie and bar charts
- Trend line chart
- Expandable recommendation cards
- Mismatch alert table

---

### 7. **Replay Viewer Page** (`/replay/[runId]`)

**Purpose:** Step-by-step visualization of how an agent solved a task.

**Layout:**

#### Header
- Task name, agent name, run ID
- Timestamp, duration, status badge (✅ pass, ❌ fail, etc.)
- Overall result metrics

#### Timeline / Event Stream
- **Vertical timeline** showing chronological events
- Each event marked with:
  - Timestamp (relative: "0.0s", "0.3s", "1.2s", etc.)
  - Event type icon (🖥️ command, 📋 output, ⚠️ error, ✓ success)
  - Event description

#### Event Details Panel (Right Side)
- **When you click on an event in timeline:**
  - Command executed (e.g., `ls -la`)
  - Output produced (full text, scrollable)
  - Duration for this step
  - Any errors or warnings

#### Color Coding
- 🔵 **Blue:** Command execution
- ⚪ **Gray:** Standard output
- 🟠 **Orange:** Warning messages
- 🔴 **Red:** Error messages
- 🟢 **Green:** Success/completion messages

#### Playback Controls
- ⏮️ Jump to start
- ◀️ Previous event
- ▶️ Next event
- ⏭️ Jump to end
- ⏸️ Pause / ▶️ Play (auto-advance through events)
- Speed control (0.5x, 1x, 2x)

#### Full Transcript
- Expandable section showing entire command/output sequence
- Copy button for transcript
- Export as text file

#### Metadata Section
- Total events: N
- Total duration: X seconds
- Commands executed: N
- Errors encountered: N
- Final status: Pass/Fail

#### Comparison (Optional)
- Link to compare this run with another run of same task
- Side-by-side timeline view
- Highlights differences

**Data Fetched:**
```
GET /api/runs/:id                  → Run details
GET /api/replays/:runId            → Full replay trace (JSON)
```

**Visuals:**
- Vertical timeline with events
- Color-coded event badges
- Expandable event details
- Playback timeline (progress bar)
- Full transcript viewer

---

### 8. **Cost Analytics Dashboard** (Optional, can be part of `/tasks` or standalone)

**Purpose:** Track and optimize the cost of running benchmarks.

**Key Metrics:**
- Total tokens used (across all runs)
- Total API cost (if using paid APIs)
- Cost per task
- Cost per agent
- Cost efficiency (reliability score / cost)

**Charts:**
- **Line Chart:** Cost trend over time
- **Bar Chart:** Cost by agent
- **Pie Chart:** Cost distribution by task category
- **Scatter Plot:** Reliability vs Cost (bubble size = run count)

**Breakdown:**
- Cost by model (GPT-4, GPT-3.5, Ollama, etc.)
- Token usage breakdown (input vs output tokens)
- Most expensive tasks
- Most efficient agents (best score per dollar)

---

## Common UI Components

### StatsCard Component
```tsx
<StatsCard
  title="Success Rate"
  value="78.5%"
  subtitle="↑ 2.3% from last week"
  icon={CheckCircle2}
  trend="up"
/>
```

### HealthStatusBadge Component
```tsx
<HealthStatusBadge status="HEALTHY" />
// Renders: Green badge with "HEALTHY" text
```

### Charts (ECharts Integration)
All charts use Apache ECharts with common props:
- `data`: Array of data points
- `xAxis`: X-axis configuration
- `yAxis`: Y-axis configuration
- `colors`: Custom color palette
- `responsive`: Auto-resize on window resize

### Tables
All data tables support:
- Sorting (by clicking headers)
- Filtering (text search, dropdown, range)
- Pagination
- Export (CSV, JSON)
- Selection (checkboxes)
- Expandable rows

---

## API Integration

### Base URL
```
http://localhost:3001/api
```

### Key Endpoints

**Tasks:**
```
GET    /api/tasks                      # List all tasks
GET    /api/tasks/:id                  # Get task details
POST   /api/tasks                      # Create task (admin)
PUT    /api/tasks/:id                  # Update task (admin)
```

**Runs:**
```
GET    /api/runs                       # List runs (filterable)
GET    /api/runs/:id                   # Get run details
POST   /api/runs                       # Trigger new run
```

**Statistics:**
```
GET    /api/stats/tasks                # Per-task stats
GET    /api/stats/agents               # Per-agent stats
GET    /api/stats/reliability          # Reliability metrics
GET    /api/stats/costs                # Cost analytics
GET    /api/stats/failures             # Failure taxonomy
```

**Health:**
```
GET    /api/health/benchmark           # Overall health
GET    /api/health/tasks               # Health for all tasks
GET    /api/health/tasks/:id           # Health for specific task
```

**Replays:**
```
GET    /api/replays/:runId             # Get replay trace
```

**Leaderboard:**
```
GET    /api/leaderboard                # Ranked agents
GET    /api/leaderboard/compare        # Agent comparison
```

---

## Data Models

### Task
```typescript
{
  id: string;
  name: string;
  category: string;           // filesystem, data-processing, etc.
  difficulty: string;         // easy, medium, hard, expert
  description: string;
  health_status: string;      // healthy, flaky, broken, trivial, saturated
  success_rate: number;       // 0-100
  total_runs: number;
  last_run: timestamp;
  created_at: timestamp;
  updated_at: timestamp;
}
```

### Run
```typescript
{
  id: string;
  task_id: string;
  agent: string;
  status: string;             // pass, fail, timeout, partial, error
  reliability_score: number;  // 0-100
  success_rate: number;
  runtime_seconds: number;
  tokens_used: number;
  cost: number;
  created_at: timestamp;
  replay_path: string;
}
```

### Agent
```typescript
{
  name: string;
  model: string;              // gpt-4, gpt-3.5, codellama, etc.
  reliability_score: number;
  total_runs: number;
  success_rate: number;
  avg_cost: number;
  avg_tokens: number;
  consistency_score: number;
}
```

### Health Report
```typescript
{
  task_id: string;
  status: string;             // HEALTHY, FLAKY, BROKEN, TRIVIAL, SATURATED
  success_rate: number;
  variance: number;
  n_agents: number;
  evidence: string[];         // Reasons for classification
  recommendations: string[]; // Action items
  analyzed_at: timestamp;
}
```

---

## Styling & Design System

### Colors
- **Primary:** Blue (#3B82F6)
- **Success:** Green (#10B981)
- **Warning:** Yellow (#FBBF24)
- **Error:** Red (#EF4444)
- **Info:** Cyan (#06B6D4)
- **Neutral:** Gray (#6B7280)

### Typography
- **Headings:** Inter, Bold
- **Body:** Inter, Regular
- **Code:** Courier New, Monospace

### Spacing
- Base unit: 4px
- Use 4x, 8x, 12x, 16x, 20x, 24x for consistency

### Components
- All UI components from shadcn/ui
- Custom components built on top with Tailwind styling
- Dark mode support (optional)

---

## Getting Started

### Prerequisites
```bash
# Node.js 18+
node --version

# Bun
bun --version
```

### Installation

**Frontend:**
```bash
cd dashboard/web
npm install
npm run dev
# Opens http://localhost:3000
```

**Backend API:**
```bash
cd dashboard/api
bun install
bun run src/index.ts
# Runs on http://localhost:3001
```

**Database:**
```bash
# Start PostgreSQL (Docker)
docker run -d \
  --name agentbench-db \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16
```

### Environment Variables

**Frontend (`dashboard/web/.env.local`):**
```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_APP_NAME=AgentBench
NEXT_PUBLIC_THEME=light
```

**Backend (`dashboard/api/.env`):**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/agentbench
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000
```

---

## Testing

### Frontend Tests
```bash
cd dashboard/web
npm run test              # Run all tests
npm run test:watch       # Watch mode
npm run test:coverage    # Coverage report
```

### Backend Tests
```bash
cd dashboard/api
bun test                  # Run all tests
```

---

## Deployment

### Production Build

**Frontend:**
```bash
cd dashboard/web
npm run build
npm run start
```

**Backend:**
```bash
cd dashboard/api
bun run src/index.ts --production
```

### Docker Deployment
```bash
docker-compose up -d
```

---

## Performance Optimization

- **Image Optimization:** Next.js Image component for lazy loading
- **Code Splitting:** Automatic with Next.js
- **Caching:** API responses cached with SWR or React Query
- **Database:** Indexes on frequently queried fields
- **Pagination:** Server-side pagination for large datasets
- **Chart Optimization:** Virtual scrolling for large datasets

---

## Accessibility

- WCAG 2.1 AA compliance target
- Keyboard navigation support
- Screen reader friendly labels
- Color contrast ratios ≥ 4.5:1
- Focus indicators on all interactive elements

---

## Future Enhancements

1. **Real-time Updates:** WebSocket integration for live run updates
2. **Custom Dashboards:** User-configurable dashboard layouts
3. **Alerts & Notifications:** Email alerts for benchmark failures
4. **Advanced Analytics:** ML-based anomaly detection
5. **User Authentication:** Role-based access control (admin, viewer, etc.)
6. **Scheduled Reports:** Automated weekly/monthly benchmark reports
7. **Integration:** Slack, GitHub, or Jira integration for alerts
8. **Dark Mode:** Full dark mode support
9. **Mobile Responsive:** Optimize for mobile/tablet viewing
10. **Batch Operations:** Bulk re-run tasks, bulk configuration updates

---

## Troubleshooting

### API Connection Issues
- Verify backend is running on port 3001
- Check `NEXT_PUBLIC_API_URL` in frontend env
- Check CORS configuration in backend

### Database Errors
- Ensure PostgreSQL is running
- Verify `DATABASE_URL` is correct
- Run migrations: `bun run migrate`

### Chart Display Issues
- Clear browser cache
- Check console for ECharts errors
- Verify data format matches chart expectations

---

## Contributing

When adding new pages or features:

1. Create feature branch: `git checkout -b feature/dashboard-feature-name`
2. Build components in `components/` directory
3. Add page routes in `app/` directory
4. Update API client in `lib/api-client.ts`
5. Add tests in `__tests__/` directories
6. Update this README with feature details
7. Submit PR with description

---

## Support

For issues or questions:
- Check existing GitHub issues
- Review documentation in `/docs`
- Examine test files for usage examples
- Refer to shadcn/ui and ECharts documentation

---

## License

MIT

---

**Last Updated:** July 5, 2026  
**Version:** 1.0.0 (Week 5 - Dashboard Phase)  
**Status:** In Development
