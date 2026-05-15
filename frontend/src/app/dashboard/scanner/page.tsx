'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { scanAPI, wasteAPI } from '@/lib/api';
import { Upload, Scan, AlertCircle, CheckCircle, Leaf, Heart, Trash2, ArrowLeft } from 'lucide-react';

export default function ScannerPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [wasteDecision, setWasteDecision] = useState<any>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setWasteDecision(null);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleScan = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      const response = await scanAPI.predictFreshness(selectedFile);
      setResult(response.data);

      // Get waste decision
      if (response.data.risk_score) {
        const decision = await wasteAPI.logAction({
          food_name: response.data.food_name,
          action: getActionFromRisk(response.data.risk_score),
          co2_saved: calculateCO2(response.data.risk_score)
        });
        setWasteDecision(decision.data);
      }
    } catch (error: any) {
      console.error('Scan failed:', error);
      const detail = error.response?.data?.detail || error.message || 'The neural engine is currently unreachable. Please check your connection or try again later.';
      alert(`SCAN ERROR: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const getActionFromRisk = (risk: number): string => {
    if (risk < 30) return 'store_properly';
    if (risk < 70) return 'eat_immediately';
    if (risk < 85) return 'repurpose';
    if (risk < 95) return 'compost';
    return 'discard';
  };

  const calculateCO2 = (risk: number): number => {
    return Math.round((risk / 100) * 0.5 * 100) / 100;
  };

  const getFreshnessColor = (status: string) => {
    switch (status) {
      case 'fresh': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'slightly_aged': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'rotten': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-emerald-400';
    if (score < 70) return 'text-amber-400';
    return 'text-rose-400';
  };

  return (
    <div className="min-h-screen bg-transparent">
      <header className="glass backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm font-medium">Back to Kitchen</span>
          </button>
          <h1 className="text-4xl font-black text-white tracking-tight">Food <span className="text-emerald-400">Scanner</span></h1>
          <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Smart freshness detection</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8 items-start">
          {/* Upload Section */}
          <div className="glass backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/10 shadow-2xl">
            <div className="flex items-center gap-3 mb-8">
              <div className="bg-emerald-500/20 p-2 rounded-xl">
                <Upload className="w-6 h-6 text-emerald-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">Ingest Sample</h2>
            </div>
            
            {!preview ? (
              <label className="group relative flex flex-col items-center justify-center w-full h-80 border-2 border-dashed border-white/10 rounded-[2rem] cursor-pointer hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all duration-500">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <div className="bg-white/5 p-6 rounded-full mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="w-10 h-10 text-gray-400 group-hover:text-emerald-400 transition-colors" />
                  </div>
                  <p className="mb-2 text-sm text-gray-300">
                    <span className="font-bold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-[10px] text-gray-500 uppercase tracking-widest font-black">High Res Images Preferred</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileSelect}
                />
              </label>
            ) : (
              <div className="space-y-6">
                <div className="relative group overflow-hidden rounded-[2rem] border border-white/20 shadow-2xl">
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-80 object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <button
                    onClick={() => {
                      setPreview(null);
                      setSelectedFile(null);
                      setResult(null);
                      setWasteDecision(null);
                    }}
                    className="absolute top-4 right-4 p-2 bg-rose-500/80 backdrop-blur-md text-white rounded-xl text-xs hover:bg-rose-500 transition-colors"
                  >
                    Discard
                  </button>
                </div>

                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full py-5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-[1.5rem] hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 font-black uppercase tracking-widest shadow-xl shadow-emerald-500/20"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Scan className="w-6 h-6" />
                      Initialize Scan
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {result ? (
              <div className="animate-fade-in-up">
                {/* Main Analysis Card - Premium Glassmorphism */}
                <div className="glass backdrop-blur-2xl rounded-[2.5rem] shadow-2xl p-6 md:p-8 border border-white/20 relative overflow-hidden group">
                  <div className="relative z-10">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                      <div>
                        <p className="text-[10px] font-bold text-emerald-400 mb-1 uppercase tracking-[0.2em]">Analysis Complete</p>
                        <h2 className="text-3xl md:text-5xl font-black text-white">{result.food_name}</h2>
                      </div>
                      <div className={`px-6 py-2 rounded-2xl font-black text-xs md:text-sm tracking-widest text-center border-2 ${getFreshnessColor(result.freshness_status)}`}>
                        {result.freshness_status.toUpperCase().replace('_', ' ')}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                      {/* Risk Meter */}
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400 font-bold uppercase tracking-widest text-[10px]">Risk Index</span>
                          <span className={`text-3xl font-black ${getRiskColor(result.risk_score)}`}>{result.risk_score}%</span>
                        </div>
                        <div className="h-4 bg-white/5 rounded-full p-1 border border-white/10">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ease-out shadow-lg ${
                              result.risk_score < 30 ? 'bg-gradient-to-r from-green-400 to-emerald-500 shadow-green-500/50' :
                              result.risk_score < 70 ? 'bg-gradient-to-r from-orange-400 to-amber-500 shadow-orange-500/50' : 
                              'bg-gradient-to-r from-red-500 to-rose-600 shadow-red-500/50'
                            }`}
                            style={{ width: `${result.risk_score}%` }}
                          ></div>
                        </div>
                        <p className="text-[10px] text-gray-500 uppercase font-black">Confidence Factor: {(result.confidence * 100).toFixed(1)}%</p>
                      </div>

                      {/* Health Status Indicator */}
                      <div className={`p-6 rounded-[2rem] border-2 ${
                        result.health_analysis?.status === 'recommended' ? 'bg-emerald-500/10 border-emerald-500/20' :
                        result.health_analysis?.status === 'avoid' ? 'bg-rose-500/10 border-rose-500/20' :
                        result.health_analysis?.status === 'caution' ? 'bg-amber-500/10 border-amber-500/20' :
                        'bg-white/5 border-white/10'
                      }`}>
                        <div className="flex items-center gap-3 mb-3">
                          <Heart className={`w-5 h-5 ${
                            result.health_analysis?.status === 'recommended' ? 'text-emerald-400' :
                            result.health_analysis?.status === 'avoid' ? 'text-rose-400' : 'text-amber-400'
                          }`} />
                          <span className="font-black uppercase tracking-widest text-[10px] text-white">Health Logic</span>
                        </div>
                        <p className="text-sm text-gray-200 font-medium leading-relaxed">
                          {result.health_analysis?.message || "Set up your health profile for AI optimization."}
                        </p>
                        {result.health_analysis?.tags?.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-4">
                            {result.health_analysis.tags.map((tag: string, i: number) => (
                              <span key={i} className="text-[9px] uppercase font-black px-2.5 py-1 bg-white/10 text-white rounded-lg border border-white/10">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Recommendation Box */}
                    <div className="p-6 bg-blue-500/10 rounded-[2rem] border-2 border-blue-500/20 transition-all hover:bg-blue-500/15">
                      <div className="flex items-start gap-4">
                        <div className="bg-blue-500/20 p-2 rounded-xl">
                          <AlertCircle className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                          <p className="text-[10px] font-black text-blue-400 uppercase tracking-widest mb-1">Advisor Protocol</p>
                          <p className="text-sm text-gray-200 font-bold leading-snug">{result.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Nutrition Card */}
                {result.nutrition && (
                  <div className="mt-6 glass backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/20 animate-fade-in-up">
                    <div className="flex items-center gap-3 mb-8">
                      <div className="bg-emerald-500/20 p-2 rounded-xl">
                        <Leaf className="w-5 h-5 text-emerald-400" />
                      </div>
                      <h3 className="text-xl font-black text-white uppercase tracking-widest">Bio Metrics</h3>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <MetricBox label="Calories" value={result.nutrition.calories} unit="kcal" color="text-amber-400" bg="bg-amber-400/10" />
                      <MetricBox label="Protein" value={result.nutrition.protein} unit="g" color="text-blue-400" bg="bg-blue-400/10" />
                      <MetricBox label="Carbs" value={result.nutrition.carbohydrates} unit="g" color="text-emerald-400" bg="bg-emerald-400/10" />
                      <MetricBox label="Fiber" value={result.nutrition.fiber} unit="g" color="text-purple-400" bg="bg-purple-400/10" />
                    </div>
                  </div>
                )}

                {/* Sustainability Impact */}
                {wasteDecision && (
                  <div className="mt-6 glass backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/20 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-3">
                        <div className="bg-orange-500/20 p-2 rounded-xl">
                          <Leaf className="w-5 h-5 text-orange-400" />
                        </div>
                        <h3 className="text-xl font-black text-white uppercase tracking-widest">Planetary Gear</h3>
                      </div>
                      <div className="flex items-center gap-2 px-6 py-2 bg-emerald-500/20 rounded-full border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
                        <span className="text-[10px] font-black text-emerald-400 uppercase">{wasteDecision.co2_saved}kg CO₂ RECOVERED</span>
                      </div>
                    </div>
                    
                    <div className="p-6 bg-orange-500/5 rounded-[2rem] border-2 border-orange-500/10">
                      <p className="text-[10px] font-black text-orange-400 uppercase tracking-widest mb-1">Waste Vector</p>
                      <p className="text-2xl font-black text-white capitalize tracking-tighter">{wasteDecision.action.replace('_', ' ')}</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass backdrop-blur-xl rounded-[2.5rem] p-12 border border-white/10 h-full flex flex-col items-center justify-center text-center">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-emerald-500 blur-3xl opacity-20 animate-pulse"></div>
                  <Scan className="w-24 h-24 text-white/10 relative z-10" />
                </div>
                <h3 className="text-3xl font-black text-white mb-3 tracking-tight">System Idle</h3>
                <p className="text-gray-500 text-sm max-w-[240px] leading-relaxed uppercase tracking-tighter font-bold">
                  Feed food imagery to the neural engine for full biological profiling.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function MetricBox({ label, value, unit, color, bg }: { label: string, value: any, unit: string, color: string, bg: string }) {
  return (
    <div className={`${bg} p-6 rounded-[2rem] border border-white/5 flex flex-col items-center justify-center hover:scale-105 transition-all duration-500`}>
      <p className="text-[9px] font-black text-gray-500 uppercase mb-2 tracking-widest leading-none">{label}</p>
      <div className="flex items-baseline gap-0.5">
        <span className={`text-2xl font-black ${color} tracking-tighter leading-none`}>{value || '0'}</span>
        <span className="text-[9px] font-black text-gray-500 uppercase tracking-widest ml-1">{unit}</span>
      </div>
    </div>
  );
}
