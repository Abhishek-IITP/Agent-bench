# AgentBench

AgentBench is a reliability-focused AI agent benchmark.

The benchmark evaluates AI agents inside isolated Linux environments and measures:

- Task Success
- Reliability
- Reproducibility
- Cost Efficiency
- Benchmark Health

Future Features:

- Multi-run evaluation
- Replay traces
- Difficulty calibration
- Cost metrics
- Leaderboards

## architecture

Task
 ↓
Docker Environment
 ↓
Agent
 ↓
Filesystem Outputs
 ↓
Test Harness
 ↓
Metrics