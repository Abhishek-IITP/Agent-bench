# AgentBench User Guide

**Welcome to AgentBench!** This guide will help you test your AI model against our benchmark tasks.

## 🚀 Quick Start (5 Minutes)

### Option 1: Use the Web Interface (Easiest)

1. **Open your browser** and navigate to: **http://localhost:3002**
2. **Click "Test Model"** in the sidebar
3. **Fill in the form**:
   - Select your model provider (OpenAI, Anthropic, Local, or Custom)
   - Enter your model name (e.g., `gpt-4`, `claude-3-opus`)
   - Optionally add your API key
   - Choose a benchmark task
   - Click "Run Benchmark"
4. **View results** instantly!

### Option 2: Use the Command Line

```bash
# Run a single benchmark
agentbench bench find-database-files --agent openai --model gpt-4

# Run multiple benchmarks for reliability testing
agentbench bench find-database-files --agent openai --model gpt-4 --runs 10

# View all available tasks
agentbench tasks list

# Check benchmark health
agentbench health
```

---

## 📋 Available Benchmark Tasks

| Task ID | Name | Difficulty | Category | Description |
|---------|------|------------|----------|-------------|
| `find-database-files` | Find Database Files | Easy | Filesystem | Find files containing database keywords |
| `extract-emails` | Extract Email Addresses | Easy | Data Processing | Extract and list all email addresses |
| `sort-json-by-field` | Sort JSON by Field | Easy | Data Processing | Sort JSON objects by a specific field |
| `count-error-lines` | Count Error Lines | Easy | Data Processing | Count lines containing errors in logs |
| `filter-logs-by-date` | Filter Logs by Date | Medium | Data Processing | Filter log entries by date range |
| `calculate-statistics` | Calculate Statistics | Medium | Data Processing | Calculate statistical metrics |
| `debug-python-error` | Debug Python Error | Medium | Debugging | Find and fix a bug in Python code |
| `parse-config-values` | Parse Config Values | Medium | Data Processing | Parse configuration files |
| `find-largest-file` | Find Largest File | Easy | Filesystem | Identify the largest file in directory |
| `merge-csv-files` | Merge CSV Files | Medium | Data Processing | Merge multiple CSV files |
| `optimize-query` | Optimize Query | Hard | Debugging | Optimize a database query |
| `find-security-issues` | Find Security Issues | Hard | Security | Identify security vulnerabilities |
| `fix-broken-script` | Fix Broken Script | Medium | Debugging | Fix a non-working shell script |
| `transform-data-format` | Transform Data Format | Medium | Data Processing | Convert data between formats |

---

## 🔧 Supported Model Providers

### OpenAI Models
```bash
agentbench bench <task-id> --agent openai --model gpt-4
agentbench bench <task-id> --agent openai --model gpt-3.5-turbo
```

**Required**: Set `OPENAI_API_KEY` in `.env` file or pass via `--api-key` flag

### Anthropic Models
```bash
agentbench bench <task-id> --agent anthropic --model claude-3-opus-20240229
agentbench bench <task-id> --agent anthropic --model claude-3-sonnet-20240229
```

**Required**: Set `ANTHROPIC_API_KEY` in `.env` file

### Local Models (Ollama)
```bash
agentbench bench <task-id> --agent ollama --model llama2
agentbench bench <task-id> --agent ollama --model mistral
```

**Required**: Ollama must be running locally (`ollama serve`)

### Custom API
```bash
agentbench bench <task-id> --agent custom --model your-model --api-url http://your-api.com
```

---

## 📊 Understanding Results

After running a benchmark, you'll receive:

### Success/Failure
- ✅ **Passed**: Your model completed the task correctly
- ❌ **Failed**: Your model did not meet the requirements

### Metrics Explained

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Score** | Percentage of tests passed | > 90% |
| **Duration** | Time taken to complete (seconds) | < 120s |
| **Tokens Used** | Number of tokens consumed | Varies by task |
| **Cost** | Estimated API cost ($) | Lower is better |
| **Tests Passed** | Number of test cases passed | All tests |

### Reliability Score
When running multiple times (`--runs > 1`):
- **Consistency**: How often your model succeeds
- **Variance**: How stable the performance is
- **Confidence Interval**: Statistical confidence in results

---

## 🎯 Best Practices

### 1. Start with Easy Tasks
Begin with easy tasks to understand the system:
```bash
agentbench bench find-database-files --agent openai --model gpt-4
```

### 2. Run Multiple Times for Reliability
Single runs can be misleading. Run 5-10 times:
```bash
agentbench bench find-database-files --agent openai --model gpt-4 --runs 10
```

### 3. Compare Different Models
Test multiple models on the same task:
```bash
agentbench bench find-database-files --agent openai --model gpt-4
agentbench bench find-database-files --agent openai --model gpt-3.5-turbo
agentbench bench find-database-files --agent anthropic --model claude-3-opus
```

### 4. Use the Dashboard
View all results in a visual interface:
- Go to http://localhost:3002
- Check the Leaderboard to see how your model ranks
- View detailed run history and metrics

### 5. Check Task Health
Before testing, check if a task is stable:
```bash
agentbench health --task find-database-files
```

---

## 🔍 Troubleshooting

### "Connection refused" error
**Problem**: Database or API not running

**Solution**:
```bash
# Check if database is running
docker ps | findstr agentbench-db

# Start database if not running
docker-compose up -d postgres

# Check if API is running (should see port 3001)
```

### "API key not found" error
**Problem**: No API key configured

**Solution**:
1. Copy `.env.example` to `.env`
2. Add your API keys:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### "Task not found" error
**Problem**: Invalid task ID

**Solution**:
```bash
# List all available tasks
agentbench tasks list
```

### Model times out
**Problem**: Task took too long

**Solution**:
- Try an easier task first
- Increase timeout: `--timeout 900`
- Check if your API is responding

### Results not showing in dashboard
**Problem**: Database connection issue

**Solution**:
1. Check database is running: `docker ps`
2. Test connection: `docker exec agentbench-db psql -U postgres -d agentbench -c "SELECT 1"`
3. Restart API server

---

## 📈 Interpreting the Leaderboard

The leaderboard ranks models by:

1. **Reliability Score** (0-100)
   - Combines success rate + consistency
   - Higher is better

2. **Tasks Solved**
   - Number of unique tasks completed successfully
   - More is better

3. **Average Cost**
   - Average cost per successful run
   - Lower is better

4. **Success Rate**
   - Percentage of all runs that passed
   - Higher is better

---

## 🚀 Advanced Usage

### Batch Testing
Test your model on all tasks:
```bash
for task in find-database-files extract-emails sort-json-by-field; do
  agentbench bench $task --agent openai --model gpt-4 --runs 5
done
```

### Custom Configuration
Create a config file `my-agent.json`:
```json
{
  "name": "my-custom-agent",
  "type": "custom",
  "model": "my-model-v1",
  "config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

Run with config:
```bash
agentbench bench find-database-files --config my-agent.json
```

### Export Results
Export results to CSV:
```bash
agentbench export --format csv --output results.csv
```

### Compare Agents
Generate comparison report:
```bash
agentbench compare --agents "gpt-4,claude-3-opus,llama2" --task find-database-files
```

---

## 💡 Tips for Success

1. **Warm up your model**: Run a simple task first before complex ones
2. **Check task instructions**: Each task has specific requirements
3. **Monitor costs**: Use `--dry-run` flag to estimate costs
4. **Use verbose mode**: Add `--verbose` to see detailed execution logs
5. **Save replays**: Use `--save-replay` to review agent's actions later

---

## 🆘 Getting Help

### Documentation
- **Main README**: `/README.md`
- **API Docs**: `/dashboard/api/src/README.md`
- **Task Specifications**: `/tasks/<task-id>/README.md`

### Commands
```bash
# Get help on any command
agentbench --help
agentbench bench --help
agentbench health --help

# Check system status
agentbench status

# Verify installation
agentbench doctor
```

### Contact & Support
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Email**: support@agentbench.dev

---

## 🎉 Example Workflow

Here's a complete example workflow:

```bash
# 1. Check system is ready
docker ps | findstr agentbench-db

# 2. List available tasks
agentbench tasks list

# 3. Run your first benchmark
agentbench bench find-database-files --agent openai --model gpt-4

# 4. Check the results
agentbench runs list --limit 1

# 5. Run reliability test (10 runs)
agentbench bench find-database-files --agent openai --model gpt-4 --runs 10

# 6. View leaderboard
agentbench leaderboard

# 7. Open dashboard
# Visit http://localhost:3002 in your browser
```

---

## 📱 Dashboard Overview

### Main Pages

**1. Overview (`/`)**
- Real-time reliability score
- Recent activity timeline
- Task health map
- Top performing agents

**2. Test Model (`/test`)**
- **START HERE** to test your model
- User-friendly web form
- Instant results display

**3. Tasks (`/tasks`)**
- Browse all available tasks
- View task details and requirements
- See success rates and statistics

**4. Runs (`/runs`)**
- History of all benchmark runs
- Filter by task, agent, success/failure
- View detailed execution logs

**5. Leaderboard (`/leaderboard`)**
- Compare all models
- See rankings and scores
- View agent performance metrics

**6. Health (`/health`)**
- Monitor benchmark health
- Identify flaky or broken tasks
- View recommendations

---

## ✅ Checklist Before Testing

- [ ] Database is running (`docker ps`)
- [ ] API server is running (port 3001)
- [ ] Dashboard is accessible (http://localhost:3002)
- [ ] API keys are configured (`.env` file)
- [ ] Task exists (`agentbench tasks list`)
- [ ] Docker is installed and running
- [ ] Sufficient disk space (>2GB)
- [ ] Internet connection (for API calls)

---

## 🎓 Learning Path

### Beginner
1. Run a single easy task via web interface
2. View results in dashboard
3. Try 2-3 different easy tasks
4. Compare with leaderboard

### Intermediate
1. Use command line interface
2. Run reliability tests (10 runs)
3. Test multiple models
4. Analyze task health

### Advanced
1. Create custom agents
2. Add new benchmark tasks
3. Export and analyze data
4. Integrate with CI/CD

---

**Ready to start? Go to http://localhost:3002/test and run your first benchmark!** 🚀

