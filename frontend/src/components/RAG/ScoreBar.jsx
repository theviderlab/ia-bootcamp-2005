/**
 * ScoreBar Component
 * Visual indicator for RAG chunk relevance score (0.0-1.0)
 */
export const ScoreBar = ({ score }) => {
  const percentage = Math.round(score * 100);
  
  // Color based on score
  const getColor = () => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const getTextColor = () => {
    if (score >= 0.8) return 'text-green-700';
    if (score >= 0.6) return 'text-yellow-700';
    return 'text-orange-700';
  };

  return (
    <div className="flex items-center space-x-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${getColor()}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <span className={`text-xs font-medium ${getTextColor()}`}>
        {percentage}%
      </span>
    </div>
  );
};
