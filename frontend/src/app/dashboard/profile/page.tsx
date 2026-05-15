'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { User, Calendar, Mail, Hash, TrendingUp, Leaf, Trash2, Edit2, Save, X } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingPage } from '@/components/ui/LoadingPage';
import { useToast } from '@/hooks/useToast';
import { scanAPI, groceryAPI, wasteAPI, userAPI } from '@/lib/api';

interface UserData {
  id: number;
  name: string;
  email: string;
  age?: number;
  created_at: string;
}

interface UserStats {
  total_scans: number;
  total_groceries: number;
  total_waste_actions: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [user, setUser] = useState<UserData | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [age, setAge] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    
    fetchUserData(token);
  }, [router]);

  const fetchUserData = async (token: string) => {
    try {
      setLoading(true);
      
      // Fetch user profile from backend
      const userResponse = await userAPI.getProfile();
      const userData = userResponse.data;
      
      setUser(userData);
      setAge(userData.age || 0);
      
      // Fetch statistics
      await fetchStats();
    } catch (err: any) {
      console.error('Failed to fetch user data:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/auth/login');
      } else {
        showToast({
          type: 'error',
          message: 'Failed to load profile data',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const [scansResponse, groceriesResponse, wasteResponse] = await Promise.all([
        scanAPI.getHistory(),
        groceryAPI.getAll(),
        wasteAPI.getLogs(),
      ]);
      
      setStats({
        total_scans: scansResponse.data.length,
        total_groceries: groceriesResponse.data.length,
        total_waste_actions: wasteResponse.data.length,
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
      // Set default stats if fetch fails
      setStats({
        total_scans: 0,
        total_groceries: 0,
        total_waste_actions: 0,
      });
    }
  };

  const handleSave = async () => {
    if (!user) return;
    
    try {
      setSaving(true);
      
      await userAPI.updateProfile({ age });
      
      setUser({ ...user, age });
      setIsEditing(false);
      
      showToast({
        type: 'success',
        message: 'Profile updated successfully!',
      });
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      showToast({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to update profile',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setAge(user?.age || 0);
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return <LoadingPage message="Loading profile..." />;
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <div className="text-center">
            <p className="text-sm md:text-base text-gray-600">Failed to load profile data</p>
            <Button onClick={() => router.push('/dashboard')} variant="primary" className="mt-4 min-h-[44px]">
              Back to Dashboard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 md:px-8 py-4 md:py-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900 mb-2 min-h-[44px] min-w-[44px] flex items-center"
          >
            ← Back to Dashboard
          </button>
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <User className="w-6 h-6 md:w-8 md:h-8 text-green-600" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">User Profile</h1>
              <p className="text-sm md:text-base text-gray-600 mt-1">Manage your account information</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 md:px-8 py-6 md:py-8">
        {/* Profile Information Card */}
        <Card title="Profile Information" className="mb-6 md:mb-8">
          <div className="space-y-4 md:space-y-6">
            {/* Name - Read Only */}
            <div>
              <label className="block text-xs md:text-sm font-medium text-gray-700 mb-2">
                Name
              </label>
              <div className="flex items-center gap-3 px-3 md:px-4 py-2 bg-gray-50 rounded-lg min-h-[44px]">
                <User className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                <span className="text-sm md:text-base text-gray-900">{user.name}</span>
              </div>
            </div>

            {/* Email - Read Only */}
            <div>
              <label className="block text-xs md:text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="flex items-center gap-3 px-3 md:px-4 py-2 bg-gray-50 rounded-lg min-h-[44px]">
                <Mail className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                <span className="text-sm md:text-base text-gray-900">{user.email}</span>
              </div>
            </div>

            {/* Age - Editable */}
            <div>
              <label className="block text-xs md:text-sm font-medium text-gray-700 mb-2">
                Age
              </label>
              {isEditing ? (
                <Input
                  type="number"
                  value={age || ''}
                  onChange={(e) => setAge(parseInt(e.target.value) || 0)}
                  placeholder="Enter your age"
                  min="0"
                  max="150"
                  className="min-h-[44px]"
                />
              ) : (
                <div className="flex items-center gap-3 px-3 md:px-4 py-2 bg-gray-50 rounded-lg min-h-[44px]">
                  <Hash className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                  <span className="text-sm md:text-base text-gray-900">{user.age || 'Not set'}</span>
                </div>
              )}
            </div>

            {/* Created At - Read Only */}
            <div>
              <label className="block text-xs md:text-sm font-medium text-gray-700 mb-2">
                Account Created
              </label>
              <div className="flex items-center gap-3 px-3 md:px-4 py-2 bg-gray-50 rounded-lg min-h-[44px]">
                <Calendar className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                <span className="text-sm md:text-base text-gray-900">{formatDate(user.created_at)}</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              {!isEditing ? (
                <Button
                  onClick={() => setIsEditing(true)}
                  variant="primary"
                  className="flex items-center justify-center gap-2 min-h-[44px]"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Profile
                </Button>
              ) : (
                <>
                  <Button
                    onClick={handleSave}
                    variant="primary"
                    loading={saving}
                    className="flex items-center justify-center gap-2 min-h-[44px]"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </Button>
                  <Button
                    onClick={handleCancel}
                    variant="secondary"
                    disabled={saving}
                    className="flex items-center justify-center gap-2 min-h-[44px]"
                  >
                    <X className="w-4 h-4" />
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </div>
        </Card>

        {/* Account Statistics Card */}
        {stats && (
          <Card title="Account Statistics">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              <div className="flex items-center gap-3 md:gap-4">
                <div className="bg-blue-100 p-3 md:p-4 rounded-lg">
                  <TrendingUp className="w-6 h-6 md:w-8 md:h-8 text-blue-600" />
                </div>
                <div>
                  <p className="text-xs md:text-sm text-gray-600">Total Scans</p>
                  <p className="text-2xl md:text-3xl font-bold text-gray-900">{stats.total_scans}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 md:gap-4">
                <div className="bg-green-100 p-3 md:p-4 rounded-lg">
                  <Leaf className="w-6 h-6 md:w-8 md:h-8 text-green-600" />
                </div>
                <div>
                  <p className="text-xs md:text-sm text-gray-600">Total Groceries</p>
                  <p className="text-2xl md:text-3xl font-bold text-gray-900">{stats.total_groceries}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 md:gap-4">
                <div className="bg-orange-100 p-3 md:p-4 rounded-lg">
                  <Trash2 className="w-6 h-6 md:w-8 md:h-8 text-orange-600" />
                </div>
                <div>
                  <p className="text-xs md:text-sm text-gray-600">Waste Actions</p>
                  <p className="text-2xl md:text-3xl font-bold text-gray-900">{stats.total_waste_actions}</p>
                </div>
              </div>
            </div>
          </Card>
        )}
      </main>
    </div>
  );
}
