import { useState } from 'react';
import { useMCP } from '@hooks/useMCP';

/**
 * MPCSection Component
 * 
 * Sidebar section for managing MCP (Model Context Protocol) tools.
 * Allows enabling/disabling individual tools with detailed schema display.
 * 
 * Features:
 * - Master toggle for MCP tools
 * - Individual tool selection with checkboxes
 * - Tool description tooltips
 * - Tool schema modal for detailed parameter info
 * - Select all / Clear all shortcuts
 * 
 * Phase 6: MCP Tools & Session Management
 */
export const MPCSection = () => {
  const {
    toolsEnabled,
    selectedTools,
    availableTools,
    loading,
    error,
    toggleMCP,
    toggleTool,
    selectAllTools,
    clearAllTools,
  } = useMCP();

  const [expandedTool, setExpandedTool] = useState(null);

  /**
   * Toggle tool schema visibility
   */
  const toggleToolSchema = (toolName) => {
    setExpandedTool(expandedTool === toolName ? null : toolName);
  };

  /**
   * Render tool input schema in readable format
   */
  const renderSchema = (schema) => {
    if (!schema || !schema.properties) return null;

    return (
      <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded text-xs space-y-2">
        <div className="font-semibold text-gray-700 dark:text-gray-300">Parameters:</div>
        {Object.entries(schema.properties).map(([param, details]) => (
          <div key={param} className="pl-2">
            <div className="flex items-start space-x-2">
              <span className="font-mono text-blue-600 dark:text-blue-400">{param}</span>
              {schema.required?.includes(param) && (
                <span className="text-red-500 text-xs">*</span>
              )}
            </div>
            <div className="text-gray-600 dark:text-gray-400 pl-2">
              {details.description || 'No description'}
            </div>
            <div className="text-gray-500 dark:text-gray-500 pl-2 text-xs">
              Type: {details.type}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold text-gray-900 dark:text-white">MCP Tools</h3>
          {loading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
        </div>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {availableTools.length} available
        </span>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-3 p-2 bg-red-50 dark:bg-red-900/20 rounded text-sm text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Master Toggle */}
      <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg mb-3">
        <div>
          <label className="font-medium text-gray-900 dark:text-white">
            Enable MCP Tools
          </label>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            Allow agent to use external tools
          </p>
        </div>
        <button
          role="switch"
          aria-checked={toolsEnabled}
          onClick={() => toggleMCP(!toolsEnabled)}
          disabled={loading}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
            ${toolsEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}
            ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:opacity-80'}`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
              ${toolsEnabled ? 'translate-x-6' : 'translate-x-1'}`}
          />
        </button>
      </div>

      {/* Shortcuts */}
      {toolsEnabled && availableTools.length > 0 && (
        <div className="flex items-center justify-between mb-2 px-1">
          <button
            onClick={selectAllTools}
            disabled={loading || selectedTools.length === availableTools.length}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Select All
          </button>
          <button
            onClick={clearAllTools}
            disabled={loading || selectedTools.length === 0}
            className="text-xs text-gray-600 dark:text-gray-400 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear All
          </button>
        </div>
      )}

      {/* Tool List */}
      {toolsEnabled && (
        <div className="space-y-2">
          {availableTools.length === 0 ? (
            <div className="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
              No tools available
            </div>
          ) : (
            availableTools.map((tool) => (
              <div
                key={tool.name}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
              >
                {/* Tool Header */}
                <div className="flex items-start space-x-3">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedTools.includes(tool.name)}
                    onChange={() => toggleTool(tool.name)}
                    disabled={loading}
                    className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 disabled:opacity-50"
                  />

                  {/* Tool Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <label className="font-medium text-gray-900 dark:text-white text-sm cursor-pointer">
                        {tool.name}
                      </label>
                      {tool.input_schema && (
                        <button
                          onClick={() => toggleToolSchema(tool.name)}
                          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                          title="View parameter schema"
                        >
                          {expandedTool === tool.name ? '▼ Hide' : '▶ Schema'}
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                      {tool.description || 'No description available'}
                    </p>

                    {/* Expanded Schema */}
                    {expandedTool === tool.name && tool.input_schema && (
                      <div className="mt-2">
                        {renderSchema(tool.input_schema)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <p className="text-xs text-blue-800 dark:text-blue-300">
          <strong>💡 MCP Tools:</strong> When enabled, the agent can call external
          functions during the conversation. Select specific tools to limit the
          agent's capabilities. Click "Schema" to view tool parameters.
        </p>
      </div>

      {/* Selected Tools Summary */}
      {toolsEnabled && selectedTools.length > 0 && (
        <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs">
          <span className="text-green-800 dark:text-green-300 font-medium">
            {selectedTools.length} tool{selectedTools.length > 1 ? 's' : ''} active:
          </span>
          <span className="ml-2 text-gray-700 dark:text-gray-300">
            {selectedTools.join(', ')}
          </span>
        </div>
      )}
    </div>
  );
};
