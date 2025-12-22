import apiClient from './api';
import { API_ENDPOINTS } from '@constants/api';
import { configService } from './configService';
import { memoryService } from './memoryService';

/**
 * Session Service
 * Handles session management: reset and delete all
 */

export const sessionService = {
  /**
   * Get the latest session ID from backend
   * @returns {Promise<Object>} Object with session_id property
   */
  getLatestSession: async () => {
    const response = await apiClient.get('/session/latest');
    return response.data;
  },

  /**
   * Reset session (clear all chat history, generate new session ID)
   * No parameters needed - clears all sessions and creates a fresh one
   * @returns {Promise<Object>} New session info
   */
  resetSession: async () => {
    const response = await apiClient.post(API_ENDPOINTS.sessionReset, {});

    return response.data;
  },

  /**
   * Delete all system data (nuclear option)
   * @param {string} confirmation - Must be exactly "DELETE"
   * @returns {Promise<Object>} Deletion results
   */
  deleteAll: async (confirmation) => {
    if (confirmation !== 'DELETE') {
      throw new Error('Invalid confirmation string. Must be exactly "DELETE"');
    }

    const response = await apiClient.post(API_ENDPOINTS.sessionResetAll, {
      confirmation,
    });

    return response.data;
  },

  /**
   * Create session configuration with optional custom values
   * @param {string} sessionId - Session ID
   * @param {Object} config - Optional configuration overrides
   * @param {Object} config.memory - Memory configuration
   * @param {Object} config.rag - RAG configuration
   * @returns {Promise<Object>} Created configuration
   */
  createSessionConfig: async (sessionId, config = {}) => {
    const defaultConfig = {
      session_id: sessionId,
      memory: {
        enable_short_term: true,
        enable_semantic: false,
        enable_episodic: false,
        enable_profile: false,
        enable_procedural: false,
      },
      rag: {
        enabled: false,
        namespaces: [],
        top_k: 5,
      },
    };

    // Merge with provided config (safely handle null/undefined)
    const finalConfig = {
      session_id: sessionId,
      memory: { 
        ...defaultConfig.memory, 
        ...(config?.memory || {}) 
      },
      rag: { 
        ...defaultConfig.rag, 
        ...(config?.rag || {}) 
      },
    };

    const response = await apiClient.post(API_ENDPOINTS.CONFIG_SESSION, finalConfig);

    return response.data;
  },

  /**
   * Save active long-term memory before session reset
   * Extracts and persists profile, semantic, episodic, and procedural memory
   * based on session configuration.
   * 
   * @param {string} sessionId - Session ID to extract from
   * @returns {Promise<Object>} Summary of saved memories
   */
  saveActiveLongTermMemory: async (sessionId) => {
    try {
      console.log('[sessionService] Saving long-term memory for session:', sessionId);

      // Get session configuration to check which memory types are enabled
      let sessionConfig;
      try {
        sessionConfig = await configService.getSessionConfig(sessionId);
      } catch (err) {
        console.warn('[sessionService] Could not fetch session config:', err);
        // If we can't get config, assume nothing is enabled
        return {
          saved: false,
          reason: 'No session configuration found',
          results: {},
        };
      }

      // Extract enabled memory types from config
      // Backend returns: { config: { memory: { enable_profile: true, ... } } }
      const memoryConfig = sessionConfig?.config?.memory || {};
      const enabledTypes = {
        profile: memoryConfig.enable_profile || false,
        semantic: memoryConfig.enable_semantic || false,
        episodic: memoryConfig.enable_episodic || false,
        procedural: memoryConfig.enable_procedural || false,
      };

      console.log('[sessionService] Memory config:', memoryConfig);

      // Check if any long-term memory is enabled
      const hasEnabledTypes = Object.values(enabledTypes).some(enabled => enabled);
      
      if (!hasEnabledTypes) {
        console.log('[sessionService] No long-term memory types enabled, skipping save');
        return {
          saved: false,
          reason: 'No long-term memory types enabled',
          results: {},
        };
      }

      console.log('[sessionService] Enabled memory types:', enabledTypes);

      // Extract and save long-term memories
      const results = await memoryService.saveLongTermMemory(sessionId, enabledTypes);

      // Build summary
      const savedTypes = [];
      if (results.profile) savedTypes.push('profile');
      if (results.semantic) savedTypes.push('semantic');
      if (results.episodic) savedTypes.push('episodic');
      if (results.procedural) savedTypes.push('procedural');

      console.log('[sessionService] Saved memories:', savedTypes);

      return {
        saved: true,
        savedTypes,
        results,
        errors: results.errors || [],
      };

    } catch (err) {
      console.error('[sessionService] Failed to save long-term memory:', err);
      return {
        saved: false,
        reason: err.message,
        error: err,
      };
    }
  },
};

export default sessionService;
