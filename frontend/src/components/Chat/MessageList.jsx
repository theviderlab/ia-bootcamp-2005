import { useEffect, useRef, useMemo } from 'react';
import { useChatStore } from '@store/chatStore';
import { Message } from './Message';

/**
 * MessageList Component
 * 
 * Scrollable area displaying all chat messages.
 * Features:
 * - Auto-scroll to bottom on new messages
 * - Loading indicator while waiting for response
 * - Empty state for first load
 * - Search highlighting (Phase 7)
 * - Tool results display for last assistant message (Phase 6)
 */
export const MessageList = ({ messages, loading, searchQuery = '' }) => {
  const contextData = useChatStore((state) => state.contextData);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  // Filter messages based on search query
  const filteredMessages = useMemo(() => {
    if (!searchQuery.trim()) return messages;
    
    const query = searchQuery.toLowerCase();
    return messages.filter((msg) =>
      msg.content.toLowerCase().includes(query)
    );
  }, [messages, searchQuery]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900"
    >
      {/* Empty State */}
      {messages.length === 0 && !loading && (
        <div className="flex items-center justify-center h-full text-gray-400 dark:text-gray-500">
          <div className="text-center">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">Type a message below to begin</p>
          </div>
        </div>
      )}

      {/* Search Results Info */}
      {searchQuery && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg px-4 py-2 text-sm text-blue-700 dark:text-blue-300">
          {filteredMessages.length === 0 ? (
            <span>No messages match "{searchQuery}"</span>
          ) : (
            <span>
              Showing {filteredMessages.length} of {messages.length} messages
            </span>
          )}
        </div>
      )}

      {/* Messages */}
      {filteredMessages.map((message, index) => {
        // Check if this is the last assistant message
        const isLastAssistant = message.role === 'assistant' && index === filteredMessages.length - 1;
        
        return (
          <Message
            key={message.id}
            message={message}
            searchQuery={searchQuery}
            isLastAssistant={isLastAssistant}
            toolData={isLastAssistant ? contextData : null}
          />
        );
      })}

      {/* Loading Indicator */}
      {loading && (
        <div className="flex justify-start">
          <div className="bg-secondary-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg px-4 py-3 shadow-sm">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};
