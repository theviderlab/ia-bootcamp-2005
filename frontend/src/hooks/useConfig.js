import { useState, useEffect } from 'react';
import configService from '@services/configService';
import { useChatStore } from '@store/chatStore';

/**
 * useConfig Hook
 * 
 * Manages session configuration state and API interactions.
 * Loads configuration when session ID becomes available.
 */
export const useConfig = () => {
  const sessionId = useChatStore((state) => state.sessionId);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load session configuration from backend
   */
  const loadConfig = async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await configService.getSessionConfig(sessionId);
      setConfig(data);
    } catch (err) {
      // If no config exists, that's okay (will use defaults)
      if (err.response?.status === 404) {
        setConfig(null);
      } else {
        setError(err.message);
        console.error('Failed to load configuration:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update session configuration
   * @param {Object} updates - Configuration updates
   */
  const updateConfig = async (updates) => {
    if (!sessionId) {
      setError('No active session');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        session_id: sessionId,
        ...updates,
      };
      const data = await configService.updateSessionConfig(payload);
      setConfig(data.config);
      return data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to update configuration:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete session configuration (revert to defaults)
   */
  const deleteConfig = async () => {
    if (!sessionId) {
      setError('No active session');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await configService.deleteSessionConfig(sessionId);
      setConfig(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete configuration:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get global configuration status
   */
  const getStatus = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await configService.getStatus();
      return data;
    } catch (err) {
      setError(err.message);
      console.error('Failed to get configuration status:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Load config when session ID changes
  useEffect(() => {
    if (sessionId) {
      loadConfig();
    }
  }, [sessionId]);

  return {
    config,
    loading,
    error,
    loadConfig,
    updateConfig,
    deleteConfig,
    getStatus,
  };
};
