'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { sensorAPI } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import { Thermometer, Droplets, Wind, Sun, AlertTriangle, CheckCircle, Box, ArrowLeft, Zap } from 'lucide-react';

// Thresholds for alerts
const THRESHOLDS = {
  temperature: { warning: 2, critical: 5 },   // °C variation
  humidity:    { warning: 10, critical: 20 },  // % variation
  gas_level:   { warning: 5, critical: 20 },   // PPM variation - alert if changes by more than 5
};

export default function SmartBoxPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [sensorData, setSensorData] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const prevDataRef = useRef<any>(null);

  const [milkForm, setMilkForm] = useState({ ph: 6.6, temperature: 4, taste: 1, odor: 1, fat: 1, turbidity: 1, color: 1 });
  const [milkResult, setMilkResult] = useState<any>(null);
  const [analyzingMilk, setAnalyzingMilk] = useState(false);

  const handleAnalyzeMilk = async () => {
    setAnalyzingMilk(true);
    try {
      const response = await sensorAPI.analyzeMilkQuality(milkForm);
      setMilkResult(response.data);
    } catch (e) {
      console.error(e);
    } finally {
      setAnalyzingMilk(false);
    }
  };

  // Check for significant variations and trigger alerts
  const checkVariations = (newData: any, prevData: any) => {
    if (!prevData || !newData) return;

    const tempDiff = Math.abs(newData.temperature - prevData.temperature);
    const humDiff  = Math.abs(newData.humidity    - prevData.humidity);
    const gasDiff  = Math.abs(newData.gas_level   - prevData.gas_level);

    // Temperature alerts - only if crosses 42°C
    if (newData.temperature > 42 && prevData.temperature <= 42) {
      showToast({ type: 'error', message: `🔥 Temperature crossed 42°C! Current: ${newData.temperature}°C — Food safety risk!` });
    } else if (newData.temperature > 42) {
      showToast({ type: 'warning', message: `🌡️ Temperature above 42°C: ${newData.temperature}°C` });
    }

    // Combined temperature and PPM alert - both must cross 40
    if (newData.temperature > 40 && newData.gas_level > 40) {
      showToast({ 
        type: 'error', 
        message: `🚨 CRITICAL: Both temperature (${newData.temperature}°C) and PPM (${newData.gas_level}) above 40! Immediate action required!` 
      });
    }

    if (newData.humidity > 80) {
      showToast({ type: 'warning', message: `💦 High humidity: ${newData.humidity}% — Mold risk!` });
    }
  };

  const fetchData = async () => {
    try {
      const [dataRes, statusRes] = await Promise.all([
        sensorAPI.getCurrent(),
        sensorAPI.getStatus(),
      ]);
      const newData = dataRes.data;
      console.log('Sensor data received:', newData);

      // Check for variations before updating state
      checkVariations(newData, prevDataRef.current);
      prevDataRef.current = newData;

      setSensorData(newData);
      setStatus(statusRes.data);
    } catch (error) {
      console.error('Failed to fetch sensor data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/auth/login'); return; }
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Checking your kitchen environment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent">
      {/* Header */}
      <header className="glass backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm font-medium">Back to Kitchen</span>
          </button>
          <h1 className="text-4xl font-black text-white tracking-tight">Smart <span className="text-indigo-400">Device</span></h1>
          <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Real-time kitchen environment tracking</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Connection Status */}
        <div className="mb-12 glass backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/20 shadow-2xl animate-fade-in-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-5">
              <div className="bg-indigo-500/20 p-4 rounded-2xl border border-indigo-500/20 shadow-lg shadow-indigo-500/10">
                <Box className="w-8 h-8 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white uppercase tracking-tight">Node Integrity</h2>
                <p className="text-gray-400 text-xs font-bold uppercase tracking-widest opacity-60 mt-1">{status?.message || 'Awaiting signal...'}</p>
              </div>
            </div>
            <div className={`flex items-center gap-3 px-6 py-2 rounded-full border-2 font-black text-[10px] uppercase tracking-widest ${
                status?.connected ? 'text-emerald-400 border-emerald-400/20 bg-emerald-400/5' : 'text-amber-400 border-amber-400/20 bg-amber-400/5'
            }`}>
              {status?.connected ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Real-time Link</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4" />
                  <span>Synthetic Data</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Sensor Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <SensorCard
            icon={<Thermometer className="w-8 h-8" />}
            title="Temperature"
            value={sensorData?.temperature != null ? `${sensorData.temperature}°C` : '—'}
            status={getTemperatureStatus(sensorData?.temperature)}
            color="bg-red-500"
          />
          
          <SensorCard
            icon={<Droplets className="w-8 h-8" />}
            title="Humidity"
            value={sensorData?.humidity != null ? `${sensorData.humidity}%` : '—'}
            status={getHumidityStatus(sensorData?.humidity)}
            color="bg-blue-500"
          />
          
          <SensorCard
            icon={<Wind className="w-8 h-8" />}
            title="Gas Level"
            value={sensorData?.gas_level != null ? `${sensorData.gas_level} PPM` : '—'}
            status={getGasStatus(sensorData?.gas_level)}
            color="bg-purple-500"
          />
          
          <SensorCard
            icon={<Sun className="w-8 h-8" />}
            title="Light Level"
            value={sensorData?.light_level != null ? `${sensorData.light_level}%` : '—'}
            status="normal"
            color="bg-yellow-500"
          />
        </div>

        {/* Alerts */}
        {sensorData?.alerts && sensorData.alerts.length > 0 && (
          <div className="glass backdrop-blur-xl rounded-[2.5rem] p-8 mb-12 border border-white/10 shadow-2xl animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center gap-3 mb-8">
                <AlertTriangle className="w-6 h-6 text-amber-400" />
                <h3 className="text-xl font-black text-white uppercase tracking-widest">Heuristic Alerts</h3>
            </div>
            <div className="space-y-4">
              {sensorData.alerts.map((alert: string, index: number) => (
                <div
                  key={index}
                  className={`p-6 rounded-[1.5rem] flex items-start gap-4 transition-all hover:scale-[1.01] ${
                    alert.includes('normal')
                      ? 'bg-emerald-500/5 border border-emerald-500/20 text-emerald-100'
                      : alert.includes('High') || alert.includes('Low')
                      ? 'bg-amber-500/5 border border-amber-500/20 text-amber-100'
                      : 'bg-rose-500/5 border border-rose-500/20 text-rose-100'
                  }`}
                >
                  {alert.includes('normal') ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5 shrink-0" />
                  )}
                  <p className="text-sm font-medium leading-relaxed">{alert}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* IoT Integration Info */}
        <div className="bg-gradient-to-br from-indigo-600 via-purple-700 to-indigo-900 rounded-[3rem] p-10 text-white mb-12 shadow-2xl shadow-indigo-500/20 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:rotate-12 transition-transform duration-1000">
            <Zap className="w-64 h-64" />
          </div>
          <div className="relative z-10">
            <h3 className="text-3xl font-black mb-6 uppercase tracking-tight">Hardware Protocol Ready</h3>
            <p className="mb-8 text-indigo-100 text-sm font-medium leading-relaxed max-w-2xl">
              The Smart Vault logic is operational. Currently ingest is routed through <span className="font-black">Synthetic Telemetry</span>. Connect your hardware layer for live biological monitoring.
            </p>
            <div className="grid md:grid-cols-2 gap-6 mt-6">
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                <h4 className="font-black text-xs uppercase tracking-widest mb-3 text-indigo-300">Supported Sensors</h4>
                <ul className="text-xs text-indigo-100 space-y-2 font-medium">
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400"></div>
                        DHT22 (Atmospheric Flux)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400"></div>
                        MQ-135 (Biomass Degradation)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-400"></div>
                        LDR (Luminous Index)
                    </li>
                </ul>
                </div>
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10">
                <h4 className="font-black text-xs uppercase tracking-widest mb-3 text-purple-300">Ingest Methods</h4>
                <ul className="text-xs text-indigo-100 space-y-2 font-medium">
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400"></div>
                        MQTT 3.1.1 (Decentralized)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400"></div>
                        WebSocket (Sync Stream)
                    </li>
                    <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400"></div>
                        RESTful Node
                    </li>
                </ul>
                </div>
            </div>
          </div>
        </div>

        {/* Milk Quality Assessment Form */}
        <div className="glass backdrop-blur-2xl rounded-[3rem] p-10 border border-white/20 shadow-2xl animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <h3 className="text-2xl font-black text-white uppercase tracking-tight mb-8">Dairy Quality Checker</h3>
          
          <div className="grid lg:grid-cols-2 gap-12">
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">pH Level</label>
                  <input type="number" step="0.1" value={milkForm.ph} onChange={e => setMilkForm({...milkForm, ph: parseFloat(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-indigo-500 text-white font-bold" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Thermal (°C)</label>
                  <input type="number" step="0.1" value={milkForm.temperature} onChange={e => setMilkForm({...milkForm, temperature: parseFloat(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:ring-2 focus:ring-indigo-500 text-white font-bold" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Taste Spectrum</label>
                  <select value={milkForm.taste} onChange={e => setMilkForm({...milkForm, taste: parseInt(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-bold appearance-none cursor-pointer">
                    <option value={1} className="bg-slate-900">Optimal (1.0)</option>
                    <option value={0} className="bg-slate-900">Degraded (0.0)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Odor Threshold</label>
                  <select value={milkForm.odor} onChange={e => setMilkForm({...milkForm, odor: parseInt(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-bold appearance-none cursor-pointer">
                    <option value={1} className="bg-slate-900">Normal</option>
                    <option value={0} className="bg-slate-900">Foul</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Lipids</label>
                  <select value={milkForm.fat} onChange={e => setMilkForm({...milkForm, fat: parseInt(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-bold appearance-none cursor-pointer text-xs">
                    <option value={1} className="bg-slate-900">High</option>
                    <option value={0} className="bg-slate-900">Low</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Turbidity</label>
                  <select value={milkForm.turbidity} onChange={e => setMilkForm({...milkForm, turbidity: parseInt(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-bold appearance-none cursor-pointer text-xs">
                    <option value={0} className="bg-slate-900">Clear</option>
                    <option value={1} className="bg-slate-900">Cloudy</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Spectral</label>
                  <select value={milkForm.color} onChange={e => setMilkForm({...milkForm, color: parseInt(e.target.value)})} className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white font-bold appearance-none cursor-pointer text-xs">
                    <option value={1} className="bg-slate-900">White</option>
                    <option value={0} className="bg-slate-900">Off-white</option>
                  </select>
                </div>
              </div>
              
              <button 
                onClick={handleAnalyzeMilk} 
                disabled={analyzingMilk}
                className="w-full py-5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-2xl font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-xl shadow-indigo-500/20 text-sm"
              >
                {analyzingMilk ? 'Neural Processing...' : 'Execute ML Predictor'}
              </button>
            </div>

            <div className="bg-white/5 rounded-[2.5rem] p-8 border border-white/5 h-full flex flex-col justify-center relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform duration-1000">
                  <Droplets className="w-32 h-32" />
              </div>
              {milkResult ? (
                <div className="space-y-6 relative z-10">
                  <div className="text-center mb-8">
                    <p className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-2">Quality Prediction</p>
                    <p className={`text-5xl font-black capitalize tracking-tighter ${
                        milkResult.prediction === 'high' ? 'text-emerald-400' : milkResult.prediction === 'medium' ? 'text-amber-400' : 'text-rose-400'
                    }`}>
                      {milkResult.prediction} <span className="text-2xl opacity-60">Quality</span>
                    </p>
                  </div>
                  <div className="flex justify-between items-center bg-white/5 p-6 rounded-2xl border border-white/10">
                    <span className="text-xs font-black text-gray-400 uppercase tracking-widest">Risk Factor Score</span>
                    <span className="text-2xl font-black text-indigo-400">{milkResult.risk_score} <span className="text-xs opacity-50">/ 10</span></span>
                  </div>
                  <div className="bg-white/5 p-6 rounded-2xl border border-white/10">
                    <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Technical Insight</h4>
                    <p className="text-sm text-gray-200 font-medium leading-relaxed">{milkResult.description}</p>
                  </div>
                  {milkResult.reasons && milkResult.reasons.length > 0 && (
                    <div className="bg-rose-500/5 p-6 rounded-2xl border border-rose-500/10">
                      <h4 className="text-[10px] font-black text-rose-400 uppercase tracking-widest mb-3">Detected Degradation</h4>
                      <ul className="space-y-2">
                        {milkResult.reasons.map((r: string, i: number) => (
                            <li key={i} className="text-xs font-bold text-rose-200 flex items-center gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-rose-500"></div>
                                {r}
                            </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-gray-500 relative z-10">
                  <Droplets className="w-16 h-16 mx-auto mb-6 opacity-20" />
                  <p className="text-sm font-bold uppercase tracking-widest opacity-60">Awaiting Sample</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function SensorCard({ icon, title, value, status, color }: {
  icon: React.ReactNode;
  title: string;
  value: string;
  status: string;
  color: string;
}) {
  const statusColors = {
    normal: 'text-emerald-400 border-emerald-400/20 bg-emerald-400/5',
    warning: 'text-amber-400 border-amber-400/20 bg-amber-400/5',
    critical: 'text-rose-400 border-rose-400/20 bg-rose-400/5',
  };

  return (
    <div className="glass backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/10 transition-all duration-500 hover:scale-[1.05] group">
      <div className={`${color} text-white p-4 rounded-2xl inline-block mb-6 shadow-lg rotate-0 group-hover:rotate-6 transition-transform`}>
        {icon}
      </div>
      <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 leading-none">{title}</p>
      <p className="text-4xl font-black text-white mb-6 tracking-tighter">{value}</p>
      <span className={`px-4 py-1.5 rounded-xl border font-black text-[9px] uppercase tracking-widest ${statusColors[status as keyof typeof statusColors]}`}>
        {status}
      </span>
    </div>
  );
}

function getTemperatureStatus(temp: number): string {
  if (!temp) return 'normal';
  if (temp > 42) return 'critical';
  if (temp > 38) return 'warning';
  return 'normal';
}

function getHumidityStatus(humidity: number): string {
  if (!humidity) return 'normal';
  if (humidity < 30 || humidity > 80) return 'critical';
  if (humidity < 40 || humidity > 70) return 'warning';
  return 'normal';
}

function getGasStatus(gas: number): string {
  if (!gas) return 'normal';
  if (gas > 50) return 'critical';
  if (gas > 35) return 'warning';
  return 'normal';
}
