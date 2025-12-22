import { useState } from 'react';
import clsx from 'clsx';
import { useChatStore } from '@store/chatStore';
import TokenUsageBar from './ContextWindow/TokenUsageBar';
import ContextSection from './ContextWindow/ContextSection';
import { parseContextSections, downloadJSON, copyToClipboard } from '@utils/formatters';

/**
 * ContextWindowTab Component
 * 
 * Displays the complete context sent to the LLM with:
 * - Token usage visualization with breakdown
 * - Collapsible sections parsed from markdown (##)
 * - Copy and download actions
 * - Syntax highlighting for code blocks (CSS-based)
 */
export const ContextWindowTab = () => {
  const { contextData } = useChatStore();
  const [copiedToast, setCopiedToast] = useState(false);
  const [downloadToast, setDownloadToast] = useState(false);
  const [viewMode, setViewMode] = useState('sections'); // 'sections' or 'raw'

  if (!contextData) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <div className="text-center">
          <p className="text-lg font-medium">No context data yet</p>
          <p className="text-sm mt-2">Send a message to see the LLM context</p>
        </div>
      </div>
    );
  }

  // Parse context into sections
  const sections = parseContextSections(contextData.context_text || '');

  // Handle copy to clipboard
  const handleCopy = async () => {
    const success = await copyToClipboard(contextData.context_text || '');
    if (success) {
      setCopiedToast(true);
      setTimeout(() => setCopiedToast(false), 2000);
    }
  };

  // Handle download as JSON
  const handleDownload = () => {
    downloadJSON(contextData, `context-${Date.now()}`);
    setDownloadToast(true);
    setTimeout(() => setDownloadToast(false), 2000);
  };

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-50">
      <style>{`
        .code-block {
          background-color: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 4px;
          padding: 12px;
          overflow-x: auto;
          font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
          font-size: 13px;
          line-height: 1.5;
          color: #212529;
        }
        .code-block code {
          font-family: inherit;
          background: none;
          padding: 0;
        }
      `}</style>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-gray-800">Context Window</h2>
            
            {/* View Mode Toggle */}
            <div className="flex bg-gray-200 rounded-lg p-1">
              <button
                onClick={() => setViewMode('sections')}
                className={clsx(
                  'px-3 py-1 text-sm rounded transition-colors',
                  viewMode === 'sections'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                Sections
              </button>
              <button
                onClick={() => setViewMode('raw')}
                className={clsx(
                  'px-3 py-1 text-sm rounded transition-colors',
                  viewMode === 'raw'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                Raw Text
              </button>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title="Copy full context to clipboard"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title="Download context as JSON"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download JSON
            </button>
          </div>
        </div>

        {/* Toast Notifications */}
        {copiedToast && (
          <div className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-fade-in">
            ✓ Copied to clipboard
          </div>
        )}
        {downloadToast && (
          <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-fade-in">
            ✓ Downloaded context.json
          </div>
        )}

        {/* Token Usage Bar */}
        <TokenUsageBar
          currentTokens={contextData.context_tokens || 0}
          maxTokens={contextData.max_context_tokens || 4000}
          breakdown={contextData.token_breakdown || {}}
        />

        {/* Context Sections */}
        {viewMode === 'sections' ? (
          sections.length > 0 ? (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Context Sections
              </h3>
              {sections.map((section, index) => {
                // Get token count for this section from breakdown if available
                const sectionKey = section.title.toLowerCase().replace(/\s+/g, '_');
                const tokenCount = contextData.token_breakdown?.[sectionKey] || 0;

                return (
                  <ContextSection
                    key={index}
                    title={section.title}
                    content={section.content}
                    tokenCount={tokenCount}
                    defaultExpanded={index === 0} // First section expanded by default
                  />
                );
              })}
            </div>
          ) : (
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Full Context
              </h3>
              <pre className="code-block">
                {contextData.context_text}
              </pre>
            </div>
          )
        ) : (
          // Raw text view
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Raw Context Sent to LLM
              </h3>
              <span className="text-xs text-gray-500">
                This is the exact text sent to the language model
              </span>
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <pre className="code-block whitespace-pre-wrap">
                {contextData.context_text}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
