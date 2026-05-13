'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { scanAPI } from '@/lib/api';
import { History, Image as ImageIcon, ChevronDown, ChevronUp, ArrowLeft, Terminal, Activity, FlaskConical } from 'lucide-react';

interface ScanResult {
  id: number;
  food_name: string;
  freshness_status: 'fresh' | 'slightly_aged' | 'rotten';
  risk_score: number;
  confidence: number;
  recommendation: string;
  image_url?: string;
  created_at: string;
}

type FilterStatus = 'all' | 'fresh' | 'slightly_aged' | 'rotten';

export default function HistoryPage() {
  const router = useRouter();
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [filteredScans, setFilteredScans] = useState<ScanResult[]>([]);
  const [filter, setFilter] = useState<FilterStatus>('all');
  const [expandedId, setExpandedId] = useState<number | null>(null);
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

  useEffect(() => {
    if (filter === 'all') {
      setFilteredScans(scans);
    } else {
      setFilteredScans(scans.filter(scan => scan.freshness_status === filter));
    }
  }, [scans, filter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await scanAPI.getHistory();
      const sortedScans = response.data.sort((a: ScanResult, b: ScanResult) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      
      setScans(sortedScans);
    } catch (err: any) {
      console.error('Failed to fetch scan history:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/auth/login');
      } else {
        setError(err.response?.data?.detail || 'Telemetry sync failed. Server unreachable.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'fresh': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'slightly_aged': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'rotten': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Parsing Telemetry Logs...</p>
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
            <span className="text-sm font-medium">Back to Terminal</span>
          </button>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Telemetry <span className="text-indigo-400">Logs</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Historical Sequence Data</p>
            </div>
            
            <div className="flex items-center gap-4 bg-white/5 p-2 rounded-2xl border border-white/10">
              <label htmlFor="filter" className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-3">Node Sort:</label>
              <select
                id="filter"
                value={filter}
                onChange={(e) => setFilter(e.target.value as FilterStatus)}
                className="bg-transparent text-white font-bold text-xs uppercase tracking-widest focus:outline-none pr-4 cursor-pointer"
              >
                <option value="all" className="bg-slate-900">All Sequences</option>
                <option value="fresh" className="bg-slate-900">Active / Fresh</option>
                <option value="slightly_aged" className="bg-slate-900">Aged / Warning</option>
                <option value="rotten" className="bg-slate-900">Rotten / Critical</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {filteredScans.length === 0 ? (
          <div className="glass backdrop-blur-xl rounded-[2.5rem] p-20 text-center border border-white/10 shadow-2xl animate-fade-in-up">
            <Terminal className="w-20 h-20 text-white/10 mx-auto mb-6" />
            <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">No Data Found</h3>
            <p className="text-gray-500 mb-8 text-sm font-bold uppercase tracking-tighter">
              {scans.length === 0 ? 'Initialize a scan sequence to begin logging.' : 'No items match current filter parameters.'}
            </p>
            {scans.length === 0 && (
                <button
                onClick={() => router.push('/dashboard/scanner')}
                className="px-10 py-4 bg-indigo-500 text-white rounded-[1.5rem] font-black uppercase tracking-widest hover:scale-110 active:scale-95 transition-all shadow-xl shadow-indigo-500/20"
                >
                Start Bio-Scan
                </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredScans.map((scan, idx) => (
              <div 
                key={scan.id} 
                className="glass backdrop-blur-2xl rounded-[2.5rem] border border-white/10 hover:border-white/30 transition-all duration-500 group animate-fade-in-up flex flex-col overflow-hidden"
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                {/* Image Section */}
                <div className="relative h-48 bg-white/5 overflow-hidden">
                  {scan.image_url ? (
                    <img
                      src={scan.image_url}
                      alt={scan.food_name}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center opacity-20">
                      <ImageIcon className="w-16 h-16 text-white" />
                    </div>
                  )}
                  <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-md px-3 py-1 rounded-xl border border-white/10">
                    <p className="text-[9px] font-black text-white tracking-[0.2em] uppercase">ID #{scan.id.toString().padStart(4, '0')}</p>
                  </div>
                </div>

                {/* Content Section */}
                <div className="p-8 flex-1 flex flex-col">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-black text-white tracking-tighter capitalize mb-1">{scan.food_name}</h3>
                      <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                        {new Date(scan.created_at).toLocaleDateString('en-US', {
                          month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className={`px-4 py-1 rounded-xl border-2 font-black text-[10px] uppercase tracking-widest ${getStatusColor(scan.freshness_status)}`}>
                        {scan.freshness_status?.replace('_', ' ') ?? 'Unknown'}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                        <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Risk Index</p>
                        <p className={`text-xl font-black ${scan.risk_score > 70 ? 'text-rose-400' : 'text-emerald-400'}`}>{scan.risk_score}%</p>
                    </div>
                    <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                        <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Confidence</p>
                        <p className="text-xl font-black text-indigo-400">{scan.confidence}%</p>
                    </div>
                  </div>

                  {expandedId === scan.id && (
                    <div className="pb-6 animate-in slide-in-from-top duration-300">
                      <div className="bg-indigo-500/10 p-4 rounded-2xl border border-indigo-500/20">
                        <p className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-2">System Result</p>
                        <p className="text-xs text-gray-200 font-bold leading-relaxed">{scan.recommendation}</p>
                      </div>
                    </div>
                  )}

                  <button
                    onClick={() => toggleExpand(scan.id)}
                    className="mt-auto w-full py-3 bg-white/5 border border-white/10 rounded-xl font-black uppercase tracking-widest text-[9px] hover:bg-white/10 transition-all flex items-center justify-center gap-2 group-hover:border-indigo-500/30"
                  >
                    {expandedId === scan.id ? (
                      <>Collate <ChevronUp className="w-3 h-3" /></>
                    ) : (
                      <>Expand Dataset <ChevronDown className="w-3 h-3" /></>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
