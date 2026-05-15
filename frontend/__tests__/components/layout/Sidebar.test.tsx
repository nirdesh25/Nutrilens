import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { usePathname, useRouter } from 'next/navigation';
import Sidebar from '@/components/layout/Sidebar';

// Mock Next.js navigation hooks
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
  useRouter: jest.fn(),
}));

describe('Sidebar Component', () => {
  const mockPush = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (usePathname as jest.Mock).mockReturnValue('/dashboard');
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
      },
      writable: true,
    });
  });

  test('renders NutriLens AI logo and name', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    expect(screen.getByText('NutriLens AI')).toBeInTheDocument();
  });

  test('renders all 11 navigation items', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    
    const expectedLabels = [
      'Dashboard',
      'Scanner',
      'Groceries',
      'Health',
      'Waste Tracker',
      'Scan History',
      'pH Analysis',
      'Smart Box',
      'Analytics',
      'Profile',
      'Settings',
    ];

    expectedLabels.forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  test('highlights active link based on current pathname', () => {
    (usePathname as jest.Mock).mockReturnValue('/dashboard/scanner');
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    
    const scannerLink = screen.getByText('Scanner').closest('a');
    expect(scannerLink?.className).toContain('bg-green-50');
    expect(scannerLink?.className).toContain('text-green-700');
  });

  test('renders logout button', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    const closeButton = screen.getByLabelText('Close sidebar');
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when backdrop is clicked', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    const backdrop = document.querySelector('.bg-black\\/50');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    }
  });

  test('calls onClose when navigation link is clicked', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    const scannerLink = screen.getByText('Scanner');
    fireEvent.click(scannerLink);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  test('handles logout correctly', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    
    expect(localStorage.removeItem).toHaveBeenCalledWith('token');
    expect(mockPush).toHaveBeenCalledWith('/');
  });

  test('applies correct classes when isOpen is true', () => {
    const { container } = render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    const sidebar = container.querySelector('aside');
    expect(sidebar?.className).toContain('translate-x-0');
  });

  test('applies correct classes when isOpen is false', () => {
    const { container } = render(<Sidebar isOpen={false} onClose={mockOnClose} />);
    const sidebar = container.querySelector('aside');
    expect(sidebar?.className).toContain('-translate-x-full');
  });

  test('does not render backdrop when isOpen is false', () => {
    render(<Sidebar isOpen={false} onClose={mockOnClose} />);
    const backdrop = document.querySelector('.bg-black\\/50');
    expect(backdrop).not.toBeInTheDocument();
  });

  test('all navigation items have correct href attributes', () => {
    render(<Sidebar isOpen={true} onClose={mockOnClose} />);
    
    const expectedHrefs = [
      '/dashboard',
      '/dashboard/scanner',
      '/dashboard/groceries',
      '/dashboard/health',
      '/dashboard/waste',
      '/dashboard/history',
      '/dashboard/ph-analysis',
      '/dashboard/smart-box',
      '/dashboard/analytics',
      '/dashboard/profile',
      '/dashboard/settings',
    ];

    expectedHrefs.forEach((href) => {
      const link = document.querySelector(`a[href="${href}"]`);
      expect(link).toBeInTheDocument();
    });
  });
});
