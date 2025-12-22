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
   * @param {string} content - Message content
   * @param {Object} options - Chat options (memory, RAG, tools)
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

      // Build config from options
      const memoryConfig = {
        use_memory: options.useMemory ?? true,
        memory_types: options.memoryTypes ?? ['semantic', 'episodic', 'profile', 'procedural'],
      };
      
      const ragConfig = {
        use_rag: options.useRAG ?? false,
        rag_namespaces: options.ragNamespaces ?? [],
      };

      // Call chat service with session ID
      const response = await chatService.sendMessage(messagesForAPI, {
        session_id: sessionId,
        use_memory: memoryConfig.use_memory,
        memory_types: memoryConfig.memory_types,
        use_rag: ragConfig.use_rag,
        rag_namespaces: ragConfig.rag_namespaces,
        use_tools: options.useTools ?? false,
        available_tools: options.availableTools ?? null,
        ...options,
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
