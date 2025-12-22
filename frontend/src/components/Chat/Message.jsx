import { useState } from 'react';
import clsx from 'clsx';
import { formatRelativeTime } from '@utils/formatters';
import { highlightText } from '@utils/highlight';
import { ToolBadge } from './ToolBadge';
import { ToolResult } from './ToolResult';

/**
 * Message Component
 * 
 * Displays a single chat message (user or assistant).
 * Features:
 * - Different styling for user/assistant roles
 * - Timestamp with relative time
 * - Copy to clipboard functionality
 * - Search term highlighting (Phase 7)
 * - Tool results display (Phase 6)
 */
export const Message = ({ message, searchQuery = '', isLastAssistant = false, toolData = null }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Highlight search terms in content
  const highlightedContent = highlightText(message.content, searchQuery);

  // Show tool results only for last assistant message
  const showToolResults = isLastAssistant && !isUser && toolData?.tools_used;

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-[80%] rounded-lg px-4 py-3 shadow-sm',
          isUser
            ? 'bg-primary-500 text-white'
            : 'bg-secondary-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
        )}
      >
        {/* Tool Badge */}
        {showToolResults && (
          <div className="mb-2">
            <ToolBadge toolCalls={toolData.tool_calls} />
          </div>
        )}

        {/* Message Content */}
        <div className={clsx(
          'whitespace-pre-wrap break-words',
          isUser ? 'text-right' : 'text-left'
        )}>
          {highlightedContent.map((segment, index) => (
            segment.highlighted ? (
              <mark
                key={index}
                className="bg-yellow-200 dark:bg-yellow-600 text-gray-900 dark:text-gray-100 px-0.5 rounded"
              >
                {segment.text}
              </mark>
            ) : (
              <span key={index}>{segment.text}</span>
            )
          ))}
        </div>

        {/* Timestamp and Actions */}
        <div className="flex items-center justify-between mt-2 gap-3">
          <span
            className={clsx(
              'text-xs',
              isUser ? 'text-primary-100' : 'text-gray-500 dark:text-gray-400'
            )}
          >
            {formatRelativeTime(message.timestamp)}
          </span>

          <button
            onClick={handleCopy}
            className={clsx(
              'text-xs px-2 py-1 rounded transition-colors',
              isUser
                ? 'hover:bg-primary-600 text-primary-100'
                : 'hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300'
            )}
            title="Copy message"
          >
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
        </div>

        {/* Tool Results */}
        {showToolResults && (
          <ToolResult
            toolCalls={toolData.tool_calls}
            toolResults={toolData.tool_results}
          />
        )}
      </div>
    </div>
  );
};
