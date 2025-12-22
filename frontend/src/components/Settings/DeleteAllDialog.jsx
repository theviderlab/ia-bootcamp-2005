import { useState } from 'react';

/**
 * DeleteAllDialog Component
 * 
 * Strong warning dialog for nuclear data deletion.
 * Requires typing "DELETE" (case-sensitive) to confirm.
 * 
 * ⚠️ WARNING: This operation is irreversible!
 * 
 * Phase 6: Session Management
 */
export const DeleteAllDialog = ({ isOpen, onClose, onConfirm, loading = false, deletionCounts = null }) => {
  const [confirmText, setConfirmText] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const isValid = confirmText === 'DELETE';

  const handleConfirm = () => {
    if (!isValid) {
      setError('You must type "DELETE" exactly (case-sensitive)');
      return;
    }

    setError('');
    onConfirm(confirmText);
  };

  const handleClose = () => {
    setConfirmText('');
    setError('');
    onClose();
  };

  // Show success screen after deletion
  if (deletionCounts) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
          {/* Header */}
          <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <h2 className="text-xl font-semibold text-green-600 dark:text-green-400">
              ✓ System Reset Complete
            </h2>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-3">
            <p className="text-gray-700 dark:text-gray-300">
              All data has been permanently deleted:
            </p>

            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Sessions:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {deletionCounts.sessions || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Memory entries:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {deletionCounts.memory_entries || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">RAG documents:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {deletionCounts.rag_documents || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Vectors:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {deletionCounts.vector_count || 0}
                </span>
              </div>
            </div>

            <p className="text-sm text-gray-500 dark:text-gray-400">
              The application will now reload with a fresh session...
            </p>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Close & Reload
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4">
        {/* Header */}
        <div className="border-b border-red-200 dark:border-red-800 px-6 py-4 bg-red-50 dark:bg-red-900/20">
          <div className="flex items-center space-x-2">
            <span className="text-3xl">💀</span>
            <div>
              <h2 className="text-xl font-semibold text-red-900 dark:text-red-300">
                ⚠️ DELETE ALL DATA
              </h2>
              <p className="text-sm text-red-700 dark:text-red-400 mt-0.5">
                This action is PERMANENT and IRREVERSIBLE
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          <div className="bg-red-100 dark:bg-red-900/30 border-2 border-red-400 dark:border-red-600 rounded-lg p-4">
            <p className="font-semibold text-red-900 dark:text-red-200 mb-2">
              This will permanently delete:
            </p>
            <ul className="text-sm text-red-800 dark:text-red-300 space-y-1 ml-4 list-disc">
              <li>All conversation history (all sessions)</li>
              <li>All long-term memory (facts, profile, patterns, episodes)</li>
              <li>All RAG documents and embeddings</li>
              <li>All session configurations</li>
              <li>All system state</li>
            </ul>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 space-y-2 text-sm">
            <p className="text-gray-700 dark:text-gray-300 font-medium">
              ⚠️ Important Notes:
            </p>
            <ul className="text-gray-600 dark:text-gray-400 space-y-1 ml-4 list-disc">
              <li>No backups will be created</li>
              <li>Data cannot be recovered</li>
              <li>System will reset to initial state</li>
            </ul>
          </div>

          {/* Confirmation Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Type <code className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded font-mono text-red-600 dark:text-red-400">DELETE</code> to confirm (case-sensitive):
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => {
                setConfirmText(e.target.value);
                setError('');
              }}
              disabled={loading}
              placeholder="DELETE"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:opacity-50 disabled:cursor-not-allowed font-mono"
              autoFocus
            />
            {error && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {error}
              </p>
            )}
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400 italic">
            Once confirmed, this operation cannot be undone. Make sure you have backups if needed.
          </p>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={handleClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading || !isValid}
            className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            <span>💀 DELETE EVERYTHING</span>
          </button>
        </div>
      </div>
    </div>
  );
};
