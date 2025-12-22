import { useState } from 'react';
import clsx from 'clsx';
import { useMemory } from '@hooks/useMemory';
import { useChatStore } from '@store/chatStore';
import { useSession } from '@hooks/useSession';
import { SettingsModal } from '@components/Settings/SettingsModal';
import { ResetDialog } from '@components/Settings/ResetDialog';
import { DeleteAllDialog } from '@components/Settings/DeleteAllDialog';

/**
 * Header Component
 * 
 * Top bar with tab navigation and action buttons.
 * Phase 1: Shows Chat and Context Window tabs.
 * Phase 2: Adds Short-term and Long-term Memory tabs conditionally.
 * Phase 3: Adds RAG Results tab conditionally.
 * Phase 6: Adds Reset Session and Delete All buttons.
 * Phase 7: Adds Settings button.
 */
export const Header = ({ activeTab, onTabChange }) => {
  const { memoryEnabled, enabledTypes } = useMemory();
  const { ragSources } = useChatStore();
  const { resetSession, deleteAll, resetting, deleting, savingMemory } = useSession();
  
  const [showSettings, setShowSettings] = useState(false);
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deletionCounts, setDeletionCounts] = useState(null);

  // Build tabs array dynamically based on enabled features
  const tabs = [
    { id: 'chat', label: 'Chat', alwaysVisible: true },
    // Short-term Memory tab appears when memory is enabled
    { 
      id: 'short-term', 
      label: 'Short-term Memory', 
      alwaysVisible: false,
      condition: memoryEnabled,
    },
    // Long-term Memory tab appears when any long-term memory type is enabled
    { 
      id: 'long-term', 
      label: 'Long-term Memory', 
      alwaysVisible: false,
      condition: memoryEnabled && enabledTypes.length > 0,
    },
    // RAG Results tab appears when RAG sources exist
    { 
      id: 'rag-results', 
      label: 'RAG Results', 
      alwaysVisible: false,
      condition: ragSources && ragSources.length > 0,
    },
    { id: 'context', label: 'Context Window', alwaysVisible: true },
  ];

  // Filter tabs based on visibility conditions
  const visibleTabs = tabs.filter(tab => tab.alwaysVisible || tab.condition);

  /**
   * Handle session reset
   */
  const handleResetSession = async () => {
    try {
      await resetSession();
      setShowResetDialog(false);
      // Switch to chat tab after reset
      onTabChange('chat');
    } catch (err) {
      console.error('Failed to reset session:', err);
      alert(`Failed to reset session: ${err.message}`);
    }
  };

  /**
   * Handle delete all
   */
  const handleDeleteAll = async (confirmation) => {
    try {
      const counts = await deleteAll(confirmation);
      setDeletionCounts(counts);
      // Dialog will show success screen, then reload
    } catch (err) {
      console.error('Failed to delete all:', err);
      alert(`Failed to delete all data: ${err.message}`);
    }
  };

  return (
    <>
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Tab Navigation */}
          <nav className="flex space-x-1 overflow-x-auto">
            {visibleTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={clsx(
                  'px-4 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap',
                  activeTab === tab.id
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {/* Reset Session Button */}
            <button
              onClick={() => setShowResetDialog(true)}
              disabled={resetting}
              className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Reset Session (Clear chat history)"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            {/* Delete All Button */}
            <button
              onClick={() => setShowDeleteDialog(true)}
              disabled={deleting}
              className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Delete All Data (Nuclear option)"
            >
              <span className="text-xl">💀</span>
            </button>

            {/* Settings Button */}
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
              title="Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Settings Modal */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />

      {/* Reset Session Dialog */}
      <ResetDialog
        isOpen={showResetDialog}
        onClose={() => setShowResetDialog(false)}
        onConfirm={handleResetSession}
        loading={resetting}
      />

      {/* Delete All Dialog */}
      <DeleteAllDialog
        isOpen={showDeleteDialog}
        onClose={() => {
          setShowDeleteDialog(false);
          setDeletionCounts(null);
        }}
        onConfirm={handleDeleteAll}
        loading={deleting}
        deletionCounts={deletionCounts}
      />

      {/* Saving Memory Toast */}
      {savingMemory && (
        <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-fade-in flex items-center gap-2">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Saving memories...</span>
        </div>
      )}
    </>
  );
};
