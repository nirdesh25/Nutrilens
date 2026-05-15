/**
 * ErrorMessage Component Usage Examples
 * 
 * This file demonstrates various use cases for the ErrorMessage component.
 * It can be used as a reference for developers or as a visual test page.
 */

import React from 'react';
import { ErrorMessage } from './ErrorMessage';

export function ErrorMessageExamples() {
  const handleRetry = () => {
    console.log('Retry clicked');
    alert('Retry action triggered');
  };

  return (
    <div className="space-y-8 p-8 bg-gray-50">
      <div>
        <h2 className="text-xl font-bold mb-4">ErrorMessage Component Examples</h2>
      </div>

      {/* Example 1: Basic error message without retry */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 1: Basic Error (No Retry)
        </h3>
        <ErrorMessage message="Unable to load data. Please try again later." />
      </div>

      {/* Example 2: Error message with retry button */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 2: Error with Retry Button
        </h3>
        <ErrorMessage
          message="Failed to connect to server. Please check your connection."
          onRetry={handleRetry}
        />
      </div>

      {/* Example 3: Network error */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 3: Network Error
        </h3>
        <ErrorMessage
          message="Network error occurred. Please check your internet connection and try again."
          onRetry={handleRetry}
        />
      </div>

      {/* Example 4: Authentication error */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 4: Authentication Error
        </h3>
        <ErrorMessage
          message="Your session has expired. Please log in again."
        />
      </div>

      {/* Example 5: Short error message */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 5: Short Error
        </h3>
        <ErrorMessage
          message="Something went wrong."
          onRetry={handleRetry}
        />
      </div>

      {/* Example 6: Long error message */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 6: Long Error Message
        </h3>
        <ErrorMessage
          message="We encountered an unexpected error while processing your request. This could be due to a temporary server issue or a problem with your network connection. Please wait a moment and try again."
          onRetry={handleRetry}
        />
      </div>

      {/* Example 7: In a card context */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">
          Example 7: Error in Card Context
        </h3>
        <div className="border border-gray-200 rounded-lg">
          <ErrorMessage
            message="Failed to load waste tracker data."
            onRetry={handleRetry}
          />
        </div>
      </div>

      {/* Example 8: Full page error */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Example 8: Full Page Error (Simulated)
        </h3>
        <div className="min-h-[300px] flex items-center justify-center border border-gray-200 rounded-lg">
          <ErrorMessage
            message="Page failed to load. Please refresh the page."
            onRetry={handleRetry}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Usage in actual pages:
 * 
 * // In a page component with error state
 * const [error, setError] = useState<string | null>(null);
 * 
 * const fetchData = async () => {
 *   try {
 *     const response = await api.getData();
 *     setData(response.data);
 *   } catch (err) {
 *     setError('Failed to load data');
 *   }
 * };
 * 
 * const handleRetry = () => {
 *   setError(null);
 *   fetchData();
 * };
 * 
 * return (
 *   <div>
 *     {error ? (
 *       <ErrorMessage message={error} onRetry={handleRetry} />
 *     ) : (
 *       <div>Your content here</div>
 *     )}
 *   </div>
 * );
 */
