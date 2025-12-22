import { useState, lazy, Suspense, useEffect } from 'react';
import { Layout } from '@components/Layout/Layout';
import { useThemeStore } from '@store/themeStore';
import { useSession } from '@hooks/useSession';

// Lazy load tab components for better performance
const ChatTab = lazy(() => import('@components/Tabs/ChatTab').then(m => ({ default: m.ChatTab })));
const ContextWindowTab = lazy(() => import('@components/Tabs/ContextWindowTab').then(m => ({ default: m.ContextWindowTab })));
const ShortTermMemoryTab = lazy(() => import('@components/Tabs/ShortTermMemoryTab').then(m => ({ default: m.ShortTermMemoryTab })));
const LongTermMemoryTab = lazy(() => import('@components/Tabs/LongTermMemoryTab').then(m => ({ default: m.LongTermMemoryTab })));
const RAGResultsTab = lazy(() => import('@components/Tabs/RAGResultsTab').then(m => ({ default: m.RAGResultsTab })));

/**
 * App Component
 * 
 * Main application entry point with tab management and session initialization.
 * Phase 1: Chat and Context Window tabs.
 * Phase 2: Added Short-term and Long-term Memory tabs.
 * Phase 3: Added RAG Results tab.
 * Phase 6: Added session initialization on mount.
 * Phase 7: Added lazy loading for performance optimization.
 */
function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const theme = useThemeStore((state) => state.theme);
  const { initializing, error: sessionError } = useSession();

  // Ensure theme is applied on mount and when it changes
  useEffect(() => {
    console.log('App useEffect - current theme:', theme); // Debug log
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      console.log('Applied dark class'); // Debug log
    } else {
      document.documentElement.classList.remove('dark');
      console.log('Removed dark class'); // Debug log
    }
  }, [theme]);

  // Show initialization screen
  if (initializing) {
    return (
      <div className="h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center">
          <div className="mb-4">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Initializing session...</p>
        </div>
      </div>
    );
  }

  // Show error screen if session initialization failed
  if (sessionError) {
    return (
      <div className="h-screen flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="text-center max-w-md px-4">
          <div className="mb-4 text-red-500 text-5xl">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Session Initialization Failed
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{sessionError}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  // Loading fallback component
  const LoadingFallback = () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-gray-500 dark:text-gray-400">Loading...</div>
    </div>
  );

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      <Suspense fallback={<LoadingFallback />}>
        {activeTab === 'chat' && <ChatTab />}
        {activeTab === 'short-term' && <ShortTermMemoryTab />}
        {activeTab === 'long-term' && <LongTermMemoryTab />}
        {activeTab === 'rag-results' && <RAGResultsTab />}
        {activeTab === 'context' && <ContextWindowTab />}
      </Suspense>
    </Layout>
  );
}

export default App;
