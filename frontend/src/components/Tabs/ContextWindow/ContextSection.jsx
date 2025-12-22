/**
 * ContextSection Component
 * 
 * Collapsible section displaying a part of the context window.
 * Shows title, token count, and content with syntax highlighting for code blocks.
 */

import { useState } from 'react';

const ContextSection = ({ title, content, tokenCount = 0, defaultExpanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!content || content.trim().length === 0) {
    return null; // Don't render empty sections
  }

  // Simple code block detection (lines starting with 4+ spaces or wrapped in ```)
  const renderContent = () => {
    const lines = content.split('\n');
    const elements = [];
    let inCodeBlock = false;
    let codeBuffer = [];

    lines.forEach((line, index) => {
      // Check for ``` code fence
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          // End code block
          elements.push(
            <pre key={`code-${index}`} className="code-block">
              <code>{codeBuffer.join('\n')}</code>
            </pre>
          );
          codeBuffer = [];
        }
        inCodeBlock = !inCodeBlock;
        return;
      }

      if (inCodeBlock) {
        codeBuffer.push(line);
      } else {
        // Check for indented code (4+ spaces)
        if (line.startsWith('    ') && line.trim().length > 0) {
          elements.push(
            <pre key={`line-${index}`} className="code-block">
              <code>{line}</code>
            </pre>
          );
        } else {
          // Regular text
          if (line.trim().length > 0) {
            elements.push(
              <p key={`text-${index}`} className="text-gray-700 leading-relaxed">
                {line}
              </p>
            );
          } else {
            elements.push(<br key={`br-${index}`} />);
          }
        }
      }
    });

    // Close any remaining code block
    if (inCodeBlock && codeBuffer.length > 0) {
      elements.push(
        <pre key="code-final" className="code-block">
          <code>{codeBuffer.join('\n')}</code>
        </pre>
      );
    }

    return elements;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-gray-400 text-sm">
            {isExpanded ? '▼' : '▶'}
          </span>
          <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
        </div>
        {tokenCount > 0 && (
          <span className="text-xs font-mono bg-primary-100 text-primary-700 px-2 py-1 rounded">
            {tokenCount.toLocaleString()} tokens
          </span>
        )}
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="p-4 pt-0 border-t border-gray-100">
          <div className="space-y-2 text-sm">
            {renderContent()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContextSection;
