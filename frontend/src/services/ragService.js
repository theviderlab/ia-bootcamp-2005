import apiClient from './api';
import { API_ENDPOINTS } from '@constants/api';

/**
 * RAG Service
 * Handles all RAG-related API calls including document upload,
 * namespace management, and document queries.
 */
export const ragService = {
  /**
   * Upload documents to RAG system
   * @param {Array<string>} documents - Array of document contents (as text)
   * @param {string} namespace - Namespace to store documents in
   * @param {number} chunkSize - Maximum characters per chunk
   * @param {number} chunkOverlap - Characters of overlap between chunks
   * @returns {Promise<Object>} Upload result
   */
  uploadDocuments: async (
    documents,
    namespace = 'default',
    chunkSize = 1000,
    chunkOverlap = 200
  ) => {
    const response = await apiClient.post(API_ENDPOINTS.ragDocuments, {
      documents,
      namespace,
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
    });
    return response.data;
  },

  /**
   * Upload entire directory to RAG system
   * @param {string} directory - Path to directory
   * @param {string} namespace - Namespace to store documents in
   * @param {boolean} recursive - Search subdirectories recursively
   * @param {number} chunkSize - Maximum characters per chunk
   * @param {number} chunkOverlap - Characters of overlap between chunks
   * @returns {Promise<Object>} Upload result
   */
  uploadDirectory: async (
    directory,
    namespace = 'default',
    recursive = true,
    chunkSize = 1000,
    chunkOverlap = 200
  ) => {
    const response = await apiClient.post(API_ENDPOINTS.ragDirectory, {
      directory,
      namespace,
      recursive,
      chunk_size: chunkSize,
      chunk_overlap: chunkOverlap,
    });
    return response.data;
  },

  /**
   * Query RAG system for relevant documents
   * @param {string} query - Search query
   * @param {number} topK - Number of results to return
   * @param {string} namespace - Namespace to search in
   * @returns {Promise<Object>} Query results
   */
  query: async (query, topK = 5, namespace = null) => {
    const payload = {
      query,
      top_k: topK,
    };
    if (namespace) {
      payload.namespace = namespace;
    }
    const response = await apiClient.post(API_ENDPOINTS.ragQuery, payload);
    return response.data;
  },

  /**
   * Get list of all namespaces
   * @returns {Promise<Object>} Namespaces data
   */
  getNamespaces: async () => {
    const response = await apiClient.get(API_ENDPOINTS.ragNamespaces);
    return response.data;
  },

  /**
   * Get list of documents
   * @param {string} namespace - Filter by namespace
   * @param {number} limit - Number of documents to return
   * @param {number} offset - Number of documents to skip
   * @returns {Promise<Object>} Documents data
   */
  getDocuments: async (namespace = null, limit = 100, offset = 0) => {
    const params = { limit, offset };
    if (namespace) {
      params.namespace = namespace;
    }
    const response = await apiClient.get(API_ENDPOINTS.ragDocuments, {
      params,
    });
    return response.data;
  },

  /**
   * Get statistics for a specific namespace
   * @param {string} namespace - Namespace to get stats for
   * @returns {Promise<Object>} Namespace statistics
   */
  getNamespaceStats: async (namespace) => {
    const response = await apiClient.get(
      API_ENDPOINTS.ragNamespaceStats(namespace)
    );
    return response.data;
  },

  /**
   * Delete a namespace and all its documents
   * @param {string} namespace - Namespace to delete
   * @returns {Promise<Object>} Deletion result
   */
  deleteNamespace: async (namespace) => {
    const response = await apiClient.delete(
      API_ENDPOINTS.ragNamespaceDelete(namespace)
    );
    return response.data;
  },

  /**
   * Update RAG configuration
   * @param {boolean} enabled - Enable/disable RAG
   * @param {Array<string>} namespaces - Selected namespaces
   * @returns {Promise<Object>} Configuration update result
   */
  updateConfig: async (enabled, namespaces = []) => {
    const response = await apiClient.put(API_ENDPOINTS.CONFIG_RAG, {
      enabled,
      namespaces,
    });
    return response.data;
  },
};
