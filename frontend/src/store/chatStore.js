import { create } from 'zustand';

/**
 * Chat Store - Manages global chat state
 * 
 * State:
 * - messages: Array of chat messages (user/assistant)
 * - sessionId: Current session ID (generated on first message)
 * - loading: Is a message being sent/received
 * - error: Error message if API call fails
 * - contextData: Last response context (for Context Window tab)
 *   - context_text: Full context sent to LLM
 *   - context_tokens: Total token count
 *   - token_breakdown: Token breakdown by component
 *   - max_context_tokens: Maximum tokens allowed
 * - ragSources: RAG sources from last chat response (for RAG Results tab)
 */
export const useChatStore = create((set, get) => ({
  // State
  messages: [],
  sessionId: null,
  sessionReady: false,
  loading: false,
  error: null,
  contextData: null,
  ragSources: null,

  // Actions
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      ...message,
      timestamp: new Date().toISOString(),
      id: `${Date.now()}-${Math.random()}`,
    }],
  })),

  setSessionId: (sessionId) => set({ sessionId }),
  
  setSessionReady: (sessionReady) => set({ sessionReady }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  setContextData: (contextData) => set({ contextData }),

  setRagSources: (ragSources) => set({ ragSources }),

  clearError: () => set({ error: null }),

  clearMessages: () => set({ messages: [] }),

  clearChatMessages: () => set({
    messages: [],
    loading: false,
    error: null,
    contextData: null,
    ragSources: null,
  }),

  resetChat: () => set({
    messages: [],
    sessionId: null,
    loading: false,
    error: null,
    contextData: null,
    ragSources: null,
  }),
}));
