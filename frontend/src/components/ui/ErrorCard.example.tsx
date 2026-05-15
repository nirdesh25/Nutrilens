import React, { useState } from 'react';
import { ErrorCard } from './ErrorCard';

/**
 * Example usage of the ErrorCard component
 * 
 * This file demonstrates various use cases for the ErrorCard component
 * including network errors, API errors, and retry functionality.
 */

// Example 1: Basic Error Card
export function BasicErrorCardExample() {
  const handleRetry = () => {
    console.log('Retrying operation...');
    // Implement retry logic here
  };

  return (
    <div className="p-4">
      <ErrorCard 
        message="Failed to load data" 
        onRetry={handleRetry} 
      />
    </div>
  );
}

// Example 2: Network Error with Retry
export function NetworkErrorExample() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>('Unable to connect to server. Please check your connection and try again.');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call
      const response = await fetch('https://api.example.com/data');
      if (!response.ok) throw new Error('Network error');
      
      const data = await response.json();
      console.log('Data loaded:', data);
    } catch (err) {
      setError('Unable to connect to server. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-4">
        <ErrorCard message={error} onRetry={fetchData} />
      </div>
    );
  }

  return <div className="p-4">Data loaded successfully!</div>;
}

// Example 3: API Error with Multiple Retry Attempts
export function APIErrorWithRetriesExample() {
  const [error, setError] = useState<string | null>('Something went wrong on our end. Please try again later.');
  const [retryCount, setRetryCount] = useState(0);

  const handleRetry = async () => {
    setRetryCount(prev => prev + 1);
    console.log(`Retry attempt ${retryCount + 1}`);
    
    try {
      // Simulate API call
      await new Promise((resolve, reject) => {
        setTimeout(() => {
          // Simulate random success/failure
          if (Math.random() > 0.5) {
            resolve('success');
          } else {
            reject(new Error('API error'));
          }
        }, 1000);
      });
      
      setError(null);
      console.log('Operation succeeded!');
    } catch (err) {
      setError(`Something went wrong on our end. Please try again later. (Attempt ${retryCount + 1})`);
    }
  };

  if (!error) {
    return <div className="p-4">Operation completed successfully!</div>;
  }

  return (
    <div className="p-4">
      <ErrorCard message={error} onRetry={handleRetry} />
    </div>
  );
}

// Example 4: Error Card in a Page Layout
export function PageWithErrorExample() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>('Failed to load user data. Please try again.');
  const [loading, setLoading] = useState(false);

  const loadUserData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call
      const response = await fetch('/api/user');
      if (!response.ok) throw new Error('Failed to fetch');
      
      const userData = await response.json();
      setData(userData);
    } catch (err) {
      setError('Failed to load user data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">User Profile</h1>
        
        {loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading...</p>
          </div>
        )}
        
        {error && !loading && (
          <ErrorCard message={error} onRetry={loadUserData} />
        )}
        
        {data && !loading && !error && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">User Information</h2>
            <pre className="text-sm">{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

// Example 5: Multiple Error Cards
export function MultipleErrorCardsExample() {
  const [errors, setErrors] = useState([
    { id: 1, message: 'Failed to load user profile', retry: () => console.log('Retry user profile') },
    { id: 2, message: 'Failed to load notifications', retry: () => console.log('Retry notifications') },
    { id: 3, message: 'Failed to load settings', retry: () => console.log('Retry settings') },
  ]);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-2xl font-bold mb-4">Multiple Errors</h2>
      {errors.map(error => (
        <ErrorCard 
          key={error.id}
          message={error.message} 
          onRetry={error.retry} 
        />
      ))}
    </div>
  );
}

// Example 6: Error Card with Custom Retry Logic
export function CustomRetryLogicExample() {
  const [error, setError] = useState<string | null>('Operation failed');
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetryWithDelay = async () => {
    setIsRetrying(true);
    
    // Wait 2 seconds before retrying
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      // Simulate operation
      await fetch('/api/data');
      setError(null);
    } catch (err) {
      setError('Operation failed. Please try again.');
    } finally {
      setIsRetrying(false);
    }
  };

  if (isRetrying) {
    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-md p-6 text-center">
          <p className="text-gray-600">Retrying...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <ErrorCard message={error} onRetry={handleRetryWithDelay} />
      </div>
    );
  }

  return <div className="p-4">Success!</div>;
}

// Example 7: Error Card in Grid Layout
export function ErrorCardGridExample() {
  const sections = [
    { id: 1, name: 'Analytics', error: 'Failed to load analytics data' },
    { id: 2, name: 'Reports', error: 'Failed to load reports' },
    { id: 3, name: 'Statistics', error: 'Failed to load statistics' },
  ];

  const handleRetry = (sectionName: string) => {
    console.log(`Retrying ${sectionName}...`);
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-6">Dashboard Sections</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sections.map(section => (
          <ErrorCard 
            key={section.id}
            message={section.error} 
            onRetry={() => handleRetry(section.name)} 
          />
        ))}
      </div>
    </div>
  );
}
