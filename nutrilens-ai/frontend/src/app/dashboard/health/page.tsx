'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { healthAPI } from '@/lib/api';
import { Heart, CheckCircle, XCircle, Lightbulb, Apple, ArrowLeft } from 'lucide-react';

export default function HealthPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  const [formData, setFormData] = useState({
    diabetes: false,
    high_bp: false,
    cholesterol: false,
    surgery_recovery: false,
    weight_loss: false,
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    fetchProfile();
  }, [router]);

  const fetchProfile = async () => {
    try {
      const profileRes = await healthAPI.getProfile();
      setProfile(profileRes.data);
      setFormData({
        diabetes: profileRes.data.diabetes,
        high_bp: profileRes.data.high_bp,
        cholesterol: profileRes.data.cholesterol,
        surgery_recovery: profileRes.data.surgery_recovery,
        weight_loss: profileRes.data.weight_loss,
      });

      const recsRes = await healthAPI.getRecommendations();
      setRecommendations(recsRes.data);
    } catch (error: any) {
      if (error.response?.status === 404) {
        setEditing(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      if (profile) {
        await healthAPI.updateProfile(formData);
      } else {
        await healthAPI.createProfile(formData);
      }
      await fetchProfile();
      setEditing(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
      alert('Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !editing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-rose-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Tailoring your profile...</p>
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight">Health <span className="text-rose-400">Insights</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Personalized dietary goals</p>
            </div>
            {profile && !editing && (
              <button
                onClick={() => setEditing(true)}
                className="px-8 py-3 bg-gradient-to-r from-rose-500 to-pink-600 text-white rounded-2xl font-bold text-sm uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-rose-500/20"
              >
                Edit Matrix
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Health Conditions */}
          <div className="glass backdrop-blur-2xl rounded-[2.5rem] p-8 md:p-10 border border-white/20 shadow-2xl animate-fade-in-up">
            <div className="flex items-center gap-4 mb-10">
              <div className="bg-rose-500/20 p-3 rounded-2xl">
                <Heart className="w-8 h-8 text-rose-400" />
              </div>
              <h2 className="text-3xl font-black text-white tracking-tight uppercase">Base Profiles</h2>
            </div>
 
            <div className="space-y-6">
              <ConditionToggle
                label="Diabetes"
                description="Optimize for Glycemic Index management"
                checked={formData.diabetes}
                onChange={(checked) => setFormData({ ...formData, diabetes: checked })}
                disabled={!editing}
              />
 
              <ConditionToggle
                label="Hypertension"
                description="Strict sodium & fluid telemetry"
                checked={formData.high_bp}
                onChange={(checked) => setFormData({ ...formData, high_bp: checked })}
                disabled={!editing}
              />
 
              <ConditionToggle
                label="Hyperlipidemia"
                description="Saturated fat & lipid tracking"
                checked={formData.cholesterol}
                onChange={(checked) => setFormData({ ...formData, cholesterol: checked })}
                disabled={!editing}
              />
 
              <ConditionToggle
                label="Bio-Recovery"
                description="Surgery & inflammatory support"
                checked={formData.surgery_recovery}
                onChange={(checked) => setFormData({ ...formData, surgery_recovery: checked })}
                disabled={!editing}
              />
 
              <ConditionToggle
                label="Metabolic Cut"
                description="Caloric deficit & macro optimization"
                checked={formData.weight_loss}
                onChange={(checked) => setFormData({ ...formData, weight_loss: checked })}
                disabled={!editing}
              />
            </div>
 
            {editing && (
              <div className="flex gap-4 mt-12 pt-10 border-t border-white/10">
                <button
                  onClick={() => {
                    setEditing(false);
                    if (profile) {
                      setFormData({
                        diabetes: profile.diabetes,
                        high_bp: profile.high_bp,
                        cholesterol: profile.cholesterol,
                        surgery_recovery: profile.surgery_recovery,
                        weight_loss: profile.weight_loss,
                      });
                    }
                  }}
                  className="flex-1 px-6 py-4 border border-white/20 text-gray-400 rounded-2xl font-bold uppercase tracking-widest hover:text-white hover:bg-white/5 transition-all text-sm"
                >
                  Terminate
                </button>
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="flex-1 px-6 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl shadow-emerald-500/20 text-sm"
                >
                  {loading ? 'Encrypting...' : 'Upload Profile'}
                </button>
              </div>
            )}
          </div>
 
          {/* Recommendations */}
          <div className="space-y-8">
            {recommendations && (
              <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                {/* Recommended Foods */}
                {recommendations.recommended_foods.length > 0 && (
                  <div className="glass backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/10 shadow-2xl mb-6 hover:border-emerald-500/30 transition-colors group">
                    <div className="flex items-center gap-3 mb-6">
                      <CheckCircle className="w-6 h-6 text-emerald-400" />
                      <h2 className="text-xl font-black text-white uppercase tracking-widest">Optimized Assets</h2>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {recommendations.recommended_foods.map((food: string, index: number) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-xl text-xs font-black border border-emerald-500/20 uppercase tracking-tighter hover:bg-emerald-500/20 transition-colors"
                        >
                          {food}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
 
                {/* Foods to Avoid */}
                {recommendations.foods_to_avoid.length > 0 && (
                  <div className="glass backdrop-blur-xl rounded-[2.5rem] p-8 border border-white/10 shadow-2xl mb-6 hover:border-rose-500/30 transition-colors">
                    <div className="flex items-center gap-3 mb-6">
                      <XCircle className="w-6 h-6 text-rose-400" />
                      <h2 className="text-xl font-black text-white uppercase tracking-widest">Risk Factor Assets</h2>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {recommendations.foods_to_avoid.map((food: string, index: number) => (
                        <span
                          key={index}
                          className="px-4 py-2 bg-rose-500/10 text-rose-400 rounded-xl text-xs font-black border border-rose-500/20 uppercase tracking-tighter hover:bg-rose-500/20 transition-colors"
                        >
                          {food}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Info Card */}
                <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-[2.5rem] p-8 text-white shadow-2xl shadow-indigo-500/20 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-10">
                    <Lightbulb className="w-32 h-32" />
                  </div>
                  <h3 className="text-2xl font-black mb-4 uppercase tracking-tight relative z-10">Neural Nutrition</h3>
                  <p className="text-indigo-100 text-sm font-medium leading-relaxed relative z-10">
                    Your profile informs our <span className="font-black text-white">Hybrid Risk Logic</span>. Every scan across the Bio-Scanner and Smart Box modules is now automatically evaluated against your metabolic parameters.
                  </p>
                </div>
              </div>
            )}
 
            {!profile && !editing && (
              <div className="glass backdrop-blur-xl rounded-[2.5rem] p-16 text-center border border-white/10 shadow-2xl">
                <Heart className="w-20 h-20 text-white/10 mx-auto mb-6 animate-pulse" />
                <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">Profile Offline</h3>
                <p className="text-gray-500 mb-8 text-sm font-bold uppercase tracking-tighter">Initialize your biological parameters for full AI heuristics.</p>
                <button
                  onClick={() => setEditing(true)}
                  className="px-8 py-4 bg-gradient-to-r from-rose-500 to-pink-600 text-white rounded-[1.5rem] font-black uppercase tracking-widest hover:scale-110 active:scale-95 transition-all shadow-2xl shadow-rose-500/40"
                >
                  Establish Profile
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

interface ConditionToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled: boolean;
}

function ConditionToggle({ label, description, checked, onChange, disabled }: ConditionToggleProps) {
  return (
    <div className={`flex items-center justify-between p-6 rounded-[1.5rem] border-2 transition-all duration-300 ${
      checked ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-white/5 border-white/10 hover:border-white/20'
    } ${disabled ? 'opacity-80' : 'cursor-pointer'}`}
    onClick={() => !disabled && onChange(!checked)}>
      <div className="flex-1 pr-4">
        <p className={`font-black uppercase tracking-tight text-lg mb-0.5 ${checked ? 'text-emerald-400' : 'text-white'}`}>{label}</p>
        <p className="text-xs text-gray-400 font-medium tracking-tight leading-snug">{description}</p>
      </div>
      <div className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-300 ${
        checked ? 'bg-emerald-500' : 'bg-white/10'
      }`}>
        <span
          className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${
            checked ? 'translate-x-7' : 'translate-x-1'
          }`}
        />
      </div>
    </div>
  );
}
