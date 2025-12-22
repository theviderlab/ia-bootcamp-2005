import apiClient from './api';
import { API_ENDPOINTS } from '@constants/api';

/**
 * MCP Service
 * Handles MCP (Model Context Protocol) tool management
 */

export const mcpService = {
  /**
   * Get all available tools with full details
   * @returns {Promise<Object>} List of tools with schemas
   */
  getTools: async () => {
    const response = await apiClient.get(API_ENDPOINTS.mcpTools);
    return response.data;
  },

  /**
   * Get tool names only (lightweight)
   * @returns {Promise<Object>} Array of tool names
   */
  getToolNames: async () => {
    const response = await apiClient.get(API_ENDPOINTS.mcpToolNames);
    return response.data;
  },

  /**
   * Get detailed info for a specific tool
   * @param {string} toolName - Name of the tool
   * @returns {Promise<Object>} Tool details
   */
  getToolInfo: async (toolName) => {
    const response = await apiClient.get(API_ENDPOINTS.mcpTool(toolName));
    return response.data;
  },
};

export default mcpService;
