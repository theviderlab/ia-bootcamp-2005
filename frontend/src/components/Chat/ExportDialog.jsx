import { useState } from 'react';
import { useChatStore } from '@store/chatStore';
import { exportAsJSON, exportAsMarkdown, downloadFile, generateExportFilename } from '@utils/export';

/**
 * ExportDialog Component
 * 
 * Modal for exporting conversation in different formats:
 * - JSON (structured data with metadata)
 * - Markdown (human-readable format)
 */
export const ExportDialog = ({ isOpen, onClose }) => {
  const { messages, sessionId } = useChatStore();
  const [format, setFormat] = useState('json');
  const [includeMetadata, setIncludeMetadata] = useState(true);

  if (!isOpen) return null;

  const handleExport = () => {
    if (messages.length === 0) {
      alert('No messages to export');
      return;
    }

    try {
      let content;
      let mimeType;
      
      if (format === 'json') {
        content = exportAsJSON(messages, sessionId);
        mimeType = 'application/json';
      } else {
        content = exportAsMarkdown(messages, sessionId);
        mimeType = 'text/markdown';
      }

      const filename = generateExportFilename(format, sessionId);
      downloadFile(content, filename, mimeType);
      
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export conversation. Please try again.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Export Conversation
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Download your conversation in your preferred format
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          {/* Message Count */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
            <p className="text-sm text-blue-800 dark:text-blue-300">
              📊 <strong>{messages.length}</strong> messages will be exported
            </p>
          </div>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Export Format
            </label>
            <div className="space-y-2">
              <label className="flex items-start p-3 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <input
                  type="radio"
                  name="format"
                  value="json"
                  checked={format === 'json'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mt-0.5 mr-3"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    JSON
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Structured format with metadata. Best for programmatic use or re-importing.
                  </div>
                </div>
              </label>

              <label className="flex items-start p-3 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <input
                  type="radio"
                  name="format"
                  value="markdown"
                  checked={format === 'markdown'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mt-0.5 mr-3"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    Markdown
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Human-readable format. Best for documentation or sharing.
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Preview Info */}
          <div className="text-xs text-gray-500 dark:text-gray-400">
            <p>
              <strong>Session ID:</strong> {sessionId || 'Not started'}
            </p>
            <p className="mt-1">
              <strong>Filename:</strong> {generateExportFilename(format, sessionId)}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={messages.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            📥 Export
          </button>
        </div>
      </div>
    </div>
  );
};
