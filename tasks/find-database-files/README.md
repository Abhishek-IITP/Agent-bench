# Task: Find Database Files

## Overview

This is a complete, production-ready benchmark task. It tests whether an AI agent can:
1. Search for files containing specific text
2. Process multiple files
3. Generate output in the correct format
4. Sort results alphabetically

## Task Structure

```
find-database-files/
├── task.toml              # Task metadata & configuration
├── instruction.md         # Visible instructions for the agent
├── environment/           # Test data & files
│   ├── app_log.txt       # Application log (contains "database")
│   ├── config.json       # Configuration file (contains "database")
│   ├── deployment_notes.md  # Documentation (contains "database")
│   ├── README.md         # README file (NO "database")
│   └── notes.txt         # Notes file (NO "database")
├── solution/             # Reference solution
│   └── solve.py         # Reference implementation
└── tests/               # Evaluation tests
    └── test_output.py   # Test harness (checks if output is correct)
```

## Files Explained

### `task.toml` — Task Metadata

```toml
id = "find-database-files"
name = "Find Database Files"
version = "1.0.0"
category = "filesystem"
difficulty = "easy"
timeout = 60
description = "Search for files containing the word 'database'..."
```

**What this does:** Tells the system about this task:
- `id` — Unique identifier (kebab-case)
- `name` — Human-readable name
- `version` — Task version (for tracking changes)
- `difficulty` — How hard is this task? (easy/medium/hard/expert)
- `timeout` — How long to wait before killing the task (60 seconds)
- `expected_output_files` — What files should the agent create?

### `instruction.md` — What Agent Sees

This is what the AI agent reads. It gives clear instructions without hints or solutions.

```markdown
# Task
Search all files under: /workspace/data
Find every file containing the word: database
Write matching filenames to: /workspace/output.txt

Requirements:
- One filename per line
- Sort filenames alphabetically
- Do not include directory paths
```

### `environment/` — Test Data

Contains 5 files:
- **3 files WITH "database":**
  - `app_log.txt` — Contains "database" multiple times
  - `config.json` — Contains "database" in JSON keys
  - `deployment_notes.md` — Contains "database" in content

- **2 files WITHOUT "database":**
  - `README.md` — Documentation (no "database")
  - `notes.txt` — Random notes (no "database")

**Purpose:** Provides real test data that the agent must search through.

### `solution/solve.py` — Reference Implementation

A correct solution that:
1. Reads all files from `/workspace/data`
2. Searches for "database" (case-insensitive)
3. Collects matching filenames
4. Sorts them alphabetically
5. Writes to `/workspace/output.txt` (one per line, no paths)

**Purpose:**
- Shows what the expected behavior is
- Used for "Oracle validation" (confirm correct solution passes)

### `tests/test_output.py` — Evaluation Tests

Contains 5 tests that check:
1. ✅ `output.txt` was created
2. ✅ `output.txt` is not empty
3. ✅ Format is correct (filenames only, one per line)
4. ✅ Files are sorted alphabetically
5. ✅ Correct files were found (3 files with "database", not the other 2)

**Purpose:** Automatically scores the agent's output.

---

## Expected Output

When solved correctly, `/workspace/output.txt` should contain:

```
app_log.txt
config.json
deployment_notes.md
```

- ✅ Exactly 3 files (those containing "database")
- ✅ Sorted alphabetically
- ✅ No directory paths
- ✅ One per line

---

## How This Task Works (Week 2+)

### When You Have the Runner Ready (Week 2):

```
1. Runner loads task config from task.toml
2. Runner creates a Docker container
3. Runner copies environment/ into container
4. Runner gives agent the instruction.md
5. Agent searches for files with "database"
6. Agent creates /workspace/output.txt
7. Runner executes tests/test_output.py to evaluate
8. Tests pass = Agent solved it correctly
```

### For Benchmarking (Week 4):

```
Run the task 10 times:
- Run 1: Agent finds correct files ✅
- Run 2: Agent finds correct files ✅
- Run 3: Agent finds correct files ✅
- ... (10 times total)

Calculate metrics:
- Success rate: 10/10 = 100%
- Reliability: Very high (all runs consistent)
- Status: HEALTHY
```

---

## Key Takeaways

### This Task is "Production-Ready" Because:

✅ **Complete** — All required components present
✅ **Clear** — Instructions unambiguous
✅ **Testable** — Evaluation is automated
✅ **Reliable** — Same input always produces same answer
✅ **Fair** — Doesn't trick or mislead agents
✅ **Diverse** — Mix of matching and non-matching files

### What Makes a Good Benchmark Task:

1. **Clear objective** — Agent knows exactly what to do
2. **Real-world relevance** — Resembles actual work
3. **Automated evaluation** — No manual judgment
4. **Reproducibility** — Same results on every run
5. **Reasonable difficulty** — Not too easy, not too hard
6. **Diverse test cases** — Mix of scenarios

This task demonstrates all of these.

---

## Next Steps

Once Week 2 is complete (runner + Docker):
1. This task can be used for benchmarking
2. AI agents can solve it
3. Results can be measured
4. Success rate and reliability tracked

On Week 2, we'll create more tasks using this as a template.

---

*This is a professional benchmark task. Well done!* 🎉
