import { MemorySection } from '@components/Sidebar/MemorySection';
import { RAGSection } from '@components/Sidebar/RAGSection';
import { MPCSection } from '@components/Sidebar/MPCSection';

/**
 * Sidebar Component
 * 
 * Right panel for configuration (Memory, RAG, MCP sections).
 * Phase 2: Memory section implemented.
 * Phase 3: RAG section implemented.
 * Phase 6: MCP section implemented.
 */
export const Sidebar = () => {
  return (
    <aside className="h-full bg-gray-50 dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
      <div className="space-y-6">
        {/* Memory Section - Phase 2 */}
        <MemorySection />

        {/* RAG Section - Phase 3 */}
        <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
          <RAGSection />
        </div>

        {/* MCP Section - Phase 6 */}
        <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
          <MPCSection />
        </div>
      </div>
    </aside>
  );
};
