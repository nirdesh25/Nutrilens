import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/layout/DashboardLayout';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(() => '/dashboard'),
}));

// Mock Sidebar component
jest.mock('@/components/layout/Sidebar', () => {
  return function MockSidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    return (
      <div data-testid="sidebar" data-open={isOpen}>
        <button onClick={onClose}>Close Sidebar</button>
      </div>
    );
  };
});

describe('DashboardLayout', () => {
  let mockPush: jest.Mock;

  beforeEach(() => {
    mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication', () => {
    test('redirects to login when no token exists', () => {
      render(
        <DashboardLayout>
          <div>Dashboard Content</div>
        </DashboardLayout>
      );

      expect(mockPush).toHaveBeenCalledWith('/auth/login');
    });

    test('renders children when token exists', async () => {
      localStorage.setItem('token', 'fake-jwt-token');

      render(
        <DashboardLayout>
          <div>Dashboard Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
      });
      expect(mockPush).not.toHaveBeenCalled();
    });

    test('does not render content before authentication check', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Dashboard Content</div>
        </DashboardLayout>
      );

      // Before authentication check completes, nothing should render
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Sidebar Management', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'fake-jwt-token');
    });

    test('sidebar is closed by default', async () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        const sidebar = screen.getByTestId('sidebar');
        expect(sidebar).toHaveAttribute('data-open', 'false');
      });
    });

    test('opens sidebar when hamburger menu is clicked', async () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
      });

      const menuButton = screen.getByLabelText('Open menu');
      fireEvent.click(menuButton);

      await waitFor(() => {
        const sidebar = screen.getByTestId('sidebar');
        expect(sidebar).toHaveAttribute('data-open', 'true');
      });
    });

    test('closes sidebar when close button is clicked', async () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByLabelText('Open menu')).toBeInTheDocument();
      });

      // Open sidebar
      const menuButton = screen.getByLabelText('Open menu');
      fireEvent.click(menuButton);

      await waitFor(() => {
        const sidebar = screen.getByTestId('sidebar');
        expect(sidebar).toHaveAttribute('data-open', 'true');
      });

      // Close sidebar
      const closeButton = screen.getByText('Close Sidebar');
      fireEvent.click(closeButton);

      await waitFor(() => {
        const sidebar = screen.getByTestId('sidebar');
        expect(sidebar).toHaveAttribute('data-open', 'false');
      });
    });
  });

  describe('Layout Structure', () => {
    beforeEach(() => {
      localStorage.setItem('token', 'fake-jwt-token');
    });

    test('renders header with app name on mobile', async () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByText('NutriLens AI')).toBeInTheDocument();
      });
    });

    test('renders sidebar component', async () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByTestId('sidebar')).toBeInTheDocument();
      });
    });

    test('renders children in main content area', async () => {
      render(
        <DashboardLayout>
          <div data-testid="child-content">Test Content</div>
        </DashboardLayout>
      );

      await waitFor(() => {
        expect(screen.getByTestId('child-content')).toBeInTheDocument();
      });
    });
  });
});
