import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import App from '../App';

// Mock all child components to isolate App tests
vi.mock('../components/ZoneOverview', () => ({
  default: () => <div data-testid="zone-overview">ZoneOverview</div>,
}));
vi.mock('../components/DocumentTable', () => ({
  default: () => <div data-testid="document-table">DocumentTable</div>,
}));
vi.mock('../components/EisenhowerMatrix', () => ({
  default: () => <div data-testid="eisenhower-matrix">EisenhowerMatrix</div>,
}));
vi.mock('../components/SessionPanel', () => ({
  default: () => <div data-testid="session-panel">SessionPanel</div>,
}));

// Mock the api module so health check doesn't make real requests
vi.mock('../api', () => ({
  api: {
    health: vi.fn().mockRejectedValue(new Error('no server')),
  },
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText('Neural Lattice Dashboard')).toBeInTheDocument();
  });

  it('renders all 4 tab buttons', () => {
    render(<App />);
    expect(screen.getByText('Zone Overview')).toBeInTheDocument();
    expect(screen.getByText('Document Triage')).toBeInTheDocument();
    expect(screen.getByText('Eisenhower Matrix')).toBeInTheDocument();
    expect(screen.getByText('Session')).toBeInTheDocument();
  });

  it('starts with Zone Overview as the active tab', () => {
    render(<App />);
    const overviewBtn = screen.getByText('Zone Overview');
    expect(overviewBtn).toHaveClass('active');
  });

  it('switches active tab when clicking a different tab', async () => {
    render(<App />);

    const matrixBtn = screen.getByText('Eisenhower Matrix');
    await act(async () => {
      fireEvent.click(matrixBtn);
    });

    expect(matrixBtn).toHaveClass('active');
    expect(screen.getByText('Zone Overview')).not.toHaveClass('active');
    expect(screen.getByTestId('eisenhower-matrix')).toBeInTheDocument();
  });

  it('shows Session panel when Session tab is clicked', async () => {
    render(<App />);

    await act(async () => {
      fireEvent.click(screen.getByText('Session'));
    });
    expect(screen.getByTestId('session-panel')).toBeInTheDocument();
  });
});
