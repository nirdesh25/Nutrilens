'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { wasteAPI } from '@/lib/api';
import { Trash2, Leaf, TrendingUp, ArrowLeft, BarChart3, ShieldCheck, Zap } from 'lucide-react';

interface WasteLog {
  id: number;
  food_name: string;
  action: 'store_properly' | 'eat_immediately' | 'repurpose' | 'compost' | 'discard';
  co2_saved: number;
  created_at: string;
}

interface WasteAnalytics {
  total_co2_saved: number;
  total_actions: number;
  actions_by_type: Record<string, number>;
}

export default function WastePage() {
  const router = useRouter();
  const [logs, setLogs] = useState<WasteLog[]>([]);
  const [analytics, setAnalytics] = useState<WasteAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [logsResponse, analyticsResponse] = await Promise.all([
        wasteAPI.getLogs(),
        wasteAPI.getAnalytics(),
      ]);
      
      const sortedLogs = logsResponse.data.sort((a: WasteLog, b: WasteLog) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      
      setLogs(sortedLogs);
      setAnalytics(analyticsResponse.data);
    } catch (err: any) {
      console.error('Failed to fetch waste data:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/auth/login');
      } else {
        setError(err.response?.data?.detail || 'Impact telemetry failed to synchronize.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'store_properly': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'eat_immediately': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'repurpose': return 'text-indigo-400 bg-indigo-400/10 border-indigo-400/20';
      case 'compost': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
      case 'discard': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-orange-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Calculating your impact...</p>
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
            <div className="bg-orange-500/10 p-4 rounded-2xl border border-orange-500/20">
              <Trash2 className="w-8 h-8 text-orange-400" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Eco <span className="text-orange-400">Tracking</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Your environmental impact</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Summary Analytics */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 animate-fade-in-up">
            <div className="glass backdrop-blur-2xl rounded-[2.5rem] p-10 border border-white/10 shadow-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <Leaf className="w-32 h-32 text-emerald-400" />
              </div>
              <div className="flex items-center gap-4 mb-4">
                <div className="bg-emerald-500/20 p-2 rounded-xl">
                  <Leaf className="w-6 h-6 text-emerald-400" />
                </div>
                <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Global Carbon Offset</p>
              </div>
              <p className="text-5xl font-black text-white tracking-tighter mb-2">
                {analytics.total_co2_saved.toFixed(2)}<span className="text-xl text-gray-500 tracking-normal ml-2 font-bold uppercase">kg CO₂</span>
              </p>
              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 w-3/4 shadow-lg shadow-emerald-500/50"></div>
              </div>
            </div>

            <div className="glass backdrop-blur-2xl rounded-[2.5rem] p-10 border border-white/10 shadow-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <Zap className="w-32 h-32 text-indigo-400" />
              </div>
              <div className="flex items-center gap-4 mb-4">
                <div className="bg-indigo-500/20 p-2 rounded-xl">
                  <TrendingUp className="w-6 h-6 text-indigo-400" />
                </div>
                <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Mitigation Events</p>
              </div>
              <p className="text-5xl font-black text-white tracking-tighter mb-2">
                {analytics.total_actions}<span className="text-xl text-gray-500 tracking-normal ml-2 font-bold uppercase">Actions</span>
              </p>
              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-400 w-1/2 shadow-lg shadow-indigo-500/50"></div>
              </div>
            </div>
          </div>
        )}

        {/* Action Logs */}
        <div className="glass backdrop-blur-xl rounded-[3rem] p-10 border border-white/10 shadow-2xl animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
               <ShieldCheck className="w-6 h-6 text-orange-400" />
               <h2 className="text-2xl font-black text-white uppercase tracking-tight">Eco Journey</h2>
            </div>
            <div className="h-0.5 flex-1 mx-6 bg-white/5 hidden md:block"></div>
            <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Real-time impact</p>
          </div>

          {logs.length === 0 ? (
            <div className="text-center py-20">
              <BarChart3 className="w-16 h-16 text-white/5 mx-auto mb-6" />
              <h3 className="text-xl font-black text-gray-600 uppercase tracking-widest">No impact yet</h3>
              <p className="text-gray-500 text-xs font-bold mt-2">START SCANNING TO SEE YOUR ECO-RECOVERY DATA.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="group flex flex-col md:flex-row md:items-center p-6 bg-white/5 rounded-3xl border border-white/5 hover:border-white/20 transition-all duration-300"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <h4 className="text-xl font-black text-white tracking-tight capitalize">{log.food_name}</h4>
                      <div className={`px-4 py-1 rounded-xl border-2 font-black text-[9px] uppercase tracking-widest ${getActionColor(log.action)}`}>
                        {log.action.replace('_', ' ')}
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                             <Leaf className="w-4 h-4 text-emerald-400" />
                             <span className="text-xs font-black text-emerald-400">+{log.co2_saved.toFixed(2)}kg CO₂</span>
                        </div>
                        <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                            {new Date(log.created_at).toLocaleDateString('en-US', {
                                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                            })}
                        </div>
                    </div>
                  </div>
                  <div className="mt-4 md:mt-0 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-[9px] font-black text-white uppercase tracking-widest transition-all">
                          Details
                      </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
