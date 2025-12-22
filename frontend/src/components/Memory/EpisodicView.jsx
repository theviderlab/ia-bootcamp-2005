import { formatRelativeTime } from '@utils/formatters';
import { useState } from 'react';

/**
 * EpisodicView Component
 * Displays episodic memory as timeline of conversation episode summaries
 */
export const EpisodicView = ({ episodes }) => {
  const [expandedEpisodes, setExpandedEpisodes] = useState(new Set());

  const toggleExpand = (episodeId) => {
    setExpandedEpisodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(episodeId)) {
        newSet.delete(episodeId);
      } else {
        newSet.add(episodeId);
      }
      return newSet;
    });
  };

  if (episodes.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Episodes Yet</h3>
        <p className="text-gray-600">
          Conversation summaries will be stored here over time.
        </p>
      </div>
    );
  }

  // Group episodes by date
  const groupedEpisodes = groupByDate(episodes);

  return (
    <div className="space-y-6">
      {Object.entries(groupedEpisodes).map(([date, dateEpisodes]) => (
        <div key={date}>
          <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3 sticky top-0 bg-gray-50 py-2">
            {date}
          </h3>
          <div className="space-y-3">
            {dateEpisodes.map((episode, index) => (
              <EpisodeCard
                key={episode.id || index}
                episode={episode}
                expanded={expandedEpisodes.has(episode.id || index)}
                onToggleExpand={() => toggleExpand(episode.id || index)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * EpisodeCard Component
 * Individual episode card with expandable content
 */
const EpisodeCard = ({ episode, expanded, onToggleExpand }) => {
  const timestamp = episode.timestamp || episode.created_at || new Date().toISOString();
  const summary = episode.summary || episode.content || '';
  const preview = summary.length > 200 ? summary.slice(0, 200) + '...' : summary;

  return (
    <div className="relative pl-8 pb-4">
      {/* Timeline dot */}
      <div className="absolute left-0 top-2 w-3 h-3 bg-blue-600 rounded-full border-2 border-white shadow"></div>
      <div className="absolute left-[5px] top-5 w-0.5 h-full bg-gray-200"></div>

      {/* Card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 
                    hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xl">💬</span>
            <div>
              <div className="font-medium text-gray-900">
                {episode.title || 'Conversation Episode'}
              </div>
              <div className="text-xs text-gray-500">
                {formatRelativeTime(timestamp)}
              </div>
            </div>
          </div>

          {summary.length > 200 && (
            <button
              onClick={onToggleExpand}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {expanded ? 'Less' : 'More'}
            </button>
          )}
        </div>

        <p className="text-gray-700 whitespace-pre-wrap">
          {expanded ? summary : preview}
        </p>

        {/* Metadata */}
        {(episode.participants || episode.message_count) && (
          <div className="mt-3 pt-3 border-t border-gray-100 flex gap-4 text-xs text-gray-500">
            {episode.participants && (
              <span>👥 {episode.participants}</span>
            )}
            {episode.message_count && (
              <span>💬 {episode.message_count} messages</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Group episodes by date
 */
const groupByDate = (episodes) => {
  const grouped = {};
  
  episodes.forEach(episode => {
    const timestamp = episode.timestamp || episode.created_at || new Date().toISOString();
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    let dateKey;
    if (date.toDateString() === today.toDateString()) {
      dateKey = 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      dateKey = 'Yesterday';
    } else {
      dateKey = date.toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric', 
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined 
      });
    }

    if (!grouped[dateKey]) {
      grouped[dateKey] = [];
    }
    grouped[dateKey].push(episode);
  });

  return grouped;
};

export default EpisodicView;
