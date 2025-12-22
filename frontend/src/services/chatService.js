import apiClient from './api';
import { API_ENDPOINTS } from '@constants/api';

/**
 * Chat Service
 * Handles all chat-related API calls
 */

export const chatService = {
  /**
   * Send a chat message
   * 
   * IMPORTANT: Backend manages all conversation history, memory, RAG, and tools.
   * 
   * Configuration (memory, RAG, MCP tools) is read from session_configs in database.
   * The messages array should contain ONLY the current user message.
   * Do NOT send the full conversation history - the backend reconstructs
   * context from its memory system based on session_id.
   * 
   * @param {Array} messages - Array with single current user message [{role: 'user', content: '...'}]
   * @param {Object} config - Optional generation parameters (temperature, max_tokens, etc.)
   * @returns {Promise<Object>} Chat response with context and sources
   */
  sendMessage: async (messages, config = {}) => {
    const {
      session_id = null,
      temperature = 0.7,
      max_tokens = 500,
      max_context_tokens = 4000,
      context_priority = 'balanced',
    } = config;

    const response = await apiClient.post(API_ENDPOINTS.chat, {
      messages,
      session_id,
      temperature,
      max_tokens,
      max_context_tokens,
      context_priority,
    });

    return response.data;
  },

  /**
   * Generate text from a prompt
   * @param {string} prompt - Text prompt
   * @param {Object} options - Generation options
   * @returns {Promise<Object>} Generated text
   */
  generate: async (prompt, options = {}) => {
    const { temperature = 0.7, maxTokens = 1000 } = options;

    const response = await apiClient.post(API_ENDPOINTS.generate, {
      prompt,
      temperature,
      max_tokens: maxTokens,
    });

    return response.data;
  },
};

export default chatService;
