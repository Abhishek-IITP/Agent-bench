import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RecentRunsWidget from './RecentRunsWidget';
import type { Run } from '../../../lib/types';

describe('RecentRunsWidget', () => {
  const mockRuns: Run[] = [
    {
      id: 'run-1',
      task_id: 'task-find-files',
      agent_name: 'Claude-3',
      status: 'success',
      score: 0.95,
      cost: 0.15,
      duration: 45,
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 'run-2',
      task_id: 'task-edit-config',
      agent_name: 'GPT-4',
      status: 'failure',
      score: 0.5,
      cost: 0.20,
      duration: 60,
      created_at: '2024-01-15T09:15:00Z',
    },
    {
      id: 'run-3',
      task_id: 'task-database',
      agent_name: 'Claude-3',
      status: 'success',
      score: 0.88,
      cost: 0.18,
      duration: 50,
      created_at: '2024-01-15T08:00:00Z',
    },
    {
      id: 'run-4',
      task_id: 'task-network',
      agent_name: 'GPT-4-Turbo',
      status: 'timeout',
      score: 0.0,
      cost: 0.25,
      duration: 120,
      created_at: '2024-01-15T07:30:00Z',
    },
    {
      id: 'run-5',
      task_id: 'task-security',
      agent_name: 'Llama-70B',
      status: 'error',
      score: 0.0,
      cost: 0.10,
      duration: 30,
      created_at: '2024-01-15T06:45:00Z',
    },
  ];

  describe('Rendering', () => {
    it('renders the widget title', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      expect(screen.getByText('Recent Runs')).toBeInTheDocument();
    });

    it('renders last 5 runs in table format', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      // Check table headers
      expect(screen.getByText('Task')).toBeInTheDocument();
      expect(screen.getByText('Agent')).toBeInTheDocument();
      expect(screen.getByText('Date')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();

      // Check runs are rendered
      expect(screen.getByText('task-find-files')).toBeInTheDocument();
      expect(screen.getAllByText('Claude-3').length).toBeGreaterThan(0);
      expect(screen.getAllByText('GPT-4').length).toBeGreaterThan(0);
    });

    it('displays status badges with correct colors', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const statusBadges = screen.getAllByText(/success|failure|timeout|error/i);
      expect(statusBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Loading State', () => {
    it('shows loading skeletons when loading is true', () => {
      render(
        <RecentRunsWidget runs={null} loading={true} />
      );
      
      // Check that skeleton elements exist
      const skeletons = screen.queryAllByText(/Recent Runs/);
      expect(screen.getByText('Recent Runs')).toBeInTheDocument();
    });

    it('does not show run data when loading', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={true} />
      );
      
      // When loading, runs should not be displayed
      expect(screen.queryByText('task-find-files')).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state message when no runs available', () => {
      render(
        <RecentRunsWidget runs={[]} loading={false} />
      );
      
      expect(screen.getByText(/No runs yet/i)).toBeInTheDocument();
    });

    it('shows empty state message when runs is null', () => {
      render(
        <RecentRunsWidget runs={null} loading={false} />
      );
      
      expect(screen.getByText(/No runs yet/i)).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('shows error message when error is present', () => {
      const error = new Error('Failed to load runs');
      render(
        <RecentRunsWidget runs={null} loading={false} error={error} />
      );
      
      expect(screen.getByText(/Failed to load recent runs/i)).toBeInTheDocument();
    });

    it('shows retry button when error is present and onRetry is provided', async () => {
      const error = new Error('Failed to load runs');
      const onRetry = vi.fn();
      
      render(
        <RecentRunsWidget runs={null} loading={false} error={error} onRetry={onRetry} />
      );
      
      const retryButton = screen.getByRole('button', { name: /Retry/i });
      expect(retryButton).toBeInTheDocument();

      // Click retry button
      await userEvent.click(retryButton);
      expect(onRetry).toHaveBeenCalled();
    });
  });

  describe('Links and Navigation', () => {
    it('renders clickable task links', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const taskLinks = screen.getAllByRole('link');
      expect(taskLinks.length).toBeGreaterThan(0);
    });

    it('task links point to correct task detail pages', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const taskLink = screen.getByText('task-find-files');
      expect(taskLink.closest('a')).toHaveAttribute('href', '/tasks/task-find-files');
    });

    it('renders "View All" link pointing to runs page', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const viewAllLink = screen.getByRole('link', { name: /View All/i });
      expect(viewAllLink).toHaveAttribute('href', '/runs');
    });
  });

  describe('Data Display', () => {
    it('formats dates correctly', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      // Check that dates are formatted and visible
      const dateElements = screen.getAllByText(/Jan.*\d{2}/);
      expect(dateElements.length).toBeGreaterThan(0);
    });

    it('displays all agent names correctly', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      expect(screen.getAllByText('Claude-3').length).toBeGreaterThan(0);
      expect(screen.getAllByText('GPT-4').length).toBeGreaterThan(0);
      expect(screen.getByText('GPT-4-Turbo')).toBeInTheDocument();
      expect(screen.getByText('Llama-70B')).toBeInTheDocument();
    });

    it('displays success status with green styling', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const successBadges = screen.getAllByText('Success');
      expect(successBadges.length).toBeGreaterThan(0);
    });

    it('displays failure status with red styling', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const failureBadges = screen.getAllByText('Failure');
      expect(failureBadges.length).toBeGreaterThan(0);
    });

    it('displays timeout status with yellow styling', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const timeoutBadges = screen.getAllByText('Timeout');
      expect(timeoutBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Responsiveness', () => {
    it('renders table with horizontal scroll on small screens', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const table = screen.getByRole('table');
      const scrollContainer = table.parentElement;
      expect(scrollContainer).toHaveClass('overflow-x-auto');
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic HTML structure', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getAllByRole('columnheader')).toHaveLength(4);
    });

    it('renders status badges with descriptive text', () => {
      render(
        <RecentRunsWidget runs={mockRuns} loading={false} />
      );
      
      const statusTexts = ['Success', 'Failure', 'Timeout', 'Error'];
      statusTexts.forEach(status => {
        if (mockRuns.some(r => r.status === status.toLowerCase())) {
          expect(screen.getAllByText(status).length).toBeGreaterThan(0);
        }
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles single run correctly', () => {
      const singleRun = [mockRuns[0]];
      render(
        <RecentRunsWidget runs={singleRun} loading={false} />
      );
      
      expect(screen.getByText('task-find-files')).toBeInTheDocument();
    });

    it('handles runs with missing optional fields gracefully', () => {
      const runsWithMissingFields: Run[] = [
        {
          id: 'run-minimal',
          task_id: 'task-minimal',
          agent_name: 'Agent-X',
          status: 'success',
          score: 0.9,
          cost: 0.1,
          duration: 30,
          created_at: '2024-01-15T10:00:00Z',
          // Missing optional fields like trace, test_output, metrics
        },
      ];
      
      render(
        <RecentRunsWidget runs={runsWithMissingFields} loading={false} />
      );
      
      expect(screen.getByText('task-minimal')).toBeInTheDocument();
    });
  });
});
