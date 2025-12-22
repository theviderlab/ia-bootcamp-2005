import { useState, useEffect, useRef } from 'react';
import { useChatStore } from '@store/chatStore';
import { sessionService } from '@services/sessionService';
import { configService } from '@services/configService';

/**
 * useSession Hook
 * 
 * Manages session lifecycle and initialization.
 * Creates a new session on mount using /session/reset.
 * Applies pre-configured settings from localStorage.
 * 
 * Features:
 * - Auto-initialize session on app load
 * - Apply pre-session memory/RAG config
 * - Reset session (clear chat, keep long-term memory)
 * - Delete all data (nuclear option)
 * 
 * @returns {Object} Session state and actions
 */
export const useSession = () => {
  const { sessionId, setSessionId, setSessionReady, resetChat, clearChatMessages } = useChatStore();
  const [initializing, setInitializing] = useState(true);
  const [resetting, setResetting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [savingMemory, setSavingMemory] = useState(false);
  const initRef = useRef(false);

  /**
   * Initialize session on mount
   * Creates a fresh session on every app load
   */
  useEffect(() => {
    // Prevent double initialization in React StrictMode
    if (initRef.current) return;
    
    const initializeSession = async () => {
      try {
        initRef.current = true;
        setInitializing(true);
        setError(null);

        // Create a fresh session on app load
        const response = await sessionService.resetSession();
        const newSessionId = response.new_session_id;
        
        setSessionId(newSessionId);
        console.log('[useSession] Session initialized:', newSessionId);

        // Get pre-session config from localStorage if exists
        const preConfig = getPreSessionConfig();
        
        // Create session configuration in database
        await sessionService.createSessionConfig(newSessionId, preConfig);
        console.log('[useSession] Session config created', preConfig ? 'with pre-config' : 'with defaults');
        
        // Clear pre-session configs from localStorage
        clearPreSessionConfig();
        
        // Mark session as ready
        setSessionReady(true);

      } catch (err) {
        console.error('[useSession] Failed to initialize session:', err);
        setError(err.message);
        initRef.current = false; // Reset on error to allow retry
      } finally {
        setInitializing(false);
      }
    };

    // Only initialize once
    if (!sessionId) {
      initializeSession();
    }
  }, []); // Empty dependency array - only run on mount

  /**
   * Get pre-session configuration from localStorage
   * @returns {Object|null} Pre-session config or null if none exists
   */
  const getPreSessionConfig = () => {
    try {
      const preSessionMemoryConfig = localStorage.getItem('preSessionMemoryConfig');
      const preSessionRAGConfig = localStorage.getItem('preSessionRAGConfig');

      if (!preSessionMemoryConfig && !preSessionRAGConfig) {
        return null;
      }

      const memoryConfig = preSessionMemoryConfig ? JSON.parse(preSessionMemoryConfig) : null;
      const ragConfig = preSessionRAGConfig ? JSON.parse(preSessionRAGConfig) : null;

      const config = {};

      if (memoryConfig) {
        const types = memoryConfig.types || [];
        config.memory = {
          enable_short_term: memoryConfig.shortTerm ?? true,
          enable_semantic: types.includes('semantic'),
          enable_episodic: types.includes('episodic'),
          enable_profile: types.includes('profile'),
          enable_procedural: types.includes('procedural'),
        };
      }

      if (ragConfig) {
        config.rag = {
          enabled: ragConfig.enabled ?? false,
          namespaces: ragConfig.selectedNamespaces || [],
          top_k: 5,
        };
      }

      return config;
    } catch (err) {
      console.error('[useSession] Failed to get pre-session config:', err);
      return null;
    }
  };

  /**
   * Clear pre-session configuration from localStorage
   */
  const clearPreSessionConfig = () => {
    localStorage.removeItem('preSessionMemoryConfig');
    localStorage.removeItem('preSessionRAGConfig');
    localStorage.removeItem('preSessionMCPConfig');
  };

  /**
   * Reset current session
   * Saves long-term memory, then clears chat history but keeps RAG documents
   * 
   * @returns {Promise<string>} New session ID
   */
  const resetSession = async () => {
    try {
      setResetting(true);
      setError(null);

      // Save long-term memory before clearing chat history
      if (sessionId) {
        setSavingMemory(true);
        try {
          console.log('[useSession] Saving long-term memory before reset...');
          const memoryResult = await sessionService.saveActiveLongTermMemory(sessionId);
          
          if (memoryResult.saved) {
            console.log('[useSession] Long-term memory saved:', memoryResult.savedTypes);
          } else {
            console.log('[useSession] No long-term memory to save:', memoryResult.reason);
          }
        } catch (memErr) {
          // Don't block reset if memory save fails
          console.error('[useSession] Memory save failed (continuing with reset):', memErr);
        } finally {
          setSavingMemory(false);
        }
      }

      // Call backend reset endpoint (no parameters needed)
      const response = await sessionService.resetSession();
      const newSessionId = response.new_session_id;

      // Create session configuration with defaults
      await sessionService.createSessionConfig(newSessionId);
      console.log('[useSession] Session config created after reset');

      // Update local state
      clearChatMessages();
      setSessionId(newSessionId);
      
      // Mark session as ready
      setSessionReady(true);

      console.log('[useSession] Session reset:', { old: sessionId, new: newSessionId });
      return newSessionId;

    } catch (err) {
      console.error('[useSession] Failed to reset session:', err);
      setError(err.message);
      throw err;
    } finally {
      setResetting(false);
    }
  };

  /**
   * Delete all data (nuclear option)
   * Requires exact confirmation string: "DELETE" (case-sensitive)
   * 
   * @param {string} confirmation - Must be "DELETE"
   * @returns {Promise<Object>} Deletion counts
   */
  const deleteAll = async (confirmation) => {
    if (confirmation !== 'DELETE') {
      throw new Error('Invalid confirmation. Must be exactly "DELETE"');
    }

    try {
      setDeleting(true);
      setError(null);

      // Call backend delete-all endpoint
      const response = await sessionService.deleteAll(confirmation);

      // Clear localStorage
      localStorage.clear();

      console.log('[useSession] All data deleted:', response.deleted);
      
      // Create new session immediately after deletion
      const resetResponse = await sessionService.resetSession();
      const newSessionId = resetResponse.new_session_id;
      
      // Create session configuration with defaults
      await sessionService.createSessionConfig(newSessionId);
      console.log('[useSession] New session created after deleteAll:', newSessionId);

      // Update local state
      clearChatMessages();
      setSessionId(newSessionId);
      
      // Mark session as ready
      setSessionReady(true);

      return response.deleted;

    } catch (err) {
      console.error('[useSession] Failed to delete all:', err);
      setError(err.message);
      throw err;
    } finally {
      setDeleting(false);
    }
  };

  return {
    sessionId,
    initializing,
    resetting,
    deleting,
    savingMemory,
    error,
    resetSession,
    deleteAll,
  };
};
