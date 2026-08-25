-- Seed database with sample data

-- Insert sample tasks
INSERT INTO tasks (id, name, category, difficulty, version, timeout, docker_image, description)
VALUES
('find-database-files', 'Find Database Files', 'filesystem', 'easy', '1.0.0', 300, 'ubuntu:22.04', 'Find files containing specific database-related keywords'),
('extract-emails', 'Extract Email Addresses', 'data-processing', 'easy', '1.0.0', 300, 'ubuntu:22.04', 'Extract and list all email addresses from text files'),
('sort-json-by-field', 'Sort JSON by Field', 'data-processing', 'easy', '1.0.0', 300, 'node:20', 'Sort JSON objects by a specific field'),
('calculate-statistics', 'Calculate Statistics', 'data-processing', 'medium', '1.0.0', 450, 'python:3.11', 'Calculate statistical metrics from dataset'),
('debug-python-error', 'Debug Python Error', 'debugging', 'medium', '1.0.0', 450, 'python:3.11', 'Find and fix a bug in Python code')
ON CONFLICT (id) DO NOTHING;

-- Insert sample agents
INSERT INTO agents (name, type, model, config)
VALUES
('gpt-4', 'openai', 'gpt-4', '{"temperature": 0.7}'),
('gpt-3.5-turbo', 'openai', 'gpt-3.5-turbo', '{"temperature": 0.7}'),
('claude-3-opus', 'anthropic', 'claude-3-opus-20240229', '{}'),
('claude-3-sonnet', 'anthropic', 'claude-3-sonnet-20240229', '{}')
ON CONFLICT (name) DO NOTHING;

-- Insert sample runs
INSERT INTO runs (id, task_id, agent_id, started_at, ended_at, duration, success)
VALUES
('550e8400-e29b-41d4-a716-446655440001', 'find-database-files', 1, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '45 seconds', 45, true),
('550e8400-e29b-41d4-a716-446655440002', 'find-database-files', 1, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '42 seconds', 42, true),
('550e8400-e29b-41d4-a716-446655440003', 'extract-emails', 2, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '60 seconds', 60, true),
('550e8400-e29b-41d4-a716-446655440004', 'extract-emails', 2, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '55 seconds', 55, false),
('550e8400-e29b-41d4-a716-446655440005', 'sort-json-by-field', 3, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '50 seconds', 50, true),
('550e8400-e29b-41d4-a716-446655440006', 'calculate-statistics', 3, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '180 seconds', 180, true),
('550e8400-e29b-41d4-a716-446655440007', 'debug-python-error', 4, NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours' + INTERVAL '240 seconds', 240, false),
('550e8400-e29b-41d4-a716-446655440008', 'find-database-files', 4, NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours' + INTERVAL '38 seconds', 38, true)
ON CONFLICT (id) DO NOTHING;

-- Insert sample results
INSERT INTO results (run_id, passed, score, test_output, test_details)
VALUES
('550e8400-e29b-41d4-a716-446655440001', true, 1.0, 'All tests passed', '{"tests_run": 5, "tests_passed": 5}'),
('550e8400-e29b-41d4-a716-446655440002', true, 1.0, 'All tests passed', '{"tests_run": 5, "tests_passed": 5}'),
('550e8400-e29b-41d4-a716-446655440003', true, 0.95, 'All tests passed', '{"tests_run": 8, "tests_passed": 8}'),
('550e8400-e29b-41d4-a716-446655440004', false, 0.3, 'Test failed', '{"tests_run": 8, "tests_passed": 2}'),
('550e8400-e29b-41d4-a716-446655440005', true, 1.0, 'All tests passed', '{"tests_run": 6, "tests_passed": 6}'),
('550e8400-e29b-41d4-a716-446655440006', true, 0.92, 'All tests passed', '{"tests_run": 10, "tests_passed": 10}'),
('550e8400-e29b-41d4-a716-446655440007', false, 0.25, 'Test failed', '{"tests_run": 12, "tests_passed": 3}'),
('550e8400-e29b-41d4-a716-446655440008', true, 1.0, 'All tests passed', '{"tests_run": 5, "tests_passed": 5}')
ON CONFLICT (id) DO NOTHING;

-- Insert sample execution metrics
INSERT INTO execution_metrics (run_id, commands_executed, files_created, files_modified, tokens_used, cost)
VALUES
('550e8400-e29b-41d4-a716-446655440001', 8, 1, 2, 1500, 0.045),
('550e8400-e29b-41d4-a716-446655440002', 7, 1, 2, 1400, 0.042),
('550e8400-e29b-41d4-a716-446655440003', 12, 2, 3, 1800, 0.036),
('550e8400-e29b-41d4-a716-446655440004', 10, 1, 2, 1600, 0.032),
('550e8400-e29b-41d4-a716-446655440005', 15, 1, 4, 2500, 0.075),
('550e8400-e29b-41d4-a716-446655440006', 20, 2, 5, 3000, 0.090),
('550e8400-e29b-41d4-a716-446655440007', 18, 1, 3, 2800, 0.084),
('550e8400-e29b-41d4-a716-446655440008', 9, 1, 2, 1600, 0.048)
ON CONFLICT (id) DO NOTHING;

-- Insert task health data
INSERT INTO task_health (task_id, health_status, success_rate, variance, n_agents, n_runs_total, recommendations)
VALUES
('find-database-files', 'healthy', 0.95, 0.02, 2, 3, 'Task is performing excellently'),
('extract-emails', 'flaky', 0.50, 0.25, 1, 2, 'Task shows inconsistent results'),
('sort-json-by-field', 'healthy', 1.0, 0.0, 1, 1, 'Task is stable'),
('calculate-statistics', 'healthy', 1.0, 0.0, 1, 1, 'Task is performing well'),
('debug-python-error', 'broken', 0.0, 0.0, 1, 1, 'Task needs review')
ON CONFLICT (task_id) DO UPDATE SET
    health_status = EXCLUDED.health_status,
    success_rate = EXCLUDED.success_rate,
    variance = EXCLUDED.variance,
    n_agents = EXCLUDED.n_agents,
    n_runs_total = EXCLUDED.n_runs_total,
    recommendations = EXCLUDED.recommendations;
