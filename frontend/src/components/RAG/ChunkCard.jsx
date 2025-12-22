import { ScoreBar } from './ScoreBar';

/**
 * ChunkCard Component
 * Displays a single RAG chunk with metadata and relevance score
 */
export const ChunkCard = ({ chunk, index }) => {
  const { content, metadata, score, chunk_index } = chunk;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">
              {index + 1}
            </span>
            <h4 className="text-sm font-semibold text-gray-900 truncate">
              {metadata?.source || 'Unknown source'}
            </h4>
          </div>
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            {metadata?.namespace && (
              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded">
                {metadata.namespace}
              </span>
            )}
            {chunk_index !== undefined && (
              <span className="text-gray-400">Chunk #{chunk_index}</span>
            )}
          </div>
        </div>
      </div>

      {/* Score Bar */}
      <div className="mb-3">
        <ScoreBar score={score} />
      </div>

      {/* Content */}
      <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 leading-relaxed">
        <p className="whitespace-pre-wrap break-words">{content}</p>
      </div>

      {/* Additional Metadata */}
      {metadata && Object.keys(metadata).length > 2 && (
        <details className="mt-3">
          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
            View metadata
          </summary>
          <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
            <pre className="whitespace-pre-wrap break-words">
              {JSON.stringify(metadata, null, 2)}
            </pre>
          </div>
        </details>
      )}
    </div>
  );
};
