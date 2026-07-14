-- AgentBench PostgreSQL schema

-- Tasks table: metadata about benchmark tasks
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    description TEXT,
    timeout INTEGER DEFAULT 300,
    docker_image VARCHAR(255) DEFAULT 'ubuntu:22.04',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agents table: available agents and their configurations
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    model VARCHAR(255) NOT NULL,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Runs table: execution records
CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL REFERENCES tasks(id),
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration FLOAT,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Results table: test evaluation results
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    passed BOOLEAN NOT NULL,
    score FLOAT DEFAULT 0.0,
    test_output TEXT,
    test_details JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

-- Replays table: execution traces for replay analysis
CREATE TABLE IF NOT EXISTS replays (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

-- Execution metrics table: detailed performance data
CREATE TABLE IF NOT EXISTS execution_metrics (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES runs(id),
    commands_executed INTEGER DEFAULT 0,
    files_created INTEGER DEFAULT 0,
    files_modified INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    cost FLOAT DEFAULT 0.0,
    memory_peak_mb FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

-- Multi-run metrics table: aggregated statistics from multi-run execution
CREATE TABLE IF NOT EXISTS multi_run_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) NOT NULL REFERENCES tasks(id),
    agent_name VARCHAR(255) NOT NULL,
    n_runs INTEGER NOT NULL,
    success_rate FLOAT NOT NULL,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,
    variance FLOAT,
    mean_runtime FLOAT,
    mean_tokens INTEGER DEFAULT 0,
    mean_cost FLOAT DEFAULT 0.0,
    reliability_score FLOAT,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    UNIQUE(task_id, agent_name)
);

-- Task health table: health classifications and analysis
CREATE TABLE IF NOT EXISTS task_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) NOT NULL UNIQUE REFERENCES tasks(id),
    health_status VARCHAR(50) NOT NULL,
    success_rate FLOAT NOT NULL,
    variance FLOAT NOT NULL,
    n_agents INTEGER DEFAULT 0,
    n_runs_total INTEGER DEFAULT 0,
    evidence TEXT,
    recommendations TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Task difficulty calibration table: difficulty estimation and comparison
CREATE TABLE IF NOT EXISTS task_difficulty_calibration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) NOT NULL UNIQUE REFERENCES tasks(id),
    author_difficulty VARCHAR(50),
    empirical_difficulty VARCHAR(50) NOT NULL,
    mean_success_rate FLOAT NOT NULL,
    median_success_rate FLOAT,
    n_agents INTEGER DEFAULT 0,
    match BOOLEAN DEFAULT FALSE,
    recommendation TEXT,
    confidence FLOAT DEFAULT 0.5,
    calibrated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_runs_task_id ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_agent_id ON runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_results_run_id ON results(run_id);
CREATE INDEX IF NOT EXISTS idx_replays_run_id ON replays(run_id);
CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON execution_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_multi_run_metrics_task ON multi_run_metrics(task_id);
CREATE INDEX IF NOT EXISTS idx_multi_run_metrics_agent ON multi_run_metrics(agent_name);
CREATE INDEX IF NOT EXISTS idx_task_health_status ON task_health(health_status);
CREATE INDEX IF NOT EXISTS idx_task_difficulty_match ON task_difficulty_calibration(match);
