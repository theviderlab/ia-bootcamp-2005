import { useState } from 'react';

/**
 * ResetDialog Component
 * 
 * Confirmation dialog for resetting the current session.
 * Clears chat history but preserves long-term memory and RAG documents.
 * 
 * Phase 6: Session Management
 */
export const ResetDialog = ({ isOpen, onClose, onConfirm, loading = false }) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Reset Session
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Start a new conversation with fresh context
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-3">
          <p className="text-gray-700 dark:text-gray-300">
            This will create a new session and clear the current conversation history.
          </p>

          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
            <p className="text-sm text-blue-800 dark:text-blue-300">
              <strong>✓ Preserved:</strong>
            </p>
            <ul className="text-sm text-blue-700 dark:text-blue-400 mt-1 space-y-1 ml-4 list-disc">
              <li>Long-term memory (facts, profile, patterns)</li>
              <li>RAG documents and embeddings</li>
              <li>Configuration settings</li>
            </ul>
          </div>

          <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3">
            <p className="text-sm text-yellow-800 dark:text-yellow-300">
              <strong>✗ Cleared:</strong>
            </p>
            <ul className="text-sm text-yellow-700 dark:text-yellow-400 mt-1 space-y-1 ml-4 list-disc">
              <li>Short-term conversation buffer (all sessions)</li>
              <li>Current chat messages</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            <span>Reset Session</span>
          </button>
        </div>
      </div>
    </div>
  );
};
