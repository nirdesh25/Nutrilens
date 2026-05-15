'use client';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-green-600 mb-4">Test Page Works!</h1>
        <p className="text-gray-700 mb-4">
          If you can see this page, the Next.js routing is working correctly.
        </p>
        <div className="space-y-2">
          <a href="/" className="block px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-center">
            Go to Home
          </a>
          <a href="/auth/login" className="block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-center">
            Go to Login
          </a>
          <a href="/dashboard" className="block px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 text-center">
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
