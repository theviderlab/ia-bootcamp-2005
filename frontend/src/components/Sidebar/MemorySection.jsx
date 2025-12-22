import { useMemory } from '@hooks/useMemory';
import { 
  MEMORY_TYPES, 
  MEMORY_TYPE_LABELS, 
  MEMORY_TYPE_DESCRIPTIONS,
  LONG_TERM_MEMORY_TYPES 
} from '@constants/memoryTypes';

/**
 * MemorySection Component
 * Sidebar section for managing memory types with toggle switches
 * Syncs configuration with backend automatically
 * 
 * Memory is automatically enabled when any memory type is active
 */
export const MemorySection = () => {
  const {
    memoryEnabled,
    enabledTypes,
    shortTermEnabled,
    toggleMemoryType,
    loading,
  } = useMemory();

  const handleTypeToggle = async (type) => {
    await toggleMemoryType(type);
  };

  const isTypeEnabled = (type) => {
    if (type === 'short_term') return shortTermEnabled;
    return enabledTypes.includes(type);
  };

  const isTypeDisabled = (type) => {
    // Temporarily disable episodic and procedural memory types
    if (type === MEMORY_TYPES.EPISODIC || type === MEMORY_TYPES.PROCEDURAL) {
      return true;
    }
    return loading;
  };

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Memory</h3>
        {loading && (
          <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        )}
      </div>

      {/* Memory Type Toggles */}
      <div className="space-y-2">
        {/* Short-term Memory (first) */}
        <MemoryTypeToggle
          key={MEMORY_TYPES.SHORT_TERM}
          type={MEMORY_TYPES.SHORT_TERM}
          label={MEMORY_TYPE_LABELS[MEMORY_TYPES.SHORT_TERM]}
          description={MEMORY_TYPE_DESCRIPTIONS[MEMORY_TYPES.SHORT_TERM]}
          enabled={shortTermEnabled}
          disabled={loading}
          onToggle={() => handleTypeToggle(MEMORY_TYPES.SHORT_TERM)}
        />
        
        {/* Long-term Memory Types */}
        {LONG_TERM_MEMORY_TYPES.map((type) => (
          <MemoryTypeToggle
            key={type}
            type={type}
            label={MEMORY_TYPE_LABELS[type]}
            description={MEMORY_TYPE_DESCRIPTIONS[type]}
            enabled={isTypeEnabled(type)}
            disabled={isTypeDisabled(type)}
            onToggle={() => handleTypeToggle(type)}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * MemoryTypeToggle Component
 * Individual toggle for a specific memory type with tooltip
 */
const MemoryTypeToggle = ({ type, label, description, enabled, disabled, onToggle }) => {
  return (
    <div className="flex items-center justify-between p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <label
            htmlFor={`toggle-${type}`}
            className={`
              text-sm font-medium cursor-pointer
              ${disabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'}
            `}
          >
            {label}
          </label>
          {/* Tooltip Icon */}
          <div className="relative group/tooltip">
            <span className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-400 cursor-help text-xs">ⓘ</span>
            <div className="absolute left-0 bottom-full mb-2 hidden group-hover/tooltip:block z-10 w-64">
              <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded p-2 shadow-lg">
                {description}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <button
        id={`toggle-${type}`}
        role="switch"
        aria-checked={enabled}
        onClick={onToggle}
        disabled={disabled}
        className={`
          relative inline-flex h-5 w-9 items-center rounded-full transition-colors
          ${enabled ? 'bg-blue-600' : 'bg-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <span
          className={`
            inline-block h-3 w-3 transform rounded-full bg-white transition-transform
            ${enabled ? 'translate-x-5' : 'translate-x-1'}
          `}
        />
      </button>
    </div>
  );
};

export default MemorySection;
