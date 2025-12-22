import { useState } from 'react';

/**
 * ToolResult Component
 * 
 * Displays tool execution results with collapsible details.
 * Shows tool calls, arguments, and execution results.
 * 
 * Features:
 * - Collapsible sections for each tool call
 * - Success/error status indicators
 * - Formatted JSON arguments and output
 * - Copy to clipboard for results
 * 
 * Phase 6: Tool Results Display
 */
export const ToolResult = ({ toolCalls, toolResults }) => {
  const [expandedCalls, setExpandedCalls] = useState(new Set());

  if (!toolCalls || toolCalls.length === 0) return null;

  /**
   * Toggle tool call expansion
   */
  const toggleCall = (callId) => {
    const newExpanded = new Set(expandedCalls);
    if (newExpanded.has(callId)) {
      newExpanded.delete(callId);
    } else {
      newExpanded.add(callId);
    }
    setExpandedCalls(newExpanded);
  };

  /**
   * Get result for a specific tool call
   */
  const getResult = (callId) => {
    if (!toolResults) return null;
    return toolResults.find(r => r.tool_call_id === callId);
  };

  /**
   * Copy text to clipboard
   */
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  /**
   * Format JSON with pretty print
   */
  const formatJSON = (obj) => {
    if (typeof obj === 'string') return obj;
    return JSON.stringify(obj, null, 2);
  };

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
        Tool Execution Details
      </div>
      
      {toolCalls.map((call, index) => {
        const result = getResult(call.id);
        const isExpanded = expandedCalls.has(call.id);
        const success = result?.success !== false;

        return (
          <div
            key={call.id || index}
            className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
          >
            {/* Header */}
            <button
              onClick={() => toggleCall(call.id)}
              className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
            >
              <div className="flex items-center space-x-2">
                {/* Status Indicator */}
                <span className={`text-lg ${success ? '✅' : '❌'}`}>
                  {success ? '✅' : '❌'}
                </span>
                
                {/* Tool Name */}
                <span className="font-mono text-sm font-semibold text-gray-900 dark:text-white">
                  {call.name}
                </span>

                {/* Badge */}
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium
                  ${success 
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                  }`}
                >
                  {success ? 'Success' : 'Error'}
                </span>
              </div>

              {/* Expand Icon */}
              <span className="text-gray-500 dark:text-gray-400 text-xs">
                {isExpanded ? '▼ Hide' : '▶ Show'}
              </span>
            </button>

            {/* Expanded Details */}
            {isExpanded && (
              <div className="p-3 space-y-3 bg-white dark:bg-gray-900">
                {/* Arguments */}
                {call.arguments && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                        Arguments:
                      </span>
                      <button
                        onClick={() => copyToClipboard(formatJSON(call.arguments))}
                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Copy
                      </button>
                    </div>
                    <pre className="text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                      <code className="text-gray-800 dark:text-gray-200">
                        {formatJSON(call.arguments)}
                      </code>
                    </pre>
                  </div>
                )}

                {/* Result Output */}
                {result && (
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                        Output:
                      </span>
                      <button
                        onClick={() => copyToClipboard(
                          typeof result.output === 'string' ? result.output : formatJSON(result.output)
                        )}
                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Copy
                      </button>
                    </div>
                    <pre className={`text-xs p-2 rounded overflow-x-auto
                      ${success 
                        ? 'bg-green-50 dark:bg-green-900/20'
                        : 'bg-red-50 dark:bg-red-900/20'
                      }`}
                    >
                      <code className={`${
                        success 
                          ? 'text-green-800 dark:text-green-300'
                          : 'text-red-800 dark:text-red-300'
                      }`}>
                        {typeof result.output === 'string' 
                          ? result.output 
                          : formatJSON(result.output)
                        }
                      </code>
                    </pre>
                  </div>
                )}

                {/* Error Message */}
                {result && !success && result.error && (
                  <div>
                    <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                      Error:
                    </span>
                    <div className="text-xs text-red-700 dark:text-red-300 mt-1">
                      {result.error}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
