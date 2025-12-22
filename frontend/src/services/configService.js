import api from './api';

/**
 * Configuration Service
 * 
 * Handles session configuration endpoints for managing
 * persistent settings like memory types, RAG preferences, etc.
 */
const configService = {
  /**
   * Get global configuration status
   * @returns {Promise} Configuration status
   */
  getStatus: async () => {
    const response = await api.get('/config/status');
    return response.data;
  },

  /**
   * Get session-specific configuration
   * @param {string} sessionId - Session ID
   * @returns {Promise} Session configuration
   */
  getSessionConfig: async (sessionId) => {
    const response = await api.get(`/config/session/${sessionId}`);
    return response.data;
  },

  /**
   * Create or update session configuration
   * @param {Object} config - Configuration object
   * @param {string} config.session_id - Session ID
   * @param {Object} config.memory - Memory configuration
   * @param {Object} config.rag - RAG configuration
   * @param {Object} config.preferences - General preferences
   * @returns {Promise} Update result
   */
  updateSessionConfig: async (config) => {
    const response = await api.post('/config/session', config);
    return response.data;
  },

  /**
   * Delete session configuration (revert to defaults)
   * @param {string} sessionId - Session ID
   * @returns {Promise} Deletion result
   */
  deleteSessionConfig: async (sessionId) => {
    const response = await api.delete(`/config/session/${sessionId}`);
    return response.data;
  },

  /**
   * Update memory toggles (shortcut endpoint)
   * @param {Object} memoryConfig - Memory configuration
   * @param {boolean} memoryConfig.enabled - Enable memory
   * @param {string[]} memoryConfig.types - Memory types array
   * @returns {Promise} Update result
   */
  updateMemoryToggles: async (memoryConfig) => {
    const response = await api.put('/config/memory', memoryConfig);
    return response.data;
  },

  /**
   * Update RAG toggles (shortcut endpoint)
   * @param {Object} ragConfig - RAG configuration
   * @param {boolean} ragConfig.enabled - Enable RAG
   * @param {string[]} ragConfig.namespaces - Enabled namespaces
   * @param {number} ragConfig.top_k - Number of chunks to retrieve
   * @returns {Promise} Update result
   */
  updateRAGToggles: async (ragConfig) => {
    const response = await api.put('/config/rag', ragConfig);
    return response.data;
  },
};

export { configService };
export default configService;
