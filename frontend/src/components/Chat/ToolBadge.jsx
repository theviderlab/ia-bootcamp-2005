/**
 * ToolBadge Component
 * 
 * Displays a badge indicating tools were used in the message.
 * Shows count and list of tools called.
 * 
 * Phase 6: Tool Results Display
 */
export const ToolBadge = ({ toolCalls }) => {
  if (!toolCalls || toolCalls.length === 0) return null;

  const toolNames = toolCalls.map(call => call.name);
  const uniqueTools = [...new Set(toolNames)];

  return (
    <div className="inline-flex items-center space-x-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/30 rounded-full text-xs">
      <span className="text-purple-800 dark:text-purple-300">
        🔧 Used: {uniqueTools.join(', ')}
      </span>
      {toolCalls.length > 1 && (
        <span className="text-purple-600 dark:text-purple-400 font-semibold">
          ({toolCalls.length}x)
        </span>
      )}
    </div>
  );
};
