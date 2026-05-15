'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Settings as SettingsIcon, Sun, Moon, Monitor, Globe, Bell, BellOff, LogOut, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';

type Theme = 'light' | 'dark' | 'system';
type Language = 'en' | 'es' | 'fr';

export default function SettingsPage() {
  const router = useRouter();
  const [theme, setTheme] = useState<Theme>('system');
  const [language, setLanguage] = useState<Language>('en');
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    
    // Load settings from localStorage
    const savedTheme = localStorage.getItem('theme') as Theme;
    const savedLanguage = localStorage.getItem('language') as Language;
    const savedEmailNotifications = localStorage.getItem('emailNotifications');
    const savedPushNotifications = localStorage.getItem('pushNotifications');
    
    if (savedTheme) setTheme(savedTheme);
    if (savedLanguage) setLanguage(savedLanguage);
    if (savedEmailNotifications !== null) setEmailNotifications(savedEmailNotifications === 'true');
    if (savedPushNotifications !== null) setPushNotifications(savedPushNotifications === 'true');
  }, [router]);

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLanguage = e.target.value as Language;
    setLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
  };

  const handleEmailNotificationsToggle = () => {
    const newValue = !emailNotifications;
    setEmailNotifications(newValue);
    localStorage.setItem('emailNotifications', String(newValue));
  };

  const handlePushNotificationsToggle = () => {
    const newValue = !pushNotifications;
    setPushNotifications(newValue);
    localStorage.setItem('pushNotifications', String(newValue));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  const handleDeleteAccount = () => {
    // In a real implementation, this would call an API endpoint
    // For now, we'll just remove the token and redirect
    localStorage.removeItem('token');
    localStorage.clear();
    router.push('/');
  };

  const getThemeIcon = (themeType: Theme) => {
    switch (themeType) {
      case 'light':
        return <Sun className="w-5 h-5" />;
      case 'dark':
        return <Moon className="w-5 h-5" />;
      case 'system':
        return <Monitor className="w-5 h-5" />;
    }
  };

  const getLanguageName = (lang: Language) => {
    switch (lang) {
      case 'en':
        return 'English';
      case 'es':
        return 'Spanish';
      case 'fr':
        return 'French';
    }
  };

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
              <SettingsIcon className="w-6 h-6 md:w-8 md:h-8 text-green-600" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Settings</h1>
              <p className="text-sm md:text-base text-gray-600 mt-1">Manage your preferences and account</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 md:px-8 py-6 md:py-8 space-y-4 md:space-y-6">
        {/* Preferences Section */}
        <Card title="Preferences">
          <div className="space-y-4 md:space-y-6">
            {/* Theme Preference */}
            <div>
              <label className="block text-xs md:text-sm font-medium text-gray-700 mb-3">
                Theme
              </label>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => handleThemeChange('light')}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 md:px-4 py-3 rounded-lg border-2 transition min-h-[44px] ${
                    theme === 'light'
                      ? 'border-green-600 bg-green-50 text-green-700'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Sun className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="text-sm md:text-base font-medium">Light</span>
                </button>
                <button
                  onClick={() => handleThemeChange('dark')}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 md:px-4 py-3 rounded-lg border-2 transition min-h-[44px] ${
                    theme === 'dark'
                      ? 'border-green-600 bg-green-50 text-green-700'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Moon className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="text-sm md:text-base font-medium">Dark</span>
                </button>
                <button
                  onClick={() => handleThemeChange('system')}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 md:px-4 py-3 rounded-lg border-2 transition min-h-[44px] ${
                    theme === 'system'
                      ? 'border-green-600 bg-green-50 text-green-700'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Monitor className="w-4 h-4 md:w-5 md:h-5" />
                  <span className="text-sm md:text-base font-medium">System</span>
                </button>
              </div>
            </div>

            {/* Language Preference */}
            <div>
              <label htmlFor="language" className="block text-xs md:text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                <select
                  id="language"
                  value={language}
                  onChange={handleLanguageChange}
                  className="w-full pl-9 md:pl-10 pr-3 md:pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white text-gray-900 text-sm md:text-base min-h-[44px]"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </div>
            </div>
          </div>
        </Card>

        {/* Notifications Section */}
        <Card title="Notifications">
          <div className="space-y-4">
            {/* Email Notifications */}
            <div className="flex items-center justify-between gap-4 min-h-[44px]">
              <div className="flex items-center gap-3">
                {emailNotifications ? (
                  <Bell className="w-4 h-4 md:w-5 md:h-5 text-green-600 flex-shrink-0" />
                ) : (
                  <BellOff className="w-4 h-4 md:w-5 md:h-5 text-gray-400 flex-shrink-0" />
                )}
                <div>
                  <p className="text-sm md:text-base font-medium text-gray-900">Email Notifications</p>
                  <p className="text-xs md:text-sm text-gray-600">Receive updates via email</p>
                </div>
              </div>
              <button
                onClick={handleEmailNotificationsToggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition flex-shrink-0 ${
                  emailNotifications ? 'bg-green-600' : 'bg-gray-300'
                }`}
                aria-label="Toggle email notifications"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    emailNotifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Push Notifications */}
            <div className="flex items-center justify-between gap-4 min-h-[44px]">
              <div className="flex items-center gap-3">
                {pushNotifications ? (
                  <Bell className="w-4 h-4 md:w-5 md:h-5 text-green-600 flex-shrink-0" />
                ) : (
                  <BellOff className="w-4 h-4 md:w-5 md:h-5 text-gray-400 flex-shrink-0" />
                )}
                <div>
                  <p className="text-sm md:text-base font-medium text-gray-900">Push Notifications</p>
                  <p className="text-xs md:text-sm text-gray-600">Receive push notifications</p>
                </div>
              </div>
              <button
                onClick={handlePushNotificationsToggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition flex-shrink-0 ${
                  pushNotifications ? 'bg-green-600' : 'bg-gray-300'
                }`}
                aria-label="Toggle push notifications"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    pushNotifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </Card>

        {/* Account Section */}
        <Card title="Account">
          <div className="space-y-4">
            {/* Logout Button */}
            <div>
              <Button
                onClick={handleLogout}
                variant="secondary"
                className="w-full flex items-center justify-center gap-2 min-h-[44px]"
              >
                <LogOut className="w-4 h-4 md:w-5 md:h-5" />
                Logout
              </Button>
              <p className="text-xs md:text-sm text-gray-600 mt-2">
                Sign out of your account
              </p>
            </div>

            {/* Delete Account Button */}
            <div className="pt-4 border-t border-gray-200">
              <Button
                onClick={() => setShowDeleteModal(true)}
                variant="danger"
                className="w-full flex items-center justify-center gap-2 min-h-[44px]"
              >
                <Trash2 className="w-4 h-4 md:w-5 md:h-5" />
                Delete Account
              </Button>
              <p className="text-xs md:text-sm text-gray-600 mt-2">
                Permanently delete your account and all data
              </p>
            </div>
          </div>
        </Card>
      </main>

      {/* Delete Account Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Account"
        footer={
          <div className="flex flex-col sm:flex-row gap-3 w-full">
            <Button
              onClick={() => setShowDeleteModal(false)}
              variant="secondary"
              className="flex-1 min-h-[44px]"
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteAccount}
              variant="danger"
              className="flex-1 min-h-[44px]"
            >
              Delete Account
            </Button>
          </div>
        }
      >
        <p className="text-sm md:text-base text-gray-700">
          Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently removed.
        </p>
      </Modal>
    </div>
  );
}
