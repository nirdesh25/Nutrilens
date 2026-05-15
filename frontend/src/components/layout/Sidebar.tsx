'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Scan,
  Leaf,
  Heart,
  Trash2,
  History,
  FlaskConical,
  Box,
  BarChart3,
  User,
  Settings,
  LogOut,
  X,
  Apple,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Kitchen Home', gradient: 'from-blue-600 to-cyan-700' },
  { href: '/dashboard/scanner', icon: Scan, label: 'Food Scan', gradient: 'from-purple-600 to-pink-700' },
  { href: '/dashboard/groceries', icon: Leaf, label: 'Smart Pantry', gradient: 'from-emerald-600 to-teal-700' },
  { href: '/dashboard/health', icon: Heart, label: 'Health Insights', gradient: 'from-rose-600 to-pink-700' },
  { href: '/dashboard/waste', icon: Trash2, label: 'Eco Tracking', gradient: 'from-orange-600 to-amber-700' },
  { href: '/dashboard/history', icon: History, label: 'Recent History', gradient: 'from-violet-600 to-purple-700' },
  { href: '/dashboard/ph-analysis', icon: FlaskConical, label: 'Purity Lab', gradient: 'from-indigo-600 to-purple-700' },
  { href: '/dashboard/smart-box', icon: Box, label: 'Smart Device', gradient: 'from-cyan-600 to-blue-700' },
  { href: '/dashboard/nutrition', icon: Apple, label: 'Nutrition Advisor', gradient: 'from-lime-600 to-emerald-700' },
  { href: '/dashboard/analytics', icon: BarChart3, label: 'Usage Analytics', gradient: 'from-teal-600 to-indigo-700' },
  { href: '/dashboard/profile', icon: User, label: 'Profile Settings', gradient: 'from-pink-600 to-rose-700' },
  { href: '/dashboard/settings', icon: Settings, label: 'App Config', gradient: 'from-gray-600 to-slate-700' },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-md z-40 lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-80 glass-dark backdrop-blur-3xl shadow-2xl z-50 border-r border-white/5
          transform transition-all duration-700 cubic-bezier(0.4, 0, 0.2, 1)
          lg:translate-x-0 lg:static
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo and close button */}
          <div className="flex items-center justify-between p-10">
            <div className="flex flex-col gap-1 group cursor-pointer" onClick={() => router.push('/dashboard')}>
              <div className="flex items-center gap-4">
                <div className="relative">
                    <div className="absolute inset-0 bg-emerald-500 blur-2xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
                    <Image src="/logo.png" alt="NutriLens Logo" width={42} height={42} className="relative z-10 group-hover:scale-110 transition-transform duration-500" />
                </div>
                <div className="flex flex-col">
                    <span className="text-2xl font-black tracking-tighter text-white uppercase leading-none">
                        Nutri<span className="text-emerald-400">Lens</span>
                    </span>
                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-[0.3em] mt-1 opacity-60">Healthy Living</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-white/5 rounded-xl transition-all duration-300"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Navigation items */}
          <nav className="flex-1 overflow-y-auto px-6 py-4 space-y-1.5 custom-scrollbar">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={`
                    group flex items-center gap-4 px-5 py-4 rounded-[1.25rem]
                    transition-all duration-500 relative overflow-hidden
                    ${
                      isActive
                        ? 'bg-gradient-to-r ' + item.gradient + ' text-white shadow-2xl shadow-indigo-500/20 scale-[1.02]'
                        : 'text-gray-500 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  {/* Glass highlight on active */}
                  {isActive && (
                    <div className="absolute inset-0 bg-white/10 backdrop-blur-sm opacity-0 group-hover:opacity-10 transition-opacity"></div>
                  )}
                  
                  <Icon className={`w-5 h-5 relative z-10 transition-all duration-500 ${isActive ? 'scale-110' : 'group-hover:scale-125 group-hover:rotate-6'}`} />
                  <span className={`relative z-10 text-[11px] font-black uppercase tracking-widest transition-all duration-300 ${isActive ? 'opacity-100' : 'opacity-80 group-hover:opacity-100'}`}>
                    {item.label}
                  </span>
                  
                  {/* Pulse indicator for active */}
                  {isActive && (
                    <div className="absolute right-4 w-1.5 h-1.5 bg-white rounded-full animate-pulse shadow-[0_0_10px_rgba(255,255,255,0.8)]"></div>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Logout button */}
          <div className="p-8 mt-auto border-t border-white/5">
            <button
              onClick={handleLogout}
              className="group flex items-center gap-4 w-full px-5 py-4 rounded-2xl text-rose-500/60 hover:text-rose-400 hover:bg-rose-500/5 transition-all duration-500 relative overflow-hidden"
            >
              <LogOut className="w-5 h-5 relative z-10 group-hover:-translate-x-1 transition-transform" />
              <span className="relative z-10 text-[11px] font-black uppercase tracking-widest">Terminate Session</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
