/**
 * API Configuration Constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Health & Info
  health: '/health',
  root: '/',

  // LLM
  generate: '/llm/generate',
  chat: '/llm/chat',

  // RAG
  ragQuery: '/llm/rag/query',
  ragDocuments: '/llm/rag/documents',
  ragDirectory: '/llm/rag/directory',
  ragNamespaces: '/llm/rag/namespaces',
  ragNamespaceStats: (namespace) => `/llm/rag/namespace/${namespace}/stats`,
  ragNamespaceDelete: (namespace) => `/llm/rag/namespace/${namespace}`,

  // Memory
  MEMORY_CONTEXT: '/llm/memory/context',
  MEMORY_HISTORY: '/llm/memory/history',
  MEMORY_STATS: '/llm/memory/stats',
  MEMORY_SEARCH: '/llm/memory/search',
  MEMORY_SESSION_DELETE: '/llm/memory/session',
  
  // Long-term Memory Extraction
  MEMORY_PROFILE_EXTRACT: '/llm/memory/profile/extract',
  MEMORY_SEMANTIC_EXTRACT: '/llm/memory/semantic/extract',
  MEMORY_EPISODIC_EXTRACT: '/llm/memory/episodic/extract',
  MEMORY_PROCEDURAL_EXTRACT: '/llm/memory/procedural/extract',

  // Configuration
  CONFIG_STATUS: '/config/status',
  CONFIG_SESSION: '/config/session',
  CONFIG_MEMORY: '/config/memory',
  CONFIG_RAG: '/config/rag',

  // Session
  sessionReset: '/session/reset',
  sessionResetAll: '/session/reset-all',

  // MCP
  mcpTools: '/mpc/tools',
  mcpToolNames: '/mpc/tools/names',
  mcpTool: (toolName) => `/mpc/tools/${toolName}`,
};

export const DEFAULT_CONFIG = {
  sessionTimeout: import.meta.env.VITE_DEFAULT_SESSION_TIMEOUT || 3600000,
  enableMCP: import.meta.env.VITE_ENABLE_MCP === 'true',
  debugMode: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',
};
