import { useState, useCallback } from 'react';
import { useRAG } from '@hooks/useRAG';
import { FileUploader } from '@components/RAG/FileUploader';

/**
 * RAGSection Component
 * Sidebar section for managing RAG documents and namespaces
 * Provides file upload and namespace toggle functionality
 */
export const RAGSection = () => {
  const {
    ragEnabled,
    selectedNamespaces,
    namespaces,
    uploadProgress,
    loading,
    error,
    toggleRAG,
    toggleNamespace,
    uploadFile,
    deleteNamespace,
    fetchNamespaces,
  } = useRAG();

  const [chunkSize, setChunkSize] = useState(1000);
  const [overlapPercent, setOverlapPercent] = useState(20);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [namespaceCounter, setNamespaceCounter] = useState({});

  // Calculate overlap from percentage
  const chunkOverlap = Math.round((chunkSize * overlapPercent) / 100);

  const handleMasterToggle = async () => {
    await toggleRAG(!ragEnabled);
  };

  const handleNamespaceToggle = async (namespace) => {
    await toggleNamespace(namespace);
  };

  const handleFilesSelected = async (files) => {
    const fileArray = Array.from(files);
    
    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i];
      
      // Generate namespace from filename (without extension)
      let baseNamespace = file.name.replace(/\.[^/.]+$/, '');
      
      // Handle namespace collisions by adding numeric suffix
      let namespace = baseNamespace;
      let counter = namespaceCounter[baseNamespace] || 0;
      
      if (counter > 0) {
        namespace = `${baseNamespace}_${counter}`;
      }
      
      // Update counter for this base namespace
      setNamespaceCounter(prev => ({
        ...prev,
        [baseNamespace]: counter + 1
      }));
      
      // Upload single file with its own namespace
      await uploadFile(file, namespace, chunkSize, chunkOverlap);
    }
  };

  const handleDeleteNamespace = async (namespace) => {
    if (showDeleteConfirm === namespace) {
      await deleteNamespace(namespace);
      setShowDeleteConfirm(null);
    } else {
      setShowDeleteConfirm(namespace);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(null);
  };

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">RAG (Knowledge Base)</h3>
        {loading && (
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        )}
      </div>

      {/* Master Toggle */}
      <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div>
          <label htmlFor="rag-toggle" className="font-medium text-gray-900 dark:text-white cursor-pointer">
            Enable RAG
          </label>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Use documents for context
          </p>
        </div>
        <button
          id="rag-toggle"
          role="switch"
          aria-checked={ragEnabled}
          onClick={handleMasterToggle}
          disabled={loading}
          className={`
            relative inline-flex h-6 w-11 items-center rounded-full transition-colors
            ${ragEnabled ? 'bg-blue-600' : 'bg-gray-300'}
            ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          <span
            className={`
              inline-block h-4 w-4 transform rounded-full bg-white transition-transform
              ${ragEnabled ? 'translate-x-6' : 'translate-x-1'}
            `}
          />
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* File Upload Section */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Upload Documents
        </label>
        
        {/* Chunk Size Configuration */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Chunk Size
            </label>
            <span className="text-xs text-gray-500 dark:text-gray-400">{chunkSize} chars</span>
          </div>
          <input
            type="range"
            min="100"
            max="4000"
            step="100"
            value={chunkSize}
            onChange={(e) => setChunkSize(Number(e.target.value))}
            disabled={uploadProgress.uploading}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500">
            <span>100</span>
            <span>4000</span>
          </div>
        </div>

        {/* Overlap Percentage Configuration */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Overlap ({overlapPercent}%)
            </label>
            <span className="text-xs text-gray-500 dark:text-gray-400">{chunkOverlap} chars</span>
          </div>
          <input
            type="range"
            min="0"
            max="50"
            step="5"
            value={overlapPercent}
            onChange={(e) => setOverlapPercent(Number(e.target.value))}
            disabled={uploadProgress.uploading}
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500">
            <span>0%</span>
            <span>50%</span>
          </div>
        </div>

        {/* Info about automatic namespace */}
        <div className="text-xs text-gray-500 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 p-2 rounded border border-blue-100 dark:border-blue-800">
          💡 Files will be uploaded with filename as namespace
        </div>

        {/* File Uploader */}
        <FileUploader
          onFilesSelected={handleFilesSelected}
          disabled={uploadProgress.uploading}
        />

        {/* Upload Progress */}
        {uploadProgress.uploading && (
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                Uploading {uploadProgress.fileName}...
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400">
                {uploadProgress.current} / {uploadProgress.total}
              </p>
            </div>
            <div className="w-full bg-blue-200 dark:bg-blue-900 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${(uploadProgress.current / uploadProgress.total) * 100}%`,
                }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Namespace List */}
      {namespaces.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Select Namespaces
            </label>
            <button
              onClick={fetchNamespaces}
              className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
              disabled={loading}
            >
              🔄 Refresh
            </button>
          </div>

          <div className="space-y-1 max-h-64 overflow-y-auto">
            {namespaces.map((ns) => (
              <div
                key={ns.name}
                className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center space-x-2 flex-1">
                  <button
                    role="switch"
                    aria-checked={selectedNamespaces.includes(ns.name)}
                    onClick={() => handleNamespaceToggle(ns.name)}
                    disabled={!ragEnabled || loading}
                    className={`
                      relative inline-flex h-5 w-9 items-center rounded-full transition-colors
                      ${selectedNamespaces.includes(ns.name) ? 'bg-blue-600' : 'bg-gray-300'}
                      ${!ragEnabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    <span
                      className={`
                        inline-block h-3 w-3 transform rounded-full bg-white transition-transform
                        ${selectedNamespaces.includes(ns.name) ? 'translate-x-5' : 'translate-x-1'}
                      `}
                    />
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {ns.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {ns.document_count} docs • {ns.chunk_count} chunks
                    </p>
                  </div>
                </div>
                
                {/* Delete Button */}
                {showDeleteConfirm === ns.name ? (
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleDeleteNamespace(ns.name)}
                      className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                      disabled={loading}
                    >
                      Confirm
                    </button>
                    <button
                      onClick={handleCancelDelete}
                      className="px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                      disabled={loading}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setShowDeleteConfirm(ns.name)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete namespace"
                    disabled={loading}
                  >
                    🗑️
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {namespaces.length === 0 && !loading && (
        <div className="text-center p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400">📚 No documents uploaded yet</p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            Upload documents to get started
          </p>
        </div>
      )}

      {/* Info Text */}
      {ragEnabled && namespaces.length > 0 && (
        <div className="text-xs text-gray-500 dark:text-gray-400 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
          <p className="font-medium text-blue-900 dark:text-blue-300 mb-1">💡 RAG Tips:</p>
          <ul className="space-y-1 ml-4 list-disc">
            <li>Select namespaces to include in chat context</li>
            <li>Upload related documents to same namespace</li>
            <li>Delete unused namespaces to keep organized</li>
          </ul>
        </div>
      )}
    </div>
  );
};
