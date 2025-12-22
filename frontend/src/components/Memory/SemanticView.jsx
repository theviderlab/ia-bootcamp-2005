import { formatRelativeTime } from '@utils/formatters';

/**
 * SemanticView Component
 * Displays semantic memory as fact cards with search functionality
 */
export const SemanticView = ({ facts, onSearch, searchQuery, searchLoading }) => {
  if (facts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🧠</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Semantic Facts Yet</h3>
        <p className="text-gray-600">
          Start chatting to extract and store facts and knowledge from conversations.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="sticky top-0 bg-white z-10 pb-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search semantic facts..."
            value={searchQuery}
            onChange={(e) => onSearch(e.target.value)}
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg 
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
          {searchLoading && (
            <div className="absolute right-3 top-2.5">
              <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>
      </div>

      {/* Fact Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {facts.map((fact, index) => (
          <FactCard key={fact.id || index} fact={fact} />
        ))}
      </div>
    </div>
  );
};

/**
 * FactCard Component
 * Individual semantic fact card
 */
const FactCard = ({ fact }) => {
  const timestamp = fact.timestamp || fact.created_at || new Date().toISOString();
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 
                  hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="text-2xl">💡</div>
        <div className="flex-1">
          <p className="text-gray-800 mb-2">{fact.content || fact.text || fact.fact}</p>
          
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>{formatRelativeTime(timestamp)}</span>
            {fact.source && (
              <span className="bg-gray-100 px-2 py-1 rounded">
                {fact.source}
              </span>
            )}
          </div>

          {fact.confidence && (
            <div className="mt-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div 
                    className="bg-blue-600 h-1.5 rounded-full"
                    style={{ width: `${fact.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500">
                  {Math.round(fact.confidence * 100)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SemanticView;
