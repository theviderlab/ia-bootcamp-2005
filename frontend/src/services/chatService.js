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
   * IMPORTANT: Backend manages all conversation history and memory.
   * The messages array should contain ONLY the current user message.
   * Do NOT send the full conversation history - the backend reconstructs
   * context from its memory system based on session_id.
   * 
   * @param {Array} messages - Array with single current user message [{role: 'user', content: '...'}]
   * @param {Object} config - Chat configuration
   * @returns {Promise<Object>} Chat response with context and sources
   */
  sendMessage: async (messages, config = {}) => {
    const {
      sessionId = null,
      temperature = 0.7,
      maxTokens = 500,
      useMemory = true,
      useRag = false,
      memoryTypes = ['semantic', 'episodic', 'profile', 'procedural'],
      ragNamespaces = [],
      ragTopK = 5,
      maxContextTokens = 4000,
      contextPriority = 'balanced',
      useTools = false,
      toolChoice = 'auto',
      availableTools = null,
      maxToolIterations = 5,
    } = config;

    const response = await apiClient.post(API_ENDPOINTS.chat, {
      messages,
      session_id: sessionId,
      temperature,
      max_tokens: maxTokens,
      use_memory: useMemory,
      use_rag: useRag,
      memory_types: memoryTypes,
      rag_namespaces: ragNamespaces,
      rag_top_k: ragTopK,
      max_context_tokens: maxContextTokens,
      context_priority: contextPriority,
      use_tools: useTools,
      tool_choice: toolChoice,
      available_tools: availableTools,
      max_tool_iterations: maxToolIterations,
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
