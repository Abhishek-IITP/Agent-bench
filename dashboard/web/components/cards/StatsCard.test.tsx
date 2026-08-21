import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import StatsCard from './StatsCard';
import { BarChart3 } from 'lucide-react';

describe('StatsCard Component', () => {
  it('renders label and value correctly', () => {
    render(
      <StatsCard
        label="Total Tasks"
        value="156"
        icon={<BarChart3 />}
      />
    );
    expect(screen.getByText('Total Tasks')).toBeTruthy();
    expect(screen.getByText('156')).toBeTruthy();
  });

  it('renders with numeric value', () => {
    render(
      <StatsCard
        label="Total Runs"
        value={1234}
        icon={<BarChart3 />}
      />
    );
    expect(screen.getByText('1234')).toBeTruthy();
  });

  it('renders loading skeleton', () => {
    const { container } = render(
      <StatsCard
        label="Test"
        value="0"
        icon={<BarChart3 />}
        loading={true}
      />
    );
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('displays trend indicator', () => {
    render(
      <StatsCard
        label="Tasks"
        value="100"
        icon={<BarChart3 />}
        trend={5}
        trendLabel="vs last week"
      />
    );
    expect(screen.getByText('5%')).toBeTruthy();
    expect(screen.getByText('vs last week')).toBeTruthy();
  });

  it('renders with different colors', () => {
    const { container: greenContainer } = render(
      <StatsCard
        label="Success"
        value="95%"
        icon={<BarChart3 />}
        color="green"
      />
    );
    expect(greenContainer.querySelector('.glass')).toBeTruthy();
  });

  it('renders glass morphism styling', () => {
    const { container } = render(
      <StatsCard
        label="Test"
        value="123"
        icon={<BarChart3 />}
      />
    );
    expect(container.querySelector('.glass')).toBeTruthy();
  });
});
