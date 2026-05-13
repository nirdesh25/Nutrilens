'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for JWT token on mount
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
    } else {
      setIsAuthenticated(true);
    }
  }, [router]);

  // Don't render anything until authentication check is complete
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen relative overflow-hidden">
      {/* Organic Background Decorations */}
      <div className="organic-bg"></div>
      <div className="blob top-[-10%] left-[-10%] scale-150"></div>
      <div className="blob bottom-[-10%] right-[-10%] scale-125 bg-blue-500/10"></div>
      <div className="grain"></div>

      {/* Sidebar component */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content area */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Header with hamburger menu for mobile */}
        <header className="glass-dark backdrop-blur-xl shadow-lg lg:hidden sticky top-0 z-30 border-b border-white/10">
          <div className="flex items-center px-6 py-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-white/10 rounded-xl transition-all duration-300"
              aria-label="Open menu"
            >
              <Menu className="w-6 h-6 text-gray-300" />
            </button>
            <h1 className="ml-4 text-xl font-black bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent uppercase tracking-tight">NutriLens</h1>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}
