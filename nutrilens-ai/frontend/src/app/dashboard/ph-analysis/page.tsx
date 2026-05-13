'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { phAPI } from '@/lib/api';
import { Upload, FlaskConical, AlertTriangle, CheckCircle, ArrowLeft, ShieldCheck, Microscope, Zap } from 'lucide-react';

export default function PHAnalysisPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [foodType, setFoodType] = useState('milk');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      const response = await phAPI.analyze(selectedFile, foodType);
      setResult(response.data);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      alert(error.response?.data?.detail || 'Purity check failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fresh': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'questionable': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'spoiled': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

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
            <div className="bg-purple-500/10 p-4 rounded-2xl border border-purple-500/20">
              <FlaskConical className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Purity <span className="text-purple-400">Lab</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Analyze food quality and safety</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Upload Section */}
          <div className="glass backdrop-blur-2xl rounded-[3rem] p-8 md:p-10 border border-white/20 shadow-2xl animate-fade-in-up">
            <div className="flex items-center gap-3 mb-10">
                <Microscope className="w-6 h-6 text-purple-400" />
                <h2 className="text-2xl font-black text-white uppercase tracking-tight">Test Sample</h2>
            </div>
            
            <div className="space-y-8">
                <div className="space-y-3">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">
                    Food Category
                  </label>
                  <select
                    value={foodType}
                    onChange={(e) => setFoodType(e.target.value)}
                    className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-white font-bold appearance-none cursor-pointer"
                  >
                    <option value="milk" className="bg-slate-900">Milk / Dairy</option>
                    <option value="juice" className="bg-slate-900">Fruit Juice</option>
                    <option value="meat" className="bg-slate-900">Proteins / Meat</option>
                    <option value="default" className="bg-slate-900">Other Food</option>
                  </select>
                </div>
    
                {!preview ? (
                  <label className="flex flex-col items-center justify-center w-full h-80 border-2 border-dashed border-white/10 rounded-[2.5rem] cursor-pointer hover:border-purple-500/50 hover:bg-white/5 transition-all group">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-16 h-16 text-gray-400 mb-6 group-hover:scale-110 transition-transform group-hover:text-purple-400" />
                      <p className="mb-2 text-sm text-gray-400 font-bold uppercase tracking-widest">
                        Scan pH Strip Image
                      </p>
                      <p className="text-[10px] text-gray-600 font-bold uppercase tracking-tighter">RAW / JPG / PNG (UP TO 10MB)</p>
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
                    <div className="relative rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl">
                      <img
                        src={preview}
                        alt="pH Strip Preview"
                        className="w-full h-80 object-cover"
                      />
                      <button
                        onClick={() => {
                          setPreview(null);
                          setSelectedFile(null);
                          setResult(null);
                        }}
                        className="absolute top-4 right-4 px-4 py-2 bg-black/60 backdrop-blur-md text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-rose-500 transition-all border border-white/10"
                      >
                        Purge Sample
                      </button>
                    </div>
    
                    <button
                      onClick={handleAnalyze}
                      disabled={loading}
                      className="w-full py-5 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-3xl hover:scale-[1.02] active:scale-95 transition-all shadow-xl shadow-purple-500/20 flex items-center justify-center gap-3 font-black uppercase tracking-[0.2em] text-sm"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          Inference in Progress...
                        </>
                      ) : (
                        <>
                          <FlaskConical className="w-5 h-5" />
                          Execute Analysis
                        </>
                      )}
                    </button>
                  </div>
                )}
            </div>
          </div>

          {/* Results Section */}
          <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            {result ? (
              <div className="glass backdrop-blur-2xl rounded-[3rem] p-8 md:p-10 border border-white/20 shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
                    <ShieldCheck className="w-40 h-40 text-purple-400" />
                </div>
                
                <h2 className="text-2xl font-black text-white uppercase tracking-tight mb-10 relative z-10">Analysis Intel</h2>
                
                <div className="space-y-10 relative z-10">
                  <div className="grid grid-cols-2 gap-8">
                      <div className="bg-white/5 p-6 rounded-[2rem] border border-white/5">
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-3">Molecular pH</p>
                        <div className="flex items-baseline gap-2">
                          <p className="text-6xl font-black text-white tracking-tighter">{result.ph_value}</p>
                          <p className="text-xs font-black text-indigo-400 uppercase tracking-widest">Index</p>
                        </div>
                      </div>

                      <div className="bg-white/5 p-6 rounded-[2rem] border border-white/5">
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-3">Inference Confidence</p>
                        <div className="flex items-baseline gap-2">
                          <p className="text-6xl font-black text-white tracking-tighter">{(result.confidence * 100).toFixed(0)}</p>
                          <p className="text-xs font-black text-emerald-400 uppercase tracking-widest">%</p>
                        </div>
                      </div>
                  </div>

                  <div className="flex items-center justify-between p-6 bg-white/5 rounded-[2rem] border border-white/5">
                    <div>
                        <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Substrate Logic</p>
                        <p className="text-lg font-black text-white uppercase tracking-tight">{result.safe_range}</p>
                    </div>
                    <div className={`px-6 py-2 rounded-xl border-2 font-black text-[10px] uppercase tracking-widest ${getStatusColor(result.spoilage_status)}`}>
                        {result.spoilage_status}
                    </div>
                  </div>

                  <div className="pt-8 border-t border-white/10">
                    <div className={`flex items-start gap-4 p-6 rounded-[2rem] border-2 transition-all duration-500 ${
                      result.spoilage_status === 'fresh' 
                        ? 'bg-emerald-500/10 border-emerald-500/20' 
                        : result.spoilage_status === 'spoiled'
                        ? 'bg-rose-500/10 border-rose-500/20'
                        : 'bg-amber-500/10 border-amber-500/20'
                    }`}>
                      {result.spoilage_status === 'fresh' ? (
                        <div className="bg-emerald-500/20 p-2 rounded-xl">
                            <CheckCircle className="w-6 h-6 text-emerald-400" />
                        </div>
                      ) : (
                        <div className="bg-rose-500/20 p-2 rounded-xl">
                            <AlertTriangle className="w-6 h-6 text-rose-400" />
                        </div>
                      )}
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-widest opacity-60 mb-2">System Heuristic</p>
                        <p className="text-sm font-bold text-gray-200 leading-relaxed">{result.recommendation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass backdrop-blur-2xl rounded-[3rem] p-20 text-center border border-white/10 shadow-2xl">
                <FlaskConical className="w-20 h-20 text-white/10 mx-auto mb-6 animate-pulse" />
                <h3 className="text-xl font-black text-gray-600 uppercase tracking-widest">Awaiting Sample</h3>
                <p className="text-gray-500 text-[10px] font-black uppercase tracking-tighter mt-2">Initialize ingest to baseline molecular pH levels.</p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-12 bg-gradient-to-br from-purple-600 to-indigo-800 rounded-[3.5rem] p-12 text-white shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:scale-110 transition-transform duration-1000">
                <Zap className="w-64 h-64" />
            </div>
            <div className="relative z-10">
                <h3 className="text-3xl font-black mb-6 uppercase tracking-tight">Molecular Telemetry Logic</h3>
                <p className="text-purple-100 text-sm font-medium leading-relaxed mb-10 max-w-2xl">
                    Biological assets exhibit varying acidity thresholds during decomposition. NutriLens AI correlates real-time spectral strip data against known biological safety ranges to validate asset health.
                </p>
    
                <div className="grid md:grid-cols-3 gap-8">
                    <div className="bg-white/10 backdrop-blur-md rounded-[2rem] p-6 border border-white/10">
                        <h4 className="font-black text-xs uppercase tracking-widest mb-3 text-purple-300">Milk / Dairy</h4>
                        <p className="text-2xl font-black mb-1">6.4 - 6.8</p>
                        <p className="text-[10px] text-purple-200 font-bold uppercase opacity-60">Optimum pH Range</p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-[2rem] p-6 border border-white/10">
                        <h4 className="font-black text-xs uppercase tracking-widest mb-3 text-indigo-300">Juice Extract</h4>
                        <p className="text-2xl font-black mb-1">3.0 - 4.5</p>
                        <p className="text-[10px] text-indigo-200 font-bold uppercase opacity-60">Optimum pH Range</p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-[2rem] p-6 border border-white/10">
                        <h4 className="font-black text-xs uppercase tracking-widest mb-3 text-emerald-300">Proteins / Meat</h4>
                        <p className="text-2xl font-black mb-1">5.4 - 6.2</p>
                        <p className="text-[10px] text-emerald-200 font-bold uppercase opacity-60">Optimum pH Range</p>
                    </div>
                </div>
    
                <div className="mt-10 p-6 bg-black/20 rounded-[2rem] border border-white/5">
                    <p className="text-[10px] font-black text-purple-300 uppercase tracking-widest mb-1">Node Status:</p>
                    <p className="text-xs font-medium opacity-80 leading-relaxed">
                        Currently operating in <span className="font-black">Inference Mode</span>. Calibration requires a minimum of 200 spectral ingest samples for decentralized model training.
                    </p>
                </div>
            </div>
        </div>
      </main>
    </div>
  );
}
