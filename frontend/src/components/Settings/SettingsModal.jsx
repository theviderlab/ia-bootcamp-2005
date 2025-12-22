import { useState, useEffect } from 'react';
import { useThemeStore } from '@store/themeStore';
import { useConfig } from '@hooks/useConfig';

/**
 * SettingsModal Component
 * 
 * Modal for managing global preferences:
 * - Theme (light/dark)
 * - Display preferences (timestamps, compact mode)
 * - Session settings (timeout)
 * 
 * Note: Memory and RAG settings remain in the sidebar.
 */
export const SettingsModal = ({ isOpen, onClose }) => {
  const { theme, preferences, setTheme, updatePreferences, resetPreferences } = useThemeStore();
  const { config, deleteConfig } = useConfig();
  
  const [localPreferences, setLocalPreferences] = useState(preferences);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  if (!isOpen) return null;

  const handleSave = () => {
    updatePreferences(localPreferences);
    onClose();
  };

  const handleReset = async () => {
    resetPreferences();
    setLocalPreferences({
      autoSave: true,
      showTimestamps: true,
      compactMode: false,
      sessionTimeout: 3600000,
    });
    
    // Also reset session config if exists
    try {
      await deleteConfig();
    } catch (err) {
      console.error('Failed to reset session config:', err);
    }
    
    setShowResetConfirm(false);
  };

  const handleCancel = () => {
    setLocalPreferences(preferences);
    setShowResetConfirm(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Settings
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Manage your preferences and application settings
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-6">
          {/* Appearance Section */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Appearance
            </h3>
            
            {/* Theme Toggle */}
            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Theme
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Choose between light and dark mode
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setTheme('light')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    theme === 'light'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  ☀️ Light
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    theme === 'dark'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  🌙 Dark
                </button>
              </div>
            </div>

            {/* Show Timestamps */}
            <div className="flex items-center justify-between py-3 border-t border-gray-200 dark:border-gray-700">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Show Timestamps
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Display message timestamps in chat
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localPreferences.showTimestamps}
                  onChange={(e) =>
                    setLocalPreferences({ ...localPreferences, showTimestamps: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Compact Mode */}
            <div className="flex items-center justify-between py-3 border-t border-gray-200 dark:border-gray-700">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Compact Mode
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Reduce spacing for denser layout
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localPreferences.compactMode}
                  onChange={(e) =>
                    setLocalPreferences({ ...localPreferences, compactMode: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </section>

          {/* Session Section */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Session
            </h3>
            
            {/* Auto Save */}
            <div className="flex items-center justify-between py-3">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto-save Conversations
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Automatically save conversation to browser storage
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={localPreferences.autoSave}
                  onChange={(e) =>
                    setLocalPreferences({ ...localPreferences, autoSave: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Session Timeout */}
            <div className="py-3 border-t border-gray-200 dark:border-gray-700">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Session Timeout
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                Time before session expires (in minutes)
              </p>
              <select
                value={localPreferences.sessionTimeout}
                onChange={(e) =>
                  setLocalPreferences({ ...localPreferences, sessionTimeout: parseInt(e.target.value) })
                }
                className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm dark:text-white"
              >
                <option value={1800000}>30 minutes</option>
                <option value={3600000}>1 hour</option>
                <option value={7200000}>2 hours</option>
                <option value={14400000}>4 hours</option>
                <option value={28800000}>8 hours</option>
              </select>
            </div>
          </section>

          {/* Configuration Info */}
          {config && (
            <section className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
                ℹ️ Active Session Configuration
              </h4>
              <p className="text-xs text-blue-700 dark:text-blue-400">
                This session has custom settings. Memory and RAG configurations can be adjusted in the sidebar.
              </p>
            </section>
          )}

          {/* Reset Section */}
          <section className="border-t border-gray-200 dark:border-gray-700 pt-4">
            {!showResetConfirm ? (
              <button
                onClick={() => setShowResetConfirm(true)}
                className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
              >
                🔄 Reset to Default Settings
              </button>
            ) : (
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <p className="text-sm text-red-800 dark:text-red-300 mb-3">
                  Are you sure? This will reset all preferences to defaults and clear session configuration.
                </p>
                <div className="flex space-x-2">
                  <button
                    onClick={handleReset}
                    className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 transition-colors"
                  >
                    Yes, Reset
                  </button>
                  <button
                    onClick={() => setShowResetConfirm(false)}
                    className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-end space-x-3">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};
