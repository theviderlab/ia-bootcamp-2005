import apiClient from './api';
import { API_ENDPOINTS } from '@constants/api';

/**
 * Memory Service
 * Handles all memory-related API calls including short-term, long-term memory,
 * configuration, and search functionality.
 */
export const memoryService = {
  /**
   * Get memory context for the current session
   * @param {string} sessionId - Current session ID
   * @param {Array<string>} memoryTypes - Array of memory types to retrieve
   * @returns {Promise<Object>} Memory context data
   */
  getContext: async (sessionId, memoryTypes = []) => {
    const response = await apiClient.post(API_ENDPOINTS.MEMORY_CONTEXT, {
      session_id: sessionId,
      memory_types: memoryTypes,
    });
    return response.data;
  },

  /**
   * Get conversation history (short-term memory)
   * @param {string} sessionId - Current session ID
   * @param {number} limit - Number of messages to retrieve
   * @returns {Promise<Object>} History data
   */
  getHistory: async (sessionId, limit = 20) => {
    const response = await apiClient.get(
      `${API_ENDPOINTS.MEMORY_HISTORY}/${sessionId}`,
      {
        params: { limit },
      }
    );
    return response.data;
  },

  /**
   * Get memory statistics for the current session
   * @param {string} sessionId - Current session ID
   * @returns {Promise<Object>} Memory statistics
   */
  getStats: async (sessionId) => {
    const response = await apiClient.get(
      `${API_ENDPOINTS.MEMORY_STATS}/${sessionId}`
    );
    return response.data;
  },

  /**
   * Search through memory using semantic search
   * @param {string} query - Search query
   * @param {string} sessionId - Current session ID
   * @param {number} topK - Number of results to return
   * @returns {Promise<Object>} Search results
   */
  search: async (query, sessionId, topK = 10) => {
    const response = await apiClient.post(API_ENDPOINTS.MEMORY_SEARCH, {
      query,
      session_id: sessionId,
      top_k: topK,
    });
    return response.data;
  },

  /**
   * Get session configuration including memory settings
   * @param {string} sessionId - Current session ID
   * @returns {Promise<Object>} Session configuration
   */
  getConfig: async (sessionId) => {
    const response = await apiClient.get(
      `${API_ENDPOINTS.CONFIG_SESSION}/${sessionId}`
    );
    return response.data;
  },

  /**
   * Update memory configuration
   * @param {string} sessionId - Current session ID
   * @param {boolean} enableShortTerm - Enable short-term memory
   * @param {boolean} enableSemantic - Enable semantic memory
   * @param {boolean} enableEpisodic - Enable episodic memory
   * @param {boolean} enableProfile - Enable profile memory
   * @param {boolean} enableProcedural - Enable procedural memory
   * @returns {Promise<Object>} Updated configuration
   */
  updateConfig: async (
    sessionId,
    enableShortTerm = true,
    enableSemantic = false,
    enableEpisodic = false,
    enableProfile = false,
    enableProcedural = false
  ) => {
    // POST /config/session to update session configuration
    const response = await apiClient.post(
      API_ENDPOINTS.CONFIG_SESSION,
      {
        session_id: sessionId,
        memory: {
          enable_short_term: enableShortTerm,
          enable_semantic: enableSemantic,
          enable_episodic: enableEpisodic,
          enable_profile: enableProfile,
          enable_procedural: enableProcedural,
        },
      }
    );
    return response.data;
  },

  /**
   * Clear memory for a specific session
   * @param {string} sessionId - Current session ID
   * @returns {Promise<Object>} Deletion result
   */
  clearMemory: async (sessionId) => {
    const response = await apiClient.delete(
      `${API_ENDPOINTS.MEMORY_HISTORY}/${sessionId}`
    );
    return response.data;
  },

  // ============================================================================
  // Long-term Memory Extraction
  // ============================================================================

  /**
   * Extract and store user profile from conversation
   * @param {string} sessionId - Session ID to extract from
   * @param {boolean} incremental - Only process new messages (default: false for full extraction)
   * @returns {Promise<Object>} Extracted profile data
   */
  extractProfile: async (sessionId, incremental = false) => {
    const response = await apiClient.post(API_ENDPOINTS.MEMORY_PROFILE_EXTRACT, {
      session_id: sessionId,
      incremental: incremental,
    });
    return response.data;
  },

  /**
   * Extract and store semantic facts from conversation
   * @param {string} sessionId - Session ID to extract from
   * @param {boolean} incremental - Only process new messages (default: false)
   * @returns {Promise<Object>} Extracted semantic facts with metadata
   */
  extractSemantic: async (sessionId, incremental = false) => {
    const response = await apiClient.post(API_ENDPOINTS.MEMORY_SEMANTIC_EXTRACT, {
      session_id: sessionId,
      incremental: incremental,
    });
    return response.data;
  },

  /**
   * Extract and store episodic summary from conversation
   * @param {string} sessionId - Session ID to extract from
   * @returns {Promise<Object>} Extracted episodic summary
   * @todo Backend endpoint implementation pending
   */
  extractEpisodic: async (sessionId) => {
    // TODO: Implement when backend endpoint is ready
    console.warn('[memoryService] extractEpisodic: Backend endpoint not yet implemented');
    return { status: 'pending', message: 'Episodic extraction not yet implemented' };
  },

  /**
   * Extract and store procedural patterns from conversation
   * @param {string} sessionId - Session ID to extract from
   * @returns {Promise<Object>} Extracted procedural patterns
   * @todo Backend endpoint implementation pending
   */
  extractProcedural: async (sessionId) => {
    // TODO: Implement when backend endpoint is ready
    console.warn('[memoryService] extractProcedural: Backend endpoint not yet implemented');
    return { status: 'pending', message: 'Procedural extraction not yet implemented' };
  },

  /**
   * Save all active long-term memories based on enabled types
   * @param {string} sessionId - Session ID to extract from
   * @param {Object} enabledTypes - Which memory types are enabled
   * @param {boolean} enabledTypes.profile - Extract profile memory
   * @param {boolean} enabledTypes.semantic - Extract semantic memory
   * @param {boolean} enabledTypes.episodic - Extract episodic memory
   * @param {boolean} enabledTypes.procedural - Extract procedural memory
   * @returns {Promise<Object>} Summary of extraction results
   */
  saveLongTermMemory: async (sessionId, enabledTypes = {}) => {
    const results = {
      profile: null,
      semantic: null,
      episodic: null,
      procedural: null,
      errors: [],
    };

    // Extract profile if enabled
    if (enabledTypes.profile) {
      try {
        console.log('[memoryService] Extracting profile memory...');
        results.profile = await memoryService.extractProfile(sessionId, false); // Full extraction
      } catch (err) {
        console.error('[memoryService] Failed to extract profile:', err);
        results.errors.push({ type: 'profile', error: err.message });
      }
    }

    // Extract semantic facts if enabled
    if (enabledTypes.semantic) {
      try {
        console.log('[memoryService] Extracting semantic memory...');
        results.semantic = await memoryService.extractSemantic(sessionId);
      } catch (err) {
        console.error('[memoryService] Failed to extract semantic:', err);
        results.errors.push({ type: 'semantic', error: err.message });
      }
    }

    // Extract episodic summary if enabled
    if (enabledTypes.episodic) {
      try {
        console.log('[memoryService] Extracting episodic memory...');
        results.episodic = await memoryService.extractEpisodic(sessionId);
      } catch (err) {
        console.error('[memoryService] Failed to extract episodic:', err);
        results.errors.push({ type: 'episodic', error: err.message });
      }
    }

    // Extract procedural patterns if enabled
    if (enabledTypes.procedural) {
      try {
        console.log('[memoryService] Extracting procedural memory...');
        results.procedural = await memoryService.extractProcedural(sessionId);
      } catch (err) {
        console.error('[memoryService] Failed to extract procedural:', err);
        results.errors.push({ type: 'procedural', error: err.message });
      }
    }

    return results;
  },
};

export default memoryService;
