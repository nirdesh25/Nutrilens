'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { sensorAPI } from '@/lib/api';
import { api } from '@/lib/api';
import { Search, Apple, Zap, Droplets, Info } from 'lucide-react';

interface NutritionData {
  id: number;
  name: string;
  category: string;
  calories: number;
  protein: number;
  fat: number;
  carbs: number;
  fiber: number;
  sugar: number;
  sodium: number;
  gi_index: number;
}

interface SearchResult {
  name: string;
  category: string;
  calories: number;
}

export default function NutritionPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selected, setSelected] = useState<NutritionData | null>(null);
  const [searching, setSearching] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setSearching(true);
    setSearched(true);
    setSelected(null);
    try {
      const res = await api.get(`/api/nutrition/search?q=${encodeURIComponent(query)}`);
      setSearchResults(res.data.results);
    } catch (e) {
      console.error(e);
    } finally {
      setSearching(false);
    }
  }, [query]);

  const handleSelect = async (name: string) => {
    setLoadingDetail(true);
    try {
      const res = await api.get(`/api/nutrition/food/${encodeURIComponent(name)}`);
      setSelected(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getGILabel = (gi: number) => {
    if (!gi) return { label: 'N/A', color: 'text-gray-500' };
    if (gi <= 55) return { label: 'Low GI', color: 'text-green-600' };
    if (gi <= 69) return { label: 'Medium GI', color: 'text-orange-500' };
    return { label: 'High GI', color: 'text-red-600' };
  };

  const macroBar = (value: number, max: number, color: string) => (
    <div className="w-full bg-gray-100 rounded-full h-2 mt-1">
      <div
        className={`h-2 rounded-full ${color}`}
        style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900 mb-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Nutrition Lookup</h1>
          <p className="text-gray-600 mt-1">
            Search foods to get calories, macros, GI index and more
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Search bar */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                id="nutrition-search-input"
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="Search food (e.g., Apple, Paneer, Rice…)"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            <button
              id="nutrition-search-btn"
              onClick={handleSearch}
              disabled={searching || !query.trim()}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium transition"
            >
              {searching ? 'Searching…' : 'Search'}
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Results list */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Results</h2>

            {!searched && (
              <div className="text-center py-12">
                <Apple className="w-16 h-16 text-gray-200 mx-auto mb-4" />
                <p className="text-gray-500">Search for a food to get started</p>
              </div>
            )}

            {searching && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto" />
              </div>
            )}

            {searched && !searching && searchResults.length === 0 && (
              <div className="text-center py-12">
                <Info className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No results found for "{query}"</p>
              </div>
            )}

            <div className="space-y-2">
              {searchResults.map((item, i) => (
                <button
                  key={i}
                  onClick={() => handleSelect(item.name)}
                  className={`w-full text-left flex items-center justify-between p-4 rounded-lg border transition hover:border-green-400 hover:bg-green-50 ${
                    selected?.name === item.name ? 'border-green-500 bg-green-50' : 'border-gray-200'
                  }`}
                >
                  <div>
                    <p className="font-semibold text-gray-900">{item.name}</p>
                    <p className="text-sm text-gray-500 capitalize">{item.category}</p>
                  </div>
                  <span className="text-sm font-bold text-green-700 bg-green-100 px-3 py-1 rounded-full">
                    {item.calories} kcal
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Detail panel */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Nutritional Detail</h2>

            {loadingDetail && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mx-auto" />
              </div>
            )}

            {!loadingDetail && !selected && (
              <div className="text-center py-12">
                <Zap className="w-16 h-16 text-gray-200 mx-auto mb-4" />
                <p className="text-gray-500">Select a food item to see its nutritional breakdown</p>
              </div>
            )}

            {!loadingDetail && selected && (
              <div className="space-y-6">
                {/* Header */}
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-1">
                    {selected.category}
                  </p>
                  <h3 className="text-2xl font-bold text-gray-900">{selected.name}</h3>
                </div>

                {/* Calories hero */}
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-5 text-white text-center">
                  <p className="text-sm font-medium opacity-80 mb-1">Calories (per 100g)</p>
                  <p className="text-5xl font-black">{selected.calories}</p>
                  <p className="text-sm opacity-80 mt-1">kcal</p>
                </div>

                {/* Macros */}
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Protein', value: selected.protein, unit: 'g', max: 40, color: 'bg-blue-500' },
                    { label: 'Fat', value: selected.fat, unit: 'g', max: 40, color: 'bg-yellow-400' },
                    { label: 'Carbs', value: selected.carbs, unit: 'g', max: 80, color: 'bg-orange-400' },
                    { label: 'Fiber', value: selected.fiber, unit: 'g', max: 15, color: 'bg-green-500' },
                  ].map(m => (
                    <div key={m.label} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">{m.label}</span>
                        <span className="text-sm font-bold text-gray-900">{m.value}{m.unit}</span>
                      </div>
                      {macroBar(m.value, m.max, m.color)}
                    </div>
                  ))}
                </div>

                {/* Other nutrients */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center bg-gray-50 rounded-lg p-3">
                    <Droplets className="w-5 h-5 text-blue-400 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">Sugar</p>
                    <p className="font-bold text-gray-900">{selected.sugar}g</p>
                  </div>
                  <div className="text-center bg-gray-50 rounded-lg p-3">
                    <Info className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">Sodium</p>
                    <p className="font-bold text-gray-900">{selected.sodium}mg</p>
                  </div>
                  <div className="text-center bg-gray-50 rounded-lg p-3">
                    <Zap className="w-5 h-5 text-orange-400 mx-auto mb-1" />
                    <p className="text-xs text-gray-500">GI Index</p>
                    <p className={`font-bold ${getGILabel(selected.gi_index).color}`}>
                      {selected.gi_index || '—'}
                    </p>
                  </div>
                </div>

                {/* GI badge */}
                {selected.gi_index > 0 && (
                  <div className={`text-center text-sm font-semibold py-2 rounded-lg ${
                    selected.gi_index <= 55
                      ? 'bg-green-100 text-green-700'
                      : selected.gi_index <= 69
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {getGILabel(selected.gi_index).label}
                    {selected.gi_index <= 55 && ' — Suitable for diabetics'}
                    {selected.gi_index > 69 && ' — Limit for diabetics'}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
