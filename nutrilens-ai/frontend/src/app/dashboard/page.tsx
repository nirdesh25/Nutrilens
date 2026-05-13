'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Scan, Leaf, Heart, Trash2, FlaskConical, Box, BarChart3, History, User, Settings, TrendingUp, Award, Zap } from 'lucide-react';
import { userAPI } from '@/lib/api';

interface UserStats {
  total_scans: number;
  co2_saved: number;
  waste_reduction_pct: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<UserStats | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    userAPI.getStats()
      .then((res) => setStats(res.data))
      .catch(() => setStats({ total_scans: 0, co2_saved: 0, waste_reduction_pct: 0 }));
  }, [router]);

  return (
    <div className="min-h-screen bg-transparent">

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 md:px-8 py-8 md:py-12">
        <div className="mb-12 md:mb-16 animate-fade-in-up">
          <p className="text-emerald-400 font-bold uppercase tracking-[0.3em] text-[10px] mb-2">Organic Kitchen Companion</p>
          <h2 className="text-5xl md:text-7xl font-bold text-white tracking-tighter mb-4">
            Hello, <span className="bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">Healthy Living</span>
          </h2>
          <div className="h-1 w-24 bg-gradient-to-r from-emerald-500 to-transparent rounded-full opacity-30"></div>
        </div>
 
        {/* Quick Stats */}
        <div className="mb-12 md:mb-16 grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          <StatCard
            icon={<Scan className="w-6 h-6" />}
            title="SAMPLES PROCESSED"
            value={stats ? String(stats.total_scans) : '—'}
            subtitle="Biological items analyzed"
            gradient="from-blue-500 to-cyan-500"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="ECO IMPACT"
            value={stats ? `${stats.co2_saved} kg` : '—'}
            subtitle="Carbon offset saved"
            gradient="from-emerald-500 to-teal-500"
          />
          <StatCard
            icon={<Award className="w-6 h-6" />}
            title="SAVINGS GAIN"
            value={stats ? `${stats.waste_reduction_pct}%` : '—'}
            subtitle="Waste reduction efficiency"
            gradient="from-purple-500 to-pink-500"
          />
        </div>
 
 
        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          <ModuleCard
            href="/dashboard/scanner"
            icon={<Scan className="w-10 h-10" />}
            title="Bio-Scanner"
            description="Neural engine for instant molecular freshness analysis"
            gradient="from-blue-600 to-indigo-700"
          />
          
          <ModuleCard
            href="/dashboard/groceries"
            icon={<Leaf className="w-10 h-10" />}
            title="Vault Inventory"
            description="Manage and track your biological grocery assets"
            gradient="from-emerald-600 to-teal-700"
          />
          
          <ModuleCard
            href="/dashboard/health"
            icon={<Heart className="w-10 h-10" />}
            title="Bio-Metrics"
            description="Configure personalized health flags and logic"
            gradient="from-rose-600 to-pink-700"
          />
          
          <ModuleCard
            href="/dashboard/waste"
            icon={<Trash2 className="w-10 h-10" />}
            title="Waste Matrix"
            description="Track environmental footprint and CO2 recovery"
            gradient="from-orange-600 to-amber-700"
          />
          
          <ModuleCard
            href="/dashboard/history"
            icon={<History className="w-10 h-10" />}
            title="Activity Journal"
            description="Review your past kitchen scans and food history"
            gradient="from-violet-600 to-purple-700"
          />
          
          <ModuleCard
            href="/dashboard/ph-analysis"
            icon={<FlaskConical className="w-10 h-10" />}
            title="Chemical Lab"
            description="Digital pH strip analysis for deep spoilage detection"
            gradient="from-pink-600 to-rose-700"
          />
          
          <ModuleCard
            href="/dashboard/smart-box"
            icon={<Box className="w-10 h-10" />}
            title="Smart Hardware"
            description="Environmental telemetry: Temp, Humidity, Gas"
            gradient="from-indigo-600 to-blue-700"
            badge="Hardware Pending"
          />
          
          <ModuleCard
            href="/dashboard/analytics"
            icon={<BarChart3 className="w-10 h-10" />}
            title="Visual Intel"
            description="Deep analytics on waste reduction impact"
            gradient="from-teal-600 to-emerald-700"
          />
          
          <ModuleCard
            href="/dashboard/profile"
            icon={<User className="w-10 h-10" />}
            title="Terminal OS"
            description="Manage core identifiers and system statistics"
            gradient="from-cyan-600 to-blue-700"
          />
        </div>
      </main>
    </div>
  );
}

function ModuleCard({ href, icon, title, description, gradient, badge }: {
  href: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
  badge?: string;
}) {
  return (
    <Link href={href}>
      <div className="group glass backdrop-blur-xl rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 p-6 cursor-pointer relative h-full min-h-[180px] border border-white/10 hover:border-white/30 hover:scale-105 animate-fade-in-up">
        {badge && (
          <span className="absolute top-4 right-4 px-3 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs font-bold rounded-full shadow-lg">
            {badge}
          </span>
        )}
        <div className={`bg-gradient-to-br ${gradient} text-white p-3 rounded-2xl inline-block mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
          {icon}
        </div>
        <h3 className="text-xl font-bold text-white mb-2 group-hover:text-green-400 transition-colors">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
        
        {/* Hover glow effect */}
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 rounded-3xl transition-opacity duration-500 pointer-events-none`}></div>
      </div>
    </Link>
  );
}

function StatCard({ icon, title, value, subtitle, gradient }: {
  icon: React.ReactNode;
  title: string;
  value: string;
  subtitle: string;
  gradient: string;
}) {
  return (
    <div className="glass backdrop-blur-xl rounded-3xl shadow-xl p-6 border border-white/10 hover:border-white/30 transition-all duration-500 hover:scale-105 animate-fade-in-up group">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-400">{title}</h3>
        <div className={`bg-gradient-to-br ${gradient} text-white p-2 rounded-xl group-hover:scale-110 transition-transform`}>
          {icon}
        </div>
      </div>
      <p className="text-3xl md:text-4xl font-bold text-white mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
      
      {/* Animated progress bar */}
      <div className="mt-4 h-1 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${gradient} w-0 group-hover:w-full transition-all duration-1000`}></div>
      </div>
    </div>
  );
}
