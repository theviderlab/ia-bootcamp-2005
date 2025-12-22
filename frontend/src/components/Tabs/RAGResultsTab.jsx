import { useState, useMemo } from 'react';
import { useChatStore } from '@store/chatStore';
import { ChunkCard } from '@components/RAG/ChunkCard';

/**
 * RAGResultsTab Component
 * Displays retrieved RAG chunks with relevance scores
 */
export const RAGResultsTab = () => {
  const { ragSources } = useChatStore();
  
  const [selectedNamespace, setSelectedNamespace] = useState('all');
  const [sortBy, setSortBy] = useState('score'); // 'score' or 'index'

  // Get unique namespaces from sources
  const namespaces = useMemo(() => {
    if (!ragSources || ragSources.length === 0) return [];
    
    const nsSet = new Set();
    ragSources.forEach(source => {
      if (source.metadata?.namespace) {
        nsSet.add(source.metadata.namespace);
      }
    });
    
    return Array.from(nsSet).sort();
  }, [ragSources]);

  // Filter and sort sources
  const filteredSources = useMemo(() => {
    if (!ragSources) return [];
    
    let filtered = ragSources;
    
    // Filter by namespace
    if (selectedNamespace !== 'all') {
      filtered = filtered.filter(
        source => source.metadata?.namespace === selectedNamespace
      );
    }
    
    // Sort
    if (sortBy === 'score') {
      filtered = [...filtered].sort((a, b) => b.score - a.score);
    } else if (sortBy === 'index') {
      filtered = [...filtered].sort((a, b) => 
        (a.chunk_index ?? 0) - (b.chunk_index ?? 0)
      );
    }
    
    return filtered;
  }, [ragSources, selectedNamespace, sortBy]);

  // Empty state
  if (!ragSources || ragSources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No RAG Results Yet
        </h3>
        <p className="text-sm text-gray-600 max-w-md">
          Enable RAG in the sidebar and upload documents to see retrieved chunks here.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">RAG Results</h2>
          <span className="text-sm text-gray-600">
            {filteredSources.length} of {ragSources.length} chunks
          </span>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3">
          {/* Namespace Filter */}
          {namespaces.length > 1 && (
            <div className="flex-1">
              <label className="block text-xs text-gray-600 mb-1">Namespace</label>
              <select
                value={selectedNamespace}
                onChange={(e) => setSelectedNamespace(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Namespaces</option>
                {namespaces.map(ns => (
                  <option key={ns} value={ns}>{ns}</option>
                ))}
              </select>
            </div>
          )}

          {/* Sort By */}
          <div className="flex-1">
            <label className="block text-xs text-gray-600 mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="score">Relevance Score</option>
              <option value="index">Chunk Index</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {filteredSources.map((source, index) => (
            <ChunkCard
              key={`${source.metadata?.source}-${source.chunk_index}-${index}`}
              chunk={source}
              index={index}
            />
          ))}
        </div>
      </div>

      {/* Footer Info */}
      <div className="flex-shrink-0 border-t border-gray-200 p-3 bg-gray-50">
        <p className="text-xs text-gray-600">
          💡 <strong>Tip:</strong> Higher scores indicate more relevant chunks. Chunks are retrieved based on semantic similarity to your query.
        </p>
      </div>
    </div>
  );
};
