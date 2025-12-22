import { useState, useCallback } from 'react';
import { useMemory } from '@hooks/useMemory';
import { MEMORY_TYPES, MEMORY_TYPE_LABELS } from '@constants/memoryTypes';
import { SemanticView } from '@components/Memory/SemanticView';
import { EpisodicView } from '@components/Memory/EpisodicView';
import { ProfileView } from '@components/Memory/ProfileView';
import { ProceduralView } from '@components/Memory/ProceduralView';

/**
 * LongTermMemoryTab Component
 * Main tab for displaying long-term memory with type selector
 * Shows semantic, episodic, profile, and procedural memory
 */
export const LongTermMemoryTab = () => {
  const {
    longTermMemory,
    enabledTypes,
    loading,
    error,
    fetchLongTermMemory,
    searchMemory,
    searchResults,
    searchLoading,
    clearSearch,
  } = useMemory();

  // Determine available memory types based on enabled types
  const availableTypes = enabledTypes.filter(type => 
    Object.values(MEMORY_TYPES).includes(type)
  );

  // Set default selected type to first available type
  const [selectedType, setSelectedType] = useState(
    availableTypes.length > 0 ? availableTypes[0] : MEMORY_TYPES.SEMANTIC
  );

  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Handle search with debouncing
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    
    if (query.trim() === '') {
      clearSearch();
      return;
    }

    // Debounce search - wait 500ms after user stops typing
    const timeoutId = setTimeout(() => {
      searchMemory(query, 10);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchMemory, clearSearch]);

  if (loading && Object.values(longTermMemory).every(v => 
    Array.isArray(v) ? v.length === 0 : Object.keys(v).length === 0
  )) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchLongTermMemory} />;
  }

  if (availableTypes.length === 0) {
    return <NoTypesEnabledState />;
  }

  // Get data for selected type (use search results if searching)
  const displayData = searchQuery.trim() !== '' && searchResults.length > 0
    ? { [selectedType]: searchResults }
    : longTermMemory;

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Long-term Memory</h2>
          <div className="text-sm text-gray-600">
            Persistent memory stored across sessions
          </div>
        </div>

        {/* Memory Type Selector */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
          <div className="flex gap-2 overflow-x-auto">
            {availableTypes.map(type => (
              <button
                key={type}
                onClick={() => {
                  setSelectedType(type);
                  setSearchQuery('');
                  clearSearch();
                }}
                className={`
                  px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors
                  ${selectedType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {MEMORY_TYPE_LABELS[type]}
              </button>
            ))}
          </div>
        </div>

        {/* Memory Type Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {selectedType === MEMORY_TYPES.SEMANTIC && (
            <SemanticView
              facts={displayData.semantic_facts || []}
              onSearch={handleSearch}
              searchQuery={searchQuery}
              searchLoading={searchLoading}
            />
          )}

          {selectedType === MEMORY_TYPES.EPISODIC && (
            <EpisodicView
              episodes={displayData.episodic_episodes || []}
            />
          )}

          {selectedType === MEMORY_TYPES.PROFILE && (
            <ProfileView
              profileData={displayData.profile_data || {}}
            />
          )}

          {selectedType === MEMORY_TYPES.PROCEDURAL && (
            <ProceduralView
              patterns={displayData.procedural_patterns || []}
            />
          )}
        </div>

        {/* Refresh Button */}
        <div className="flex justify-center">
          <button
            onClick={fetchLongTermMemory}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                     flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Refreshing...
              </>
            ) : (
              <>
                <span>🔄</span>
                Refresh
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * LoadingState Component
 */
const LoadingState = () => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
      <p className="text-gray-600">Loading long-term memory...</p>
    </div>
  </div>
);

/**
 * ErrorState Component
 */
const ErrorState = ({ message, onRetry }) => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center max-w-md">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Memory</h3>
      <p className="text-gray-600 mb-4">{message}</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

/**
 * NoTypesEnabledState Component
 */
const NoTypesEnabledState = () => (
  <div className="h-full flex items-center justify-center bg-gray-50">
    <div className="text-center max-w-md">
      <div className="text-6xl mb-4">🧠</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">No Memory Types Enabled</h3>
      <p className="text-gray-600">
        Enable memory types in the sidebar to start storing long-term memories.
      </p>
    </div>
  </div>
);

export default LongTermMemoryTab;
