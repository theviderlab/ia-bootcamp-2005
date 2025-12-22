import { useEffect, useState } from 'react';
import { useMemory } from '@hooks/useMemory';
import { formatRelativeTime } from '@utils/formatters';

/**
 * ShortTermMemoryTab Component
 * Displays recent conversation buffer (short-term memory)
 * Shows timeline view with expandable message cards
 */
export const ShortTermMemoryTab = () => {
  const { 
    shortTermMemory, 
    memoryStats,
    loading, 
    error,
    fetchShortTermMemory,
  } = useMemory();

  const [expandedMessages, setExpandedMessages] = useState(new Set());

  useEffect(() => {
    fetchShortTermMemory();
  }, [fetchShortTermMemory]);

  const toggleExpand = (messageId) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  if (loading && shortTermMemory.length === 0) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchShortTermMemory} />;
  }

  if (shortTermMemory.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header with Stats */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Short-term Memory</h2>
          <div className="text-sm text-gray-600">
            Recent conversation buffer stored in session
          </div>
          
          {memoryStats && (
            <div className="mt-4 grid grid-cols-3 gap-4">
              <StatCard 
                label="Messages" 
                value={shortTermMemory.length} 
                icon="💬"
              />
              <StatCard 
                label="Buffer Size" 
                value={`${memoryStats.buffer_tokens || 0} tokens`} 
                icon="🔤"
              />
              <StatCard 
                label="Session Start" 
                value={memoryStats.session_start ? formatRelativeTime(memoryStats.session_start) : 'N/A'} 
                icon="🕐"
              />
            </div>
          )}
        </div>

        {/* Timeline View */}
        <div className="space-y-3">
          {shortTermMemory.map((message, index) => (
            <MessageCard
              key={message.id || index}
              message={message}
              expanded={expandedMessages.has(message.id || index)}
              onToggleExpand={() => toggleExpand(message.id || index)}
            />
          ))}
        </div>

        {/* Refresh Button */}
        <div className="flex justify-center">
          <button
            onClick={fetchShortTermMemory}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                     flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Refreshing...
              </>
            ) : (
              <>
                <span>🔄</span>
                Refresh
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * MessageCard Component
 * Individual message card with expand/collapse functionality
 */
const MessageCard = ({ message, expanded, onToggleExpand }) => {
  const isUser = message.role === 'user';
  const timestamp = message.timestamp || message.created_at || new Date().toISOString();
  const content = message.content || '';
  const preview = content.length > 150 ? content.slice(0, 150) + '...' : content;

  return (
    <div className={`
      bg-white rounded-lg shadow-sm border border-gray-200 p-4
      transition-all hover:shadow-md
    `}>
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`
            text-xl
            ${isUser ? '👤' : '🤖'}
          `}></span>
          <div>
            <div className="font-medium text-gray-900">
              {isUser ? 'You' : 'Assistant'}
            </div>
            <div className="text-xs text-gray-500">
              {formatRelativeTime(timestamp)}
            </div>
          </div>
        </div>
        
        {content.length > 150 && (
          <button
            onClick={onToggleExpand}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        )}
      </div>

      {/* Content */}
      <div className="text-gray-700 whitespace-pre-wrap">
        {expanded ? content : preview}
      </div>

      {/* Metadata */}
      {message.tokens && (
        <div className="mt-2 pt-2 border-t border-gray-100 text-xs text-gray-500">
          {message.tokens} tokens
        </div>
      )}
    </div>
  );
};

/**
 * StatCard Component
 * Display individual statistic
 */
const StatCard = ({ label, value, icon }) => (
  <div className="text-center">
    <div className="text-2xl mb-1">{icon}</div>
    <div className="text-lg font-semibold text-gray-900">{value}</div>
    <div className="text-xs text-gray-500">{label}</div>
  </div>
);

/**
 * LoadingState Component
 */
const LoadingState = () => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p className="text-gray-600">Loading short-term memory...</p>
    </div>
  </div>
);

/**
 * ErrorState Component
 */
const ErrorState = ({ message, onRetry }) => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center max-w-md">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Memory</h3>
      <p className="text-gray-600 mb-4">{message}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

/**
 * EmptyState Component
 */
const EmptyState = () => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center max-w-md">
      <div className="text-6xl mb-4">💭</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">No Messages Yet</h3>
      <p className="text-gray-600">
        Start chatting to build your short-term memory buffer. Recent messages will appear here.
      </p>
    </div>
  </div>
);

export default ShortTermMemoryTab;
