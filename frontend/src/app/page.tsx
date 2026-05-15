'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useState } from 'react';
import { ArrowRight, Sparkles, Apple, Carrot, Fish, Milk, Beef, Cherry, Banana, Grape, Salad, Pizza, Cookie, IceCream, Coffee, Sandwich } from 'lucide-react';

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden relative">
      {/* Animated background gradient */}
      <div className="fixed inset-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 animate-gradient"></div>
      </div>

      {/* Decorative Food Icons - Top Border */}
      <div className="absolute top-0 left-0 right-0 h-24 flex items-center justify-around px-8 opacity-20">
        <Apple className="w-8 h-8 text-red-400 animate-float" />
        <Carrot className="w-8 h-8 text-orange-400 animate-float" style={{ animationDelay: '0.5s' }} />
        <Fish className="w-8 h-8 text-blue-400 animate-float" style={{ animationDelay: '1s' }} />
        <Cherry className="w-8 h-8 text-red-500 animate-float" style={{ animationDelay: '1.5s' }} />
        <Banana className="w-8 h-8 text-yellow-400 animate-float" style={{ animationDelay: '2s' }} />
        <Grape className="w-8 h-8 text-purple-400 animate-float" style={{ animationDelay: '2.5s' }} />
        <Salad className="w-8 h-8 text-green-400 animate-float" style={{ animationDelay: '3s' }} />
      </div>

      {/* Decorative Food Icons - Left Border */}
      <div className="absolute left-0 top-1/4 bottom-1/4 w-24 flex flex-col items-center justify-around py-8 opacity-20">
        <Pizza className="w-8 h-8 text-yellow-500 animate-float" />
        <Apple className="w-8 h-8 text-green-400 animate-float" style={{ animationDelay: '0.7s' }} />
        <IceCream className="w-8 h-8 text-pink-400 animate-float" style={{ animationDelay: '1.4s' }} />
        <Coffee className="w-8 h-8 text-amber-600 animate-float" style={{ animationDelay: '2.1s' }} />
      </div>

      {/* Decorative Food Icons - Right Border */}
      <div className="absolute right-0 top-1/4 bottom-1/4 w-24 flex flex-col items-center justify-around py-8 opacity-20">
        <Sandwich className="w-8 h-8 text-orange-400 animate-float" style={{ animationDelay: '0.3s' }} />
        <Milk className="w-8 h-8 text-blue-200 animate-float" style={{ animationDelay: '1s' }} />
        <Cookie className="w-8 h-8 text-amber-500 animate-float" style={{ animationDelay: '1.7s' }} />
        <Beef className="w-8 h-8 text-red-600 animate-float" style={{ animationDelay: '2.4s' }} />
      </div>

      {/* Decorative Food Icons - Bottom Border */}
      <div className="absolute bottom-0 left-0 right-0 h-24 flex items-center justify-around px-8 opacity-20">
        <Milk className="w-8 h-8 text-blue-300 animate-float" style={{ animationDelay: '0.4s' }} />
        <Beef className="w-8 h-8 text-red-500 animate-float" style={{ animationDelay: '0.9s' }} />
        <Cookie className="w-8 h-8 text-yellow-600 animate-float" style={{ animationDelay: '1.4s' }} />
        <IceCream className="w-8 h-8 text-pink-300 animate-float" style={{ animationDelay: '1.9s' }} />
        <Coffee className="w-8 h-8 text-brown-500 animate-float" style={{ animationDelay: '2.4s' }} />
        <Sandwich className="w-8 h-8 text-yellow-500 animate-float" style={{ animationDelay: '2.9s' }} />
        <Pizza className="w-8 h-8 text-red-400 animate-float" style={{ animationDelay: '3.4s' }} />
      </div>

      {/* Hero Section - Centered */}
      <div className="relative container mx-auto px-4 py-20 min-h-screen flex items-center justify-center">
        <div className={`text-center max-w-4xl transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="flex items-center justify-center mb-8 animate-float">
            <div className="relative">
              <div className="absolute inset-0 bg-green-500 blur-3xl opacity-50 animate-pulse-glow"></div>
              <Image 
                src="/logo.png" 
                alt="NutriLens AI Logo" 
                width={140} 
                height={140} 
                className="w-32 h-32 sm:w-36 sm:h-36 relative z-10 drop-shadow-2xl" 
              />
            </div>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 bg-clip-text text-transparent animate-gradient">
            NutriLens AI
          </h1>
          
          <div className="flex items-center justify-center gap-2 mb-8">
            <Sparkles className="w-6 h-6 text-yellow-400 animate-pulse" />
            <p className="text-2xl md:text-4xl text-gray-300 font-light">
              AI-Powered Food Intelligence Platform
            </p>
            <Sparkles className="w-6 h-6 text-yellow-400 animate-pulse" />
          </div>
          
          <p className="text-lg md:text-2xl text-gray-400 max-w-3xl mx-auto mb-12 leading-relaxed">
            Detect food freshness, get health-aware recommendations, and reduce food waste with cutting-edge AI technology.
          </p>
          
          <div className="flex gap-6 justify-center flex-wrap">
            <Link
              href="/auth/register"
              className="group relative px-10 py-5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl font-semibold text-lg overflow-hidden transition-all duration-300 hover:scale-110 hover:shadow-2xl hover:shadow-green-500/50"
            >
              <span className="relative z-10 flex items-center gap-2">
                Get Started
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </Link>
            
            <Link
              href="/auth/login"
              className="group px-10 py-5 glass text-white rounded-2xl font-semibold text-lg transition-all duration-300 hover:scale-110 hover:shadow-xl backdrop-blur-xl border-2 border-white/20 hover:border-white/40"
            >
              <span className="flex items-center gap-2">
                Sign In
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
              </span>
            </Link>
          </div>

          {/* Feature Highlights - Minimal Text */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureHighlight
              icon={<Apple className="w-12 h-12" />}
              title="Food Freshness"
              gradient="from-red-500 to-pink-500"
            />
            <FeatureHighlight
              icon={<Salad className="w-12 h-12" />}
              title="Health Tracking"
              gradient="from-green-500 to-emerald-500"
            />
            <FeatureHighlight
              icon={<Sparkles className="w-12 h-12" />}
              title="AI Powered"
              gradient="from-blue-500 to-purple-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureHighlight({ icon, title, gradient }: {
  icon: React.ReactNode;
  title: string;
  gradient: string;
}) {
  return (
    <div className="group flex flex-col items-center gap-4 p-6 glass backdrop-blur-xl rounded-3xl border border-white/10 hover:border-white/30 transition-all duration-500 hover:scale-110">
      <div className={`bg-gradient-to-br ${gradient} text-white p-4 rounded-2xl group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300`}>
        {icon}
      </div>
      <h3 className="text-xl font-bold text-white">{title}</h3>
    </div>
  );
}
