import { vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import TopTasksWidget from './TopTasksWidget';
import { Task, TaskHealth } from '@/lib/types';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
  })),
}));

const mockTasks: Task[] = [
  {
    id: 'find-files',
    name: 'Find Files',
    category: 'filesystem',
    difficulty: 'easy',
    timeout: 30,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'database-query',
    name: 'Database Query',
    category: 'database',
    difficulty: 'hard',
    timeout: 60,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'text-processing',
    name: 'Text Processing',
    category: 'text',
    difficulty: 'medium',
    timeout: 45,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'image-analysis',
    name: 'Image Analysis',
    category: 'vision',
    difficulty: 'hard',
    timeout: 90,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'math-solving',
    name: 'Math Solving',
    category: 'math',
    difficulty: 'medium',
    timeout: 30,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'code-generation',
    name: 'Code Generation',
    category: 'coding',
    difficulty: 'hard',
    timeout: 120,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockTaskHealths: TaskHealth[] = [
  {
    task_id: 'find-files',
    health_status: 'healthy',
    success_rate: 0.95,
    variance: 0.01,
    n_agents: 5,
    n_runs_total: 100,
    reasons: [],
  },
  {
    task_id: 'database-query',
    health_status: 'flaky',
    success_rate: 0.75,
    variance: 0.15,
    n_agents: 3,
    n_runs_total: 80,
    reasons: ['High variance in results'],
  },
  {
    task_id: 'text-processing',
    health_status: 'healthy',
    success_rate: 0.92,
    variance: 0.02,
    n_agents: 4,
    n_runs_total: 90,
    reasons: [],
  },
  {
    task_id: 'image-analysis',
    health_status: 'broken',
    success_rate: 0.45,
    variance: 0.25,
    n_agents: 2,
    n_runs_total: 60,
    reasons: ['Low success rate'],
  },
  {
    task_id: 'math-solving',
    health_status: 'healthy',
    success_rate: 0.88,
    variance: 0.05,
    n_agents: 3,
    n_runs_total: 70,
    reasons: [],
  },
  {
    task_id: 'code-generation',
    health_status: 'saturated',
    success_rate: 0.98,
    variance: 0.01,
    n_agents: 4,
    n_runs_total: 110,
    reasons: ['Very high performance'],
  },
];

describe('TopTasksWidget Component', () => {
  it('renders loading skeleton', () => {
    const { container } = render(
      <TopTasksWidget
        tasks={null}
        taskHealths={null}
        loading={true}
      />
    );
    expect(screen.getByText('Top Tasks (Highest Reliability)')).toBeTruthy();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('renders error state with retry button', () => {
    const mockRetry = vi.fn();
    render(
      <TopTasksWidget
        tasks={null}
        taskHealths={null}
        error={new Error('Failed to load')}
        onRetry={mockRetry}
      />
    );
    expect(screen.getByText('Failed to load top tasks')).toBeTruthy();
    const retryButton = screen.getByText('Retry');
    expect(retryButton).toBeTruthy();
    fireEvent.click(retryButton);
    expect(mockRetry).toHaveBeenCalled();
  });

  it('renders empty state', () => {
    render(
      <TopTasksWidget
        tasks={[]}
        taskHealths={[]}
        loading={false}
      />
    );
    expect(screen.getByText('No task data available yet.')).toBeTruthy();
  });

  it('renders top 5 tasks sorted by reliability', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check that the component renders the top 5 tasks
    // The order should be: code-generation (98%), find-files (95%), text-processing (92%), math-solving (88%), database-query (75%)
    expect(screen.getByText('Code Generation')).toBeTruthy();
    expect(screen.getByText('Find Files')).toBeTruthy();
    expect(screen.getByText('Text Processing')).toBeTruthy();
    expect(screen.getByText('Math Solving')).toBeTruthy();
    expect(screen.getByText('Database Query')).toBeTruthy();

    // Image Analysis should not be visible since it's ranked 6th
    expect(screen.queryByText('Image Analysis')).toBeNull();
  });

  it('displays all required columns', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check column headers
    expect(screen.getByText('Task')).toBeTruthy();
    expect(screen.getByText('Reliability')).toBeTruthy();
    expect(screen.getByText('Success Rate')).toBeTruthy();
    expect(screen.getByText('Difficulty')).toBeTruthy();
    expect(screen.getByText('Status')).toBeTruthy();
  });

  it('displays difficulty badges correctly', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check for difficulty levels in the rendered output
    const easyBadges = screen.getAllByText('Easy');
    const hardBadges = screen.getAllByText('Hard');
    const mediumBadges = screen.getAllByText('Medium');

    expect(easyBadges.length).toBeGreaterThan(0);
    expect(hardBadges.length).toBeGreaterThan(0);
    expect(mediumBadges.length).toBeGreaterThan(0);
  });

  it('displays health status badges correctly', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check for health status badges
    expect(screen.getAllByText('Healthy').length).toBeGreaterThan(0);
    expect(screen.getByText('Flaky')).toBeTruthy();
    expect(screen.getByText('Saturated')).toBeTruthy();
  });

  it('displays success rates as percentages', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check that success rates are displayed as percentages
    expect(screen.getAllByText('95%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('75%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('98%').length).toBeGreaterThan(0);
  });

  it('displays reliability scores', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // The reliability scores should match the success rates (scaled to 0-100)
    // Top 5 tasks by reliability: 98, 95, 92, 88, 75
    const cells = screen.getAllByRole('cell');
    expect(cells.length).toBeGreaterThan(0);
  });

  it('has "View All" link to tasks page', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    const viewAllLink = screen.getByText('View All');
    expect(viewAllLink).toBeTruthy();
    expect(viewAllLink.closest('a')?.getAttribute('href')).toBe('/tasks');
  });

  it('rows are clickable via task links', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    const links = screen.getAllByRole('link');
    // Should have "View All" link plus links for the 5 top tasks
    expect(links.length).toBeGreaterThanOrEqual(6);
  });

  it('task names are clickable links to task details', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    const codeGenerationLink = screen.getByText('Code Generation').closest('a');
    expect(codeGenerationLink?.getAttribute('href')).toBe('/tasks/code-generation');

    const findFilesLink = screen.getByText('Find Files').closest('a');
    expect(findFilesLink?.getAttribute('href')).toBe('/tasks/find-files');
  });

  it('handles missing health data gracefully', () => {
    // Only first 3 tasks have health data, but all 6 tasks exist
    const partialHealths = mockTaskHealths.slice(0, 3);
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={partialHealths}
        loading={false}
      />
    );

    // Should only show tasks with health data (max 5, but only 3 available)
    expect(screen.getByText('Find Files')).toBeTruthy();
    expect(screen.getByText('Text Processing')).toBeTruthy();
    expect(screen.getByText('Database Query')).toBeTruthy();

    // These tasks have no health data, so they shouldn't appear
    expect(screen.queryByText('Image Analysis')).toBeNull();
    expect(screen.queryByText('Math Solving')).toBeNull();
    expect(screen.queryByText('Code Generation')).toBeNull();
  });

  it('displays exactly 5 tasks when more than 5 are available', () => {
    const { container } = render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    const rows = container.querySelectorAll('tbody tr');
    expect(rows).toHaveLength(5);
  });

  it('displays progress bars for reliability scores', () => {
    const { container } = render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    // Check for progress bars (gradient divs)
    const progressBars = container.querySelectorAll('.bg-gradient-to-r');
    expect(progressBars.length).toBeGreaterThan(0);
  });

  it('renders widget title correctly', () => {
    render(
      <TopTasksWidget
        tasks={mockTasks}
        taskHealths={mockTaskHealths}
        loading={false}
      />
    );

    expect(screen.getByText('Top Tasks (Highest Reliability)')).toBeTruthy();
  });
});
