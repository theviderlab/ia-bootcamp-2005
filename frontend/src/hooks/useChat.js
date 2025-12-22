import { useChatStore } from '@store/chatStore';
import { chatService } from '@services/chatService';

/**
 * useChat Hook
 * 
 * Provides chat functionality with automatic state management.
 * Wraps chatService and syncs with chatStore.
 * 
 * Features:
 * - Send messages with auto session management
 * - Handle loading/error states
 * - Store context data for transparency
 * - Configuration is managed by backend from database (single source of truth)
 * 
 * @returns {Object} Chat state and actions
 */
export const useChat = () => {
  const {
    messages,
    sessionId,
    loading,
    error,
    addMessage,
    setSessionId,
    setLoading,
    setError,
    clearError,
    setContextData,
    setRagSources,
  } = useChatStore();

  /**
   * Send a message to the LLM
   * 
   * Backend reads all configuration (memory, RAG, tools) from database.
   * No need to pass configuration parameters - they are managed via /config endpoints.
   * 
   * @param {string} content - Message content
   * @param {Object} options - Optional generation parameters (temperature, max_tokens)
   */
  const sendMessage = async (content, options = {}) => {
    if (!content.trim()) return;

    // Clear any previous errors
    clearError();

    // Add user message immediately
    const userMessage = {
      role: 'user',
      content: content.trim(),
    };
    addMessage(userMessage);

    // Set loading state
    setLoading(true);

    try {
      // Build messages array for API - ONLY send the new user message
      // Backend handles all memory/context management
      const messagesForAPI = [{
        role: userMessage.role,
        content: userMessage.content,
      }];

      // Session should always exist (created on app load)
      if (!sessionId) {
        throw new Error('No session ID available. Session should be initialized on app load.');
      }

      console.log('[useChat] Sending message with session_id:', sessionId);

      // Call chat service - backend reads config from DB
      const response = await chatService.sendMessage(messagesForAPI, {
        session_id: sessionId,
        temperature: options.temperature,
        max_tokens: options.max_tokens,
        max_context_tokens: options.max_context_tokens,
        context_priority: options.context_priority,
      });

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.response,
      });

      // Store context data for Context Window tab
      setContextData({
        context_text: response.context_text,
        context_tokens: response.context_tokens,
        token_breakdown: response.token_breakdown,
        max_context_tokens: response.max_context_tokens,
        rag_sources: response.rag_sources,
        tools_used: response.tools_used,
        tool_calls: response.tool_calls,
      });
      
      // Store RAG sources separately for RAG Results tab
      if (response.rag_sources && response.rag_sources.length > 0) {
        setRagSources(response.rag_sources);
      }

    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err.message || 'Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    sessionId,
    loading,
    error,
    sendMessage,
    clearError,
  };
};
