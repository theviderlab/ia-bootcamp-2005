import { useState, useEffect, useCallback } from 'react';
import { memoryService } from '@services/memoryService';
import { useChatStore } from '@store/chatStore';
import { ALL_MEMORY_TYPES, LONG_TERM_MEMORY_TYPES } from '@constants/memoryTypes';

/**
 * Custom hook for managing memory state and operations
 * Handles memory configuration, data fetching, and auto-refresh
 */
export const useMemory = () => {
  const { sessionId, sessionReady } = useChatStore();
  
  // Memory configuration state
  const [memoryEnabled, setMemoryEnabled] = useState(false);
  const [enabledTypes, setEnabledTypes] = useState([]);
  const [shortTermEnabled, setShortTermEnabled] = useState(true);
  
  // Memory data state
  const [shortTermMemory, setShortTermMemory] = useState([]);
  const [longTermMemory, setLongTermMemory] = useState({
    semantic_facts: [],
    episodic_episodes: [],
    profile_data: {},
    procedural_patterns: [],
  });
  const [memoryStats, setMemoryStats] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  /**
   * Load memory configuration from backend
   */
  const loadConfig = useCallback(async () => {
    if (!sessionId) {
      // No session yet, check localStorage for pre-session config
      const preSessionConfig = localStorage.getItem('preSessionMemoryConfig');
      
      if (preSessionConfig) {
        try {
          const config = JSON.parse(preSessionConfig);
          setShortTermEnabled(config.shortTerm ?? true);
          setEnabledTypes(config.types ?? ALL_MEMORY_TYPES.filter(t => t !== 'short_term'));
          setMemoryEnabled(config.shortTerm || config.types.length > 0);
          return;
        } catch (e) {
          console.error('Failed to parse pre-session config:', e);
        }
      }
      
      // Use backend-aligned defaults: ALL MEMORY ENABLED
      setMemoryEnabled(true);
      setEnabledTypes(ALL_MEMORY_TYPES.filter(t => t !== 'short_term'));
      setShortTermEnabled(true);
      return;
    }
    
    try {
      const response = await memoryService.getConfig(sessionId);
      
      // Handle case where config might not be created yet
      if (!response || !response.config || !response.config.memory) {
        console.warn('[useMemory] Config not ready yet, using defaults');
        setMemoryEnabled(true);
        setEnabledTypes(ALL_MEMORY_TYPES.filter(t => t !== 'short_term'));
        setShortTermEnabled(true);
        return;
      }
      
      const config = response.config;
      const memory = config.memory;
      
      setShortTermEnabled(memory.enable_short_term ?? true);
      
      // Determine which types are enabled
      const types = [];
      if (memory.enable_semantic) types.push('semantic');
      if (memory.enable_episodic) types.push('episodic');
      if (memory.enable_profile) types.push('profile');
      if (memory.enable_procedural) types.push('procedural');
      
      setEnabledTypes(types);
      setMemoryEnabled(types.length > 0 || memory.enable_short_term);
      
      // Clear pre-session config after successful sync
      localStorage.removeItem('preSessionMemoryConfig');
    } catch (err) {
      console.error('Failed to load memory config:', err);
      // Set backend-aligned defaults on error
      setMemoryEnabled(true);
      setEnabledTypes(ALL_MEMORY_TYPES.filter(t => t !== 'short_term'));
      setShortTermEnabled(true);
    }
  }, [sessionId]);

  /**
   * Update memory configuration on backend
   */
  const updateConfig = useCallback(async (types, shortTerm = true) => {
    if (!sessionId) {
      console.warn('No session ID available, config will be applied when session starts');
      
      // Save to localStorage for application after session creation
      const preSessionConfig = {
        types,
        shortTerm,
        timestamp: Date.now(),
      };
      localStorage.setItem('preSessionMemoryConfig', JSON.stringify(preSessionConfig));
      
      // Update local state
      setEnabledTypes(types);
      setShortTermEnabled(shortTerm);
      setMemoryEnabled(types.length > 0 || shortTerm);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Convert types array to individual flags
      const enableSemantic = types.includes('semantic');
      const enableEpisodic = types.includes('episodic');
      const enableProfile = types.includes('profile');
      const enableProcedural = types.includes('procedural');
      
      const response = await memoryService.updateConfig(
        sessionId,
        shortTerm,
        enableSemantic,
        enableEpisodic,
        enableProfile,
        enableProcedural
      );
      
      // Update local state from backend response
      const memory = response.config.memory;
      setShortTermEnabled(memory.enable_short_term);
      
      const updatedTypes = [];
      if (memory.enable_semantic) updatedTypes.push('semantic');
      if (memory.enable_episodic) updatedTypes.push('episodic');
      if (memory.enable_profile) updatedTypes.push('profile');
      if (memory.enable_procedural) updatedTypes.push('procedural');
      
      setEnabledTypes(updatedTypes);
      setMemoryEnabled(updatedTypes.length > 0 || memory.enable_short_term);
      
      // Refresh data after config change
      if (updatedTypes.length > 0) {
        await refreshMemoryData();
      }
    } catch (err) {
      console.error('Failed to update memory config:', err);
      setError('Failed to update memory configuration');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /**
   * Toggle a specific memory type
   */
  const toggleMemoryType = useCallback(async (type) => {
    // Handle short-term separately
    if (type === 'short_term') {
      await updateConfig(enabledTypes, !shortTermEnabled);
      return;
    }
    
    // Handle long-term types
    const newTypes = enabledTypes.includes(type)
      ? enabledTypes.filter(t => t !== type)
      : [...enabledTypes, type];
    
    await updateConfig(newTypes, shortTermEnabled);
  }, [enabledTypes, shortTermEnabled, updateConfig]);

  /**
   * Toggle all memory types at once (master toggle)
   */
  const toggleAllMemoryTypes = useCallback(async (enabled) => {
    const types = enabled ? ALL_MEMORY_TYPES.filter(t => t !== 'short_term') : [];
    await updateConfig(types, enabled);
  }, [updateConfig]);

  /**
   * Fetch short-term memory (conversation history)
   */
  const fetchShortTermMemory = useCallback(async (limit = 20) => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await memoryService.getHistory(sessionId, limit);
      setShortTermMemory(data.messages || []);
    } catch (err) {
      console.error('Failed to fetch short-term memory:', err);
      setError('Failed to load conversation history');
      setShortTermMemory([]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  /**
   * Fetch long-term memory (semantic, episodic, profile, procedural)
   */
  const fetchLongTermMemory = useCallback(async () => {
    if (!sessionId || enabledTypes.length === 0) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const data = await memoryService.getContext(sessionId, enabledTypes);
      setLongTermMemory({
        semantic_facts: data.semantic_facts || [],
        episodic_episodes: data.episodic_episodes || [],
        profile_data: data.profile_data || {},
        procedural_patterns: data.procedural_patterns || [],
      });
    } catch (err) {
      console.error('Failed to fetch long-term memory:', err);
      setError('Failed to load memory data');
      setLongTermMemory({
        semantic_facts: [],
        episodic_episodes: [],
        profile_data: {},
        procedural_patterns: [],
      });
    } finally {
      setLoading(false);
    }
  }, [sessionId, enabledTypes]);

  /**
   * Fetch memory statistics
   */
  const fetchMemoryStats = useCallback(async () => {
    if (!sessionId) return;
    
    try {
      const stats = await memoryService.getStats(sessionId);
      setMemoryStats(stats);
    } catch (err) {
      console.error('Failed to fetch memory stats:', err);
      setMemoryStats(null);
    }
  }, [sessionId]);

  /**
   * Search through memory
   */
  const searchMemory = useCallback(async (query, topK = 10) => {
    if (!sessionId || !query.trim()) {
      setSearchResults([]);
      return;
    }
    
    try {
      setSearchLoading(true);
      setError(null);
      
      const data = await memoryService.search(query, sessionId, topK);
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Failed to search memory:', err);
      setError('Failed to search memory');
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  }, [sessionId]);

  /**
   * Clear search results
   */
  const clearSearch = useCallback(() => {
    setSearchResults([]);
  }, []);

  /**
   * Refresh all memory data
   */
  const refreshMemoryData = useCallback(async () => {
    if (!sessionId || !memoryEnabled) return;
    
    await Promise.all([
      fetchShortTermMemory(),
      fetchLongTermMemory(),
      fetchMemoryStats(),
    ]);
  }, [sessionId, memoryEnabled, fetchShortTermMemory, fetchLongTermMemory, fetchMemoryStats]);

  /**
   * Clear memory for current session
   */
  const clearMemory = useCallback(async () => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      await memoryService.clearMemory(sessionId);
      
      // Reset local state
      setShortTermMemory([]);
      setLongTermMemory({
        semantic_facts: [],
        episodic_episodes: [],
        profile_data: {},
        procedural_patterns: [],
      });
      setMemoryStats(null);
    } catch (err) {
      console.error('Failed to clear memory:', err);
      setError('Failed to clear memory');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Load configuration on mount and when sessionId changes
  useEffect(() => {
    // Only load config when session is fully initialized
    if (sessionReady) {
      loadConfig();
    }
  }, [loadConfig, sessionReady]);

  // Auto-refresh memory data when configuration changes or after messages
  useEffect(() => {
    if (memoryEnabled && sessionId) {
      refreshMemoryData();
    }
  }, [memoryEnabled, sessionId, refreshMemoryData]);

  return {
    // Configuration state
    memoryEnabled,
    enabledTypes,
    shortTermEnabled,
    
    // Data state
    shortTermMemory,
    longTermMemory,
    memoryStats,
    searchResults,
    
    // UI state
    loading,
    error,
    searchLoading,
    
    // Actions
    toggleMemoryType,
    toggleAllMemoryTypes,
    updateConfig,
    fetchShortTermMemory,
    fetchLongTermMemory,
    fetchMemoryStats,
    refreshMemoryData,
    searchMemory,
    clearSearch,
    clearMemory,
  };
};

export default useMemory;
