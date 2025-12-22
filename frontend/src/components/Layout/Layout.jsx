import { Header } from './Header';
import { Sidebar } from './Sidebar';

/**
 * Layout Component
 * 
 * Main application layout with responsive design:
 * - Desktop (≥1024px): Split-screen (60% chat, 40% sidebar)
 * - Tablet (768-1023px): Stacked layout
 * - Mobile (≤767px): Full-width single column
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Tab content (ChatTab, ContextTab, etc.)
 * @param {string} props.activeTab - Current active tab ID
 * @param {Function} props.onTabChange - Tab change handler
 */
export const Layout = ({ children, activeTab, onTabChange }) => {
  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <Header activeTab={activeTab} onTabChange={onTabChange} />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Main Content (Chat, Context Window, etc.) */}
        <main className="flex-1 lg:w-[60%] bg-white dark:bg-gray-800 overflow-hidden">
          {children}
        </main>

        {/* Right Panel - Sidebar (Configuration) */}
        <div className="hidden lg:block lg:w-[40%]">
          <Sidebar />
        </div>
      </div>
    </div>
  );
};
