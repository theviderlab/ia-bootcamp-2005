import { useState, useEffect, useCallback } from 'react';
import { useChatStore } from '@store/chatStore';
import { mcpService } from '@services/mcpService';
import { configService } from '@services/configService';

/**
 * useMCP Hook
 * 
 * Manages MCP (Model Context Protocol) tools state and configuration.
 * Follows the pattern from useMemory and useRAG hooks.
 * 
 * Features:
 * - Fetch available tools from backend
 * - Toggle MCP tools on/off
 * - Select specific tools to enable
 * - Sync with backend session config
 * - Pre-session config support (localStorage)
 * 
 * @returns {Object} MCP state and actions
 */
export const useMCP = () => {
  const sessionId = useChatStore((state) => state.sessionId);
  
  // State
  const [toolsEnabled, setToolsEnabled] = useState(false);
  const [selectedTools, setSelectedTools] = useState([]);
  const [availableTools, setAvailableTools] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch available tools from backend
   * Called once on mount
   */
  const fetchTools = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await mcpService.getTools();
      const tools = response.tools || [];
      
      setAvailableTools(tools);
      console.log('[useMCP] Fetched tools:', tools.length);

    } catch (err) {
      console.error('[useMCP] Failed to fetch tools:', err);
      setError(err.message);
      setAvailableTools([]);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Load MCP configuration from backend or localStorage
   */
  const loadConfig = useCallback(async () => {
    if (!sessionId) {
      // No session yet, check localStorage for pre-session config
      const preSessionConfig = localStorage.getItem('preSessionMCPConfig');
      
      if (preSessionConfig) {
        try {
          const config = JSON.parse(preSessionConfig);
          setToolsEnabled(config.enabled ?? false);
          setSelectedTools(config.selectedTools ?? []);
          console.log('[useMCP] Loaded pre-session config:', config);
          return;
        } catch (e) {
          console.error('[useMCP] Failed to parse pre-session config:', e);
        }
      }
      
      // Default: MCP disabled
      setToolsEnabled(false);
      setSelectedTools([]);
      return;
    }
    
    try {
      const response = await configService.getSession(sessionId);
      const config = response.config;
      
      // Parse MCP config from backend
      const mcp = config.mcp;
      setToolsEnabled(mcp?.enabled ?? false);
      setSelectedTools(mcp?.available_tools ?? []);
      
      // Clear pre-session config after successful sync
      localStorage.removeItem('preSessionMCPConfig');
      
      console.log('[useMCP] Loaded config from backend:', mcp);
    } catch (err) {
      console.error('[useMCP] Failed to load config:', err);
      // Default on error
      setToolsEnabled(false);
      setSelectedTools([]);
    }
  }, [sessionId]);

  /**
   * Update MCP configuration
   * Saves to localStorage if no session, otherwise syncs with backend
   */
  const updateConfig = useCallback(async (enabled, tools = []) => {
    if (!sessionId) {
      console.warn('[useMCP] No session ID, saving to localStorage');
      
      // Save to localStorage for application after session creation
      const preSessionConfig = {
        enabled,
        selectedTools: tools,
        timestamp: Date.now(),
      };
      localStorage.setItem('preSessionMCPConfig', JSON.stringify(preSessionConfig));
      
      // Update local state
      setToolsEnabled(enabled);
      setSelectedTools(tools);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);

      // Update session config on backend
      await configService.updateSession({
        session_id: sessionId,
        mcp: {
          enabled,
          available_tools: tools.length > 0 ? tools : null,
        },
      });

      // Update local state
      setToolsEnabled(enabled);
      setSelectedTools(tools);
      
      console.log('[useMCP] Config updated:', { enabled, tools });

    } catch (err) {
      console.error('[useMCP] Failed to update config:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /**
   * Toggle MCP master switch
   * When disabled, clears all selected tools
   */
  const toggleMCP = useCallback(async (enabled) => {
    const tools = enabled ? selectedTools : [];
    await updateConfig(enabled, tools);
  }, [selectedTools, updateConfig]);

  /**
   * Toggle individual tool selection
   * Automatically enables MCP if a tool is selected
   */
  const toggleTool = useCallback(async (toolName) => {
    const newSelectedTools = selectedTools.includes(toolName)
      ? selectedTools.filter(t => t !== toolName)
      : [...selectedTools, toolName];
    
    // Auto-enable MCP if any tool is selected
    const enabled = newSelectedTools.length > 0;
    
    await updateConfig(enabled, newSelectedTools);
  }, [selectedTools, updateConfig]);

  /**
   * Select all tools
   */
  const selectAllTools = useCallback(async () => {
    const allToolNames = availableTools.map(t => t.name);
    await updateConfig(true, allToolNames);
  }, [availableTools, updateConfig]);

  /**
   * Clear all tool selections
   */
  const clearAllTools = useCallback(async () => {
    await updateConfig(false, []);
  }, [updateConfig]);

  // Fetch tools on mount
  useEffect(() => {
    fetchTools();
  }, [fetchTools]);

  // Load config when session changes
  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  return {
    // State
    toolsEnabled,
    selectedTools,
    availableTools,
    loading,
    error,
    
    // Actions
    toggleMCP,
    toggleTool,
    selectAllTools,
    clearAllTools,
    fetchTools,
    loadConfig,
  };
};
