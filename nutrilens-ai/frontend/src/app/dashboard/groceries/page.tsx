'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { groceryAPI } from '@/lib/api';
import { Plus, Edit2, Trash2, Leaf, Package, ArrowLeft, ShieldCheck, Box } from 'lucide-react';

export default function GroceriesPage() {
  const router = useRouter();
  const [groceries, setGroceries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingGrocery, setEditingGrocery] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    fetchGroceries();
  }, [router]);

  const fetchGroceries = async () => {
    try {
      const response = await groceryAPI.getAll();
      setGroceries(response.data);
    } catch (error) {
      console.error('Failed to fetch groceries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this asset?')) return;

    try {
      await groceryAPI.delete(id);
      setGroceries(groceries.filter(g => g.id !== id));
    } catch (error) {
      console.error('Failed to delete grocery:', error);
      alert('Failed to delete item');
    }
  };

  const getFreshnessColor = (status: string) => {
    switch (status) {
      case 'fresh': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'slightly_aged': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'rotten': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-gray-400 bg-white/5 border-white/10';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-emerald-500 mx-auto mb-6"></div>
          <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Loading your pantry...</p>
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
              <h1 className="text-4xl font-black text-white tracking-tight">Smart <span className="text-emerald-400">Pantry</span></h1>
              <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest font-bold opacity-60">Manage your kitchen essentials</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-8 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl font-bold text-sm uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-emerald-500/20 flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Item
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {groceries.length === 0 ? (
          <div className="glass backdrop-blur-xl rounded-[2.5rem] p-20 text-center border border-white/10 shadow-2xl animate-fade-in-up">
            <Package className="w-20 h-20 text-white/10 mx-auto mb-6" />
            <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">Vault Empty</h3>
            <p className="text-gray-500 mb-8 text-sm font-bold uppercase tracking-tighter">No biological assets registered in the database.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-10 py-4 bg-white/5 border border-white/20 text-white rounded-[1.5rem] font-black uppercase tracking-widest hover:bg-white/10 transition-all"
            >
              Add First Asset
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {groceries.map((grocery, idx) => (
              <div 
                key={grocery.id} 
                className="glass backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/10 hover:border-white/30 transition-all duration-500 group animate-fade-in-up"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="flex items-start justify-between mb-8">
                  <div className="flex items-center gap-4">
                    <div className="bg-emerald-500/10 p-4 rounded-2xl border border-emerald-500/20 group-hover:scale-110 transition-transform">
                      <Leaf className="w-7 h-7 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-black text-white tracking-tighter capitalize leading-none mb-1">{grocery.food_name}</h3>
                      {grocery.category && (
                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">{grocery.category}</p>
                      )}
                    </div>
                  </div>
                  <div className={`px-4 py-1.5 rounded-xl border-2 font-black text-[10px] uppercase tracking-widest ${getFreshnessColor(grocery.freshness_status)}`}>
                    {grocery.freshness_status.replace('_', ' ')}
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5">
                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none">Quantity</span>
                    <span className="text-lg font-black text-white leading-none">{grocery.quantity}</span>
                  </div>

                  <div className="flex items-center justify-between px-4">
                    <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Registered</span>
                    <span className="text-xs font-bold text-gray-400">{new Date(grocery.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex gap-4 pt-6 border-t border-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => setEditingGrocery(grocery)}
                    className="flex-1 px-4 py-3 bg-white/5 border border-white/10 text-white rounded-xl font-bold uppercase tracking-widest text-[10px] hover:bg-white/10 transition-all flex items-center justify-center gap-2"
                  >
                    <Edit2 className="w-3 h-3" />
                    Adjust
                  </button>
                  <button
                    onClick={() => handleDelete(grocery.id)}
                    className="px-4 py-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl font-bold uppercase tracking-widest text-[10px] hover:bg-rose-500 hover:text-white transition-all"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Add/Edit Modal */}
      {(showAddModal || editingGrocery) && (
        <GroceryModal
          grocery={editingGrocery}
          onClose={() => {
            setShowAddModal(false);
            setEditingGrocery(null);
          }}
          onSave={() => {
            fetchGroceries();
            setShowAddModal(false);
            setEditingGrocery(null);
          }}
        />
      )}
    </div>
  );
}

function GroceryModal({ grocery, onClose, onSave }: any) {
  const [formData, setFormData] = useState({
    food_name: grocery?.food_name || '',
    category: grocery?.category || '',
    quantity: grocery?.quantity || 1,
    freshness_status: grocery?.freshness_status || 'fresh',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (grocery) {
        await groceryAPI.update(grocery.id, formData);
      } else {
        await groceryAPI.create(formData);
      }
      onSave();
    } catch (error) {
      console.error('Failed to save grocery:', error);
      alert('Failed to save grocery');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-2xl flex items-center justify-center p-4 z-[100] animate-in fade-in zoom-in duration-300">
      <div className="glass backdrop-blur-3xl rounded-[3rem] border border-white/20 shadow-2xl max-w-lg w-full p-10 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-10 opacity-5">
            <Box className="w-40 h-40" />
        </div>
        
        <div className="relative z-10">
            <div className="flex items-center gap-3 mb-8">
                <div className="bg-emerald-500/20 p-2 rounded-xl">
                    <ShieldCheck className="w-6 h-6 text-emerald-400" />
                </div>
                <h2 className="text-3xl font-black text-white tracking-tighter uppercase">
                {grocery ? 'Edit Protocol' : 'New Registration'}
                </h2>
            </div>
    
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">
                  Asset Descriptor
                </label>
                <input
                  type="text"
                  required
                  value={formData.food_name}
                  onChange={(e) => setFormData({ ...formData, food_name: e.target.value })}
                  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white placeholder-gray-600 transition-all font-bold"
                  placeholder="e.g., Avocado Cluster"
                />
              </div>
    
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">
                    Category
                    </label>
                    <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white transition-all font-bold appearance-none cursor-pointer"
                    >
                    <option value="" className="bg-slate-900">Selective</option>
                    <option value="Fruit" className="bg-slate-900">Fruit</option>
                    <option value="Vegetable" className="bg-slate-900">Vegetable</option>
                    <option value="Meat" className="bg-slate-900">Meat</option>
                    <option value="Dairy" className="bg-slate-900">Dairy</option>
                    <option value="Grain" className="bg-slate-900">Grain</option>
                    <option value="Other" className="bg-slate-900">Other</option>
                    </select>
                </div>
    
                <div className="space-y-2">
                    <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">
                    Density
                    </label>
                    <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                    className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white transition-all font-bold"
                    />
                </div>
              </div>
    
              <div className="space-y-2">
                <label className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em] ml-1">
                  Biological State
                </label>
                <select
                  value={formData.freshness_status}
                  onChange={(e) => setFormData({ ...formData, freshness_status: e.target.value })}
                  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-white transition-all font-bold appearance-none cursor-pointer"
                >
                  <option value="fresh" className="bg-slate-900">Fresh / Active</option>
                  <option value="slightly_aged" className="bg-slate-900">Aged / Maturing</option>
                  <option value="rotten" className="bg-slate-900">Rotten / Expired</option>
                  <option value="unknown" className="bg-slate-900">Unknown / Null</option>
                </select>
              </div>
    
              <div className="flex gap-4 pt-6">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-6 py-4 border border-white/10 text-gray-400 rounded-2xl font-bold uppercase tracking-widest text-xs hover:text-white hover:bg-white/5 transition-all"
                >
                  Abort
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-[2] px-6 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs hover:scale-105 active:scale-95 transition-all shadow-xl shadow-emerald-500/20"
                >
                  {loading ? 'Encrypting...' : 'Upload Data'}
                </button>
              </div>
            </form>
        </div>
      </div>
    </div>
  );
}
