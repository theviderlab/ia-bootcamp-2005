import { useState } from 'react';
import { useChat } from '@hooks/useChat';
import { useMemory } from '@hooks/useMemory';
import { useRAG } from '@hooks/useRAG';
import { useMCP } from '@hooks/useMCP';
import { useDebounce } from '@utils/debounce';
import { MessageList } from '../Chat/MessageList';
import { InputBox } from '../Chat/InputBox';
import { ExportDialog } from '../Chat/ExportDialog';

/**
 * ChatTab Component
 * 
 * Main chat interface combining MessageList and InputBox.
 * Uses useChat hook for state management and API integration.
 * Phase 6: Integrated MCP tools with chat flow.
 * Phase 7: Adds export and search functionality.
 */
export const ChatTab = () => {
  const { messages, loading, error, sendMessage, clearError } = useChat();
  const { memoryEnabled, enabledTypes } = useMemory();
  const { ragEnabled, selectedNamespaces } = useRAG();
  const { toolsEnabled, selectedTools } = useMCP();
  const [showExport, setShowExport] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Debounce search query to reduce re-renders
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  /**
   * Handle message send with current configuration
   */
  const handleSend = async (content) => {
    await sendMessage(content, {
      // Memory config
      useMemory: memoryEnabled,
      memoryTypes: enabledTypes,
      
      // RAG config
      useRAG: ragEnabled,
      ragNamespaces: selectedNamespaces,
      
      // MCP tools config
      useTools: toolsEnabled,
      availableTools: selectedTools.length > 0 ? selectedTools : null,
      toolChoice: 'auto',
    });
  };

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="border-b border-gray-200 dark:border-gray-700 px-4 py-2 flex items-center justify-between gap-3">
        {/* Search Input */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search messages..."
              className="w-full pl-9 pr-4 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <svg
              className="absolute left-3 top-2 w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExport(true)}
            disabled={messages.length === 0}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Export conversation"
          >
            📥 Export
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
            <span>⚠️</span>
            <span className="text-sm">{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 text-sm font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Messages Area */}
      <MessageList messages={messages} loading={loading} searchQuery={debouncedSearchQuery} />

      {/* Input Area */}
      <InputBox onSend={handleSend} loading={loading} disabled={!!error} />

      {/* Export Dialog */}
      <ExportDialog isOpen={showExport} onClose={() => setShowExport(false)} />
    </div>
  );
};
