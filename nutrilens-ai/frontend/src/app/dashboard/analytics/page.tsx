'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { wasteAPI } from '@/lib/api';
import { BarChart3, TrendingDown, Leaf, Award, ArrowLeft, Activity, Zap, PieChart } from 'lucide-react';

export default function AnalyticsPage() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    fetchAnalytics();
  }, [router]);

  const fetchAnalytics = async () => {
    try {
      const response = await wasteAPI.getAnalytics();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-teal-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Gathering your stats...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent">
      <header className="glass backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm font-medium">Back to Kitchen</span>
          </button>
          <div className="flex items-center gap-4">
            <div className="bg-teal-500/10 p-4 rounded-2xl border border-teal-500/20">
              <BarChart3 className="w-8 h-8 text-teal-400" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Usage <span className="text-teal-400">Analytics</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Your kitchen efficiency reports</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Key Metrics */}
        <div className="grid md:grid-cols-3 gap-8 mb-12 animate-fade-in-up">
          <MetricCard
            icon={<Leaf className="w-6 h-6" />}
            title="Eco Impact"
            value={`${analytics?.total_co2_saved || 0}`}
            unit="kg"
            subtitle="Carbon saved"
            color="text-emerald-400"
            bg="bg-emerald-500/10"
          />

          <MetricCard
            icon={<TrendingDown className="w-6 h-6" />}
            title="Total Actions"
            value={analytics?.total_actions || 0}
            unit="Items"
            subtitle="Food waste prevented"
            color="text-indigo-400"
            bg="bg-indigo-500/10"
          />

          <MetricCard
            icon={<Activity className="w-6 h-6" />}
            title="Activity"
            value={analytics?.recent_activity_count || 0}
            unit="Scans"
            subtitle="Last 30 days"
            color="text-rose-400"
            bg="bg-rose-500/10"
          />
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Actions Breakdown */}
            {analytics?.actions_by_type && analytics.actions_by_type.length > 0 && (
            <div className="glass backdrop-blur-2xl rounded-[3rem] p-10 border border-white/10 shadow-2xl animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                <div className="flex items-center gap-3 mb-10">
                    <PieChart className="w-6 h-6 text-indigo-400" />
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight">Mitigation Spectrum</h2>
                </div>

                <div className="space-y-8">
                {analytics.actions_by_type.map((item: any, index: number) => (
                    <div key={index} className="group">
                    <div className="flex items-center justify-between mb-3 px-1">
                        <span className="text-xs font-black text-gray-400 uppercase tracking-widest group-hover:text-white transition-colors">
                        {item.action.replace('_', ' ')}
                        </span>
                        <span className="text-sm font-black text-white">{item.count}</span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-3 border border-white/5 p-0.5">
                        <div
                        className="bg-gradient-to-r from-teal-500 to-indigo-600 h-full rounded-full transition-all duration-1000 group-hover:shadow-[0_0_15px_rgba(45,212,191,0.4)]"
                        style={{
                            width: `${(item.count / analytics.total_actions) * 100}%`
                        }}
                        ></div>
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}

            {/* Most Wasted Foods */}
            {analytics?.most_wasted_foods && analytics.most_wasted_foods.length > 0 && (
            <div className="glass backdrop-blur-2xl rounded-[3rem] p-10 border border-white/10 shadow-2xl animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="flex items-center gap-3 mb-10">
                    <Zap className="w-6 h-6 text-amber-400" />
                    <h2 className="text-2xl font-black text-white uppercase tracking-tight">Critical Vectors</h2>
                </div>

                <div className="grid gap-4">
                {analytics.most_wasted_foods.map((item: any, index: number) => (
                    <div
                    key={index}
                    className="flex items-center justify-between p-5 bg-white/5 rounded-2xl border border-white/5 hover:border-white/10 transition-all hover:scale-[1.02]"
                    >
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center border border-amber-500/20">
                        <span className="text-amber-400 font-black text-sm">0{index + 1}</span>
                        </div>
                        <span className="text-lg font-black text-white tracking-tight capitalize">{item.food}</span>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest leading-none mb-1">Frequency</p>
                        <span className="text-sm font-bold text-gray-300">{item.count} Cycles</span>
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}
        </div>

        {/* Impact Summary */}
        <div className="bg-gradient-to-br from-emerald-600 via-teal-700 to-indigo-800 rounded-[3.5rem] p-12 text-white shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:scale-110 transition-transform duration-1000">
                <Leaf className="w-64 h-64" />
            </div>
            <div className="relative z-10">
                <h3 className="text-4xl font-black mb-10 uppercase tracking-tighter">Planetary Synchronization</h3>
                <div className="grid md:grid-cols-3 gap-12">
                    <div className="space-y-2">
                        <p className="text-[10px] font-black text-emerald-300 uppercase tracking-[0.2em]">Atmospheric Recovery</p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-5xl font-black">{analytics?.total_co2_saved || 0}</span>
                            <span className="text-sm font-bold opacity-60 uppercase">kg CO₂</span>
                        </div>
                        <p className="text-xs font-medium opacity-60">Equivalent to {Math.round((analytics?.total_co2_saved || 0) * 4.5)} driven KM mitigated.</p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-[10px] font-black text-indigo-300 uppercase tracking-[0.2em]">Logic Validations</p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-5xl font-black">{analytics?.total_actions || 0}</span>
                            <span className="text-sm font-bold opacity-60 uppercase">Signals</span>
                        </div>
                        <p className="text-xs font-medium opacity-60">Environmental mitigation protocols successfully executed.</p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-[10px] font-black text-amber-300 uppercase tracking-[0.2em]">Biomass Salvage</p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-5xl font-black">{Math.round((analytics?.total_actions || 0) * 0.2 * 10) / 10}</span>
                            <span className="text-sm font-bold opacity-60 uppercase">kg Bio</span>
                        </div>
                        <p className="text-xs font-medium opacity-60">Estimated grocery mass successfully preserved.</p>
                    </div>
                </div>

                <div className="mt-12 p-6 bg-white/10 backdrop-blur-md rounded-3xl border border-white/10 group-hover:bg-white/15 transition-all">
                    <p className="text-sm font-medium leading-relaxed">
                        <span className="font-black text-white uppercase tracking-widest mr-2">Core Insight:</span>
                        Biological waste contributes to 10% of global emissions. Your unique <span className="font-black">Waste Vector</span> shows a efficiency gain of {analytics?.efficiency_gain || '24'}% over the last baseline cycle.
                    </p>
                </div>
            </div>
        </div>

        {/* Empty State */}
        {analytics?.total_actions === 0 && (
          <div className="glass backdrop-blur-xl rounded-[3rem] p-20 text-center border border-white/10 shadow-2xl mt-12">
            <BarChart3 className="w-20 h-20 text-white/5 mx-auto mb-6" />
            <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">Intelligence Null</h3>
            <p className="text-gray-500 mb-8 text-sm font-bold uppercase tracking-tighter">
              Awaiting first data ingest to baseline ecological performance.
            </p>
            <button
              onClick={() => router.push('/dashboard/scanner')}
              className="px-10 py-4 bg-teal-500 text-white rounded-[1.5rem] font-black uppercase tracking-widest hover:scale-110 active:scale-95 transition-all shadow-xl shadow-teal-500/20"
            >
              Initiate Ingest
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

function MetricCard({ icon, title, value, unit, subtitle, color, bg }: any) {
  return (
    <div className="glass backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/10 shadow-2xl flex flex-col items-center justify-center text-center group hover:scale-[1.05] transition-all duration-500">
      <div className={`${bg} ${color} p-4 rounded-2xl mb-6 group-hover:rotate-12 transition-transform`}>
        {icon}
      </div>
      <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 leading-none">{title}</p>
      <div className="flex items-baseline gap-1 mb-1">
        <span className="text-4xl font-black text-white tracking-tighter">{value}</span>
        <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{unit}</span>
      </div>
      <p className="text-[9px] font-bold text-gray-600 uppercase tracking-tighter">{subtitle}</p>
    </div>
  );
}
