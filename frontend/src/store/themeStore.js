import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Theme Store - Manages app theme and preferences
 * 
 * Persists to localStorage for consistent theme across sessions.
 */
export const useThemeStore = create(
  persist(
    (set, get) => ({
      // Theme state - default to light
      theme: 'light',
      
      // Preferences
      preferences: {
        autoSave: true,
        showTimestamps: true,
        compactMode: false,
        sessionTimeout: 3600000, // 1 hour in ms
      },

      // Actions
      setTheme: (theme) => {
        console.log('Setting theme to:', theme); // Debug log
        
        // Update state first
        set({ theme });
        
        // Then update DOM
        requestAnimationFrame(() => {
          if (theme === 'dark') {
            console.log('Adding dark class'); // Debug log
            document.documentElement.classList.add('dark');
          } else {
            console.log('Removing dark class'); // Debug log
            document.documentElement.classList.remove('dark');
          }
        });
      },

      toggleTheme: () => {
        set((state) => {
          const newTheme = state.theme === 'light' ? 'dark' : 'light';
          // Update document class
          if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { theme: newTheme };
        });
      },

      updatePreferences: (newPreferences) => {
        set((state) => ({
          preferences: { ...state.preferences, ...newPreferences },
        }));
      },

      resetPreferences: () => {
        set({
          preferences: {
            autoSave: true,
            showTimestamps: true,
            compactMode: false,
            sessionTimeout: 3600000,
          },
        });
      },
    }),
    {
      name: 'agentlab-theme-storage',
      // Initialize theme on load
      onRehydrateStorage: () => {
        // This function returns a callback that will be called after rehydration
        return (state) => {
          if (state) {
            // Apply theme to document
            const theme = state.theme || 'light';
            if (theme === 'dark') {
              document.documentElement.classList.add('dark');
            } else {
              document.documentElement.classList.remove('dark');
            }
          } else {
            // No stored state, ensure light mode
            document.documentElement.classList.remove('dark');
          }
        };
      },
    }
  )
);
