import { useState, useEffect, useCallback } from 'react';
import { ragService } from '@services/ragService';
import { useChatStore } from '@store/chatStore';

/**
 * Custom hook for managing RAG state and operations
 * Handles RAG configuration, document upload, and namespace management
 */
export const useRAG = () => {
  const { sessionId, sessionReady } = useChatStore();

  // RAG configuration state
  const [ragEnabled, setRagEnabled] = useState(false);
  const [selectedNamespaces, setSelectedNamespaces] = useState([]);

  // RAG data state
  const [namespaces, setNamespaces] = useState([]);
  const [documents, setDocuments] = useState([]);

  // Upload state
  const [uploadProgress, setUploadProgress] = useState({
    uploading: false,
    current: 0,
    total: 0,
    fileName: '',
  });

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load RAG configuration from backend
   */
  const loadConfig = useCallback(async () => {
    if (!sessionId) {
      // No session yet, check localStorage for pre-session config
      const preSessionConfig = localStorage.getItem('preSessionRagConfig');

      if (preSessionConfig) {
    try {
          const config = JSON.parse(preSessionConfig);

          setRagEnabled(config.enabled ?? false);
          setSelectedNamespaces(config.namespaces ?? []);
          return;
        } catch (e) {
          console.error('Failed to parse pre-session RAG config:', e);
        }
      }

      // Default: RAG disabled
      setRagEnabled(false);
      setSelectedNamespaces([]);
      return;
    }

    try {
      // Import memoryService dynamically to get config
      const { memoryService } = await import('@services/memoryService');
      const response = await memoryService.getConfig(sessionId);
      const config = response.config;

      setRagEnabled(config.rag?.enable_rag ?? false);
      setSelectedNamespaces(config.rag?.namespaces ?? []);

      // Clear pre-session config after successful sync
      localStorage.removeItem('preSessionRagConfig');
    } catch (err) {
      console.error('Failed to load RAG config:', err);
      setRagEnabled(false);
      setSelectedNamespaces([]);
    }
  }, [sessionId]);

  /**
   * Update RAG configuration on backend
   */
  const updateConfig = useCallback(
    async (enabled, namespaces = []) => {
      if (!sessionId) {
        console.warn(
          'No session ID available, RAG config will be applied when session starts'
        );

        // Save to localStorage for application after session creation
        const preSessionConfig = {
          enabled,
          namespaces,
          timestamp: Date.now(),
        };
        localStorage.setItem('preSessionRagConfig', JSON.stringify(preSessionConfig));

        // Update local state
        setRagEnabled(enabled);
        setSelectedNamespaces(namespaces);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const response = await ragService.updateConfig(sessionId, enabled, namespaces);

        // Update local state from backend response (same pattern as useMemory)
        if (response && response.config && response.config.rag) {
          const rag = response.config.rag;
          setRagEnabled(rag.enable_rag ?? false);
          setSelectedNamespaces(rag.namespaces ?? []);
        } else {
          console.warn('[useRAG] Backend response missing config.rag, using sent values');
          setRagEnabled(enabled);
          setSelectedNamespaces(namespaces);
        }
      } catch (err) {
        console.error('Failed to update RAG config:', err);
        setError('Failed to update RAG configuration');
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  /**
   * Toggle RAG enabled/disabled
   */
  const toggleRAG = useCallback(
    async (enabled) => {
      await updateConfig(enabled, selectedNamespaces);
    },
    [updateConfig, selectedNamespaces]
  );

  /**
   * Toggle a specific namespace
   */
  const toggleNamespace = useCallback(
    async (namespace) => {
      const newNamespaces = selectedNamespaces.includes(namespace)
        ? selectedNamespaces.filter((ns) => ns !== namespace)
        : [...selectedNamespaces, namespace];

      await updateConfig(ragEnabled, newNamespaces);
    },
    [ragEnabled, selectedNamespaces, updateConfig]
  );

  /**
   * Fetch all namespaces from backend
   */
  const fetchNamespaces = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await ragService.getNamespaces();
      setNamespaces(response.namespaces || []);
    } catch (err) {
      console.error('Failed to fetch namespaces:', err);
      setError('Failed to load namespaces');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch documents from backend
   */
  const fetchDocuments = useCallback(
    async (namespace = null, limit = 100, offset = 0) => {
      try {
        setLoading(true);
        setError(null);

        const response = await ragService.getDocuments(namespace, limit, offset);
        setDocuments(response.documents || []);
      } catch (err) {
        console.error('Failed to fetch documents:', err);
        setError('Failed to load documents');
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Upload single file to RAG system
   * @param {File} file - File to upload
   * @param {string} namespace - Namespace to store document in
   * @param {number} chunkSize - Chunk size in characters
   * @param {number} chunkOverlap - Overlap in characters
   */
  const uploadFile = useCallback(
    async (file, namespace = 'default', chunkSize = 1000, chunkOverlap = 200) => {
      const maxFileSize = 10 * 1024 * 1024; // 10MB

      // Validate file
      // Check file size
      if (file.size > maxFileSize) {
        setError(`File "${file.name}" exceeds 10MB limit`);
        return;
      }

      // Check file extension
      const validExtensions = ['.txt', '.md', '.log'];
      const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
      if (!validExtensions.includes(fileExtension)) {
        setError(
          `File "${file.name}" has unsupported format. Only .txt, .md, .log are allowed`
        );
        return;
      }

      try {
        setUploadProgress({
          uploading: true,
          current: 1,
          total: 1,
          fileName: file.name,
        });

        // Read file content using FileReader API
        const content = await readFileContent(file);

        // Upload to backend with custom chunk settings
        await ragService.uploadDocuments([content], namespace, chunkSize, chunkOverlap);

        // Upload complete
        setUploadProgress({
          uploading: false,
          current: 0,
          total: 0,
          fileName: '',
        });

        // Refresh namespaces and documents
        await fetchNamespaces();
        await fetchDocuments(namespace);
      } catch (err) {
        console.error(`Failed to upload file "${file.name}":`, err);
        setError(`Failed to upload "${file.name}": ${err.message}`);
        setUploadProgress({
          uploading: false,
          current: 0,
          total: 0,
          fileName: '',
        });
      }
    },
    [fetchNamespaces, fetchDocuments]
  );

  /**
   * Delete a namespace
   * @param {string} namespace - Namespace to delete
   */
  const deleteNamespace = useCallback(
    async (namespace) => {
      try {
        setLoading(true);
        setError(null);

        await ragService.deleteNamespace(namespace);

        // Remove from selected namespaces if present
        if (selectedNamespaces.includes(namespace)) {
          const newNamespaces = selectedNamespaces.filter((ns) => ns !== namespace);
          await updateConfig(ragEnabled, newNamespaces);
        }

        // Refresh namespaces list
        await fetchNamespaces();
      } catch (err) {
        console.error(`Failed to delete namespace "${namespace}":`, err);
        setError(`Failed to delete namespace "${namespace}"`);
      } finally {
        setLoading(false);
      }
    },
    [selectedNamespaces, ragEnabled, updateConfig, fetchNamespaces]
  );

  /**
   * Load config when sessionId is available
   */
  useEffect(() => {
    if (sessionId) {
      loadConfig();
    }
  }, [sessionId]);

  /**
   * Fetch namespaces on mount
   */
  useEffect(() => {
    fetchNamespaces();
  }, [fetchNamespaces]);

  return {
    // State
    ragEnabled,
    selectedNamespaces,
    namespaces,
    documents,
    uploadProgress,
    loading,
    error,

    // Actions
    toggleRAG,
    toggleNamespace,
    fetchNamespaces,
    fetchDocuments,
    uploadFile,
    deleteNamespace,
    loadConfig,
  };
};

/**
 * Helper function to read file content using FileReader API
 * @param {File} file - File to read
 * @returns {Promise<string>} File content as text
 */
function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (event) => {
      resolve(event.target.result);
    };

    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };

    reader.readAsText(file);
  });
}
