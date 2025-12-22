/**
 * TokenUsageBar Component
 * 
 * Visual progress bar showing token usage with color-coded indicators:
 * - Green: < 70% usage
 * - Yellow: 70-90% usage
 * - Red: > 90% usage
 * 
 * Displays token breakdown by component (short-term, RAG, memory types, tools).
 */

import { useState } from 'react';

const TokenUsageBar = ({ currentTokens, maxTokens = 4000, breakdown = {} }) => {
  const [showBreakdown, setShowBreakdown] = useState(false);

  // Calculate percentage
  const percentage = maxTokens > 0 ? (currentTokens / maxTokens) * 100 : 0;

  // Determine color based on usage
  const getColor = () => {
    if (percentage < 70) return 'bg-green-500';
    if (percentage < 90) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getTextColor = () => {
    if (percentage < 70) return 'text-green-700';
    if (percentage < 90) return 'text-yellow-700';
    return 'text-red-700';
  };

  // Format breakdown data
  const breakdownEntries = Object.entries(breakdown)
    .filter(([_, tokens]) => tokens > 0)
    .sort(([_, a], [__, b]) => b - a); // Sort by token count descending

  const getLabelForComponent = (key) => {
    const labels = {
      short_term: 'Short-term History',
      semantic: 'Semantic Memory',
      episodic: 'Episodic Memory',
      profile: 'Profile Memory',
      procedural: 'Procedural Memory',
      rag: 'RAG Documents',
      tools: 'Tool Results',
    };
    return labels[key] || key;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-700">Token Usage</h3>
          <button
            onClick={() => setShowBreakdown(!showBreakdown)}
            className="text-xs text-primary-500 hover:text-primary-600 transition-colors"
            title="Toggle breakdown"
          >
            {showBreakdown ? '▼' : '▶'} Details
          </button>
        </div>
        <div className={`text-sm font-mono ${getTextColor()}`}>
          {currentTokens.toLocaleString()} / {maxTokens.toLocaleString()}
          <span className="text-gray-500 ml-1">({percentage.toFixed(1)}%)</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${getColor()} transition-all duration-300 ease-in-out`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      {/* Breakdown Details */}
      {showBreakdown && breakdownEntries.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
            Token Breakdown
          </div>
          {breakdownEntries.map(([key, tokens]) => {
            const componentPercentage = maxTokens > 0 ? (tokens / maxTokens) * 100 : 0;
            return (
              <div key={key} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-700">{getLabelForComponent(key)}</span>
                  <span className="font-mono text-gray-600">
                    {tokens.toLocaleString()} ({componentPercentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-full bg-primary-400 transition-all duration-300"
                    style={{ width: `${Math.min(componentPercentage, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Warning if over limit */}
      {percentage > 100 && (
        <div className="mt-3 text-xs text-red-600 bg-red-50 p-2 rounded">
          ⚠️ Context exceeds maximum tokens. Content may be truncated by LLM.
        </div>
      )}

      {/* Status indicator */}
      {percentage > 0 && (
        <div className="mt-3 text-xs text-gray-500">
          {percentage < 70 && '✓ Healthy token usage'}
          {percentage >= 70 && percentage < 90 && '⚠️ Approaching token limit'}
          {percentage >= 90 && percentage <= 100 && '🔴 Near maximum capacity'}
          {percentage > 100 && '❌ Exceeds maximum capacity'}
        </div>
      )}
    </div>
  );
};

export default TokenUsageBar;
