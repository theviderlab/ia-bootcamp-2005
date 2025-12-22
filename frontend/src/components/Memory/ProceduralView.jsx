import { formatRelativeTime } from '@utils/formatters';

/**
 * ProceduralView Component
 * Displays procedural memory as list of learned patterns and workflows
 */
export const ProceduralView = ({ patterns }) => {
  if (patterns.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">⚙️</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Patterns Identified Yet</h3>
        <p className="text-gray-600">
          Repeated workflows and patterns will be learned and stored here over time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {patterns.map((pattern, index) => (
        <PatternCard key={pattern.id || index} pattern={pattern} />
      ))}
    </div>
  );
};

/**
 * PatternCard Component
 * Individual pattern display with frequency and usage stats
 */
const PatternCard = ({ pattern }) => {
  const lastUsed = pattern.last_used || pattern.timestamp || new Date().toISOString();
  const frequency = pattern.frequency || pattern.count || 0;
  const confidence = pattern.confidence || 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 
                  hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="text-2xl">🔄</div>
        
        <div className="flex-1">
          {/* Pattern Name */}
          <h4 className="font-semibold text-gray-900 mb-1">
            {pattern.name || pattern.title || 'Unnamed Pattern'}
          </h4>

          {/* Pattern Description */}
          {pattern.description && (
            <p className="text-sm text-gray-600 mb-3">
              {pattern.description}
            </p>
          )}

          {/* Steps (if available) */}
          {pattern.steps && pattern.steps.length > 0 && (
            <div className="mb-3">
              <div className="text-xs font-medium text-gray-500 uppercase mb-1">Steps:</div>
              <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                {pattern.steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-3 pt-3 border-t border-gray-100">
            {/* Frequency */}
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{frequency}</div>
              <div className="text-xs text-gray-500">Times Used</div>
            </div>

            {/* Last Used */}
            <div className="text-center">
              <div className="text-sm font-medium text-gray-900">
                {formatRelativeTime(lastUsed)}
              </div>
              <div className="text-xs text-gray-500">Last Used</div>
            </div>

            {/* Confidence */}
            {confidence > 0 && (
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-900">
                  {Math.round(confidence * 100)}%
                </div>
                <div className="text-xs text-gray-500">Confidence</div>
              </div>
            )}
          </div>

          {/* Confidence Bar */}
          {confidence > 0 && (
            <div className="mt-3">
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${getConfidenceColor(confidence)}`}
                    style={{ width: `${confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          {/* Tags */}
          {pattern.tags && pattern.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {pattern.tags.map((tag, idx) => (
                <span 
                  key={idx}
                  className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Get color class based on confidence level
 */
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'bg-green-600';
  if (confidence >= 0.5) return 'bg-yellow-500';
  return 'bg-red-500';
};

export default ProceduralView;
