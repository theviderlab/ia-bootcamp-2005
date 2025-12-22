/**
 * ProfileView Component
 * Displays profile memory as key-value table of user preferences and characteristics
 */
export const ProfileView = ({ profileData }) => {
  // Convert profileData object to array of entries
  const entries = Object.entries(profileData || {});

  if (entries.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">👤</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Profile Data Yet</h3>
        <p className="text-gray-600">
          User preferences and characteristics will be learned and stored here.
        </p>
      </div>
    );
  }

  // Group entries by category if available
  const categorizedEntries = categorizeEntries(entries);

  return (
    <div className="space-y-6">
      {Object.entries(categorizedEntries).map(([category, items]) => (
        <div key={category} className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              {getCategoryIcon(category)}
              {category}
            </h3>
          </div>
          <div className="divide-y divide-gray-100">
            {items.map(([key, value]) => (
              <ProfileEntry key={key} entryKey={key} value={value} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * ProfileEntry Component
 * Individual key-value pair in profile
 */
const ProfileEntry = ({ entryKey, value }) => {
  const displayKey = formatKey(entryKey);
  const displayValue = formatValue(value);

  return (
    <div className="px-4 py-3 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <dt className="text-sm font-medium text-gray-600 min-w-[150px]">
          {displayKey}
        </dt>
        <dd className="text-sm text-gray-900 flex-1 text-right">
          {displayValue}
        </dd>
      </div>
    </div>
  );
};

/**
 * Categorize entries by prefix or default to "General"
 */
const categorizeEntries = (entries) => {
  const categorized = {
    'Personal Information': [],
    'Preferences': [],
    'Skills & Expertise': [],
    'Goals & Interests': [],
    'General': [],
  };

  entries.forEach(([key, value]) => {
    const lowerKey = key.toLowerCase();
    
    if (lowerKey.includes('name') || lowerKey.includes('age') || lowerKey.includes('location')) {
      categorized['Personal Information'].push([key, value]);
    } else if (lowerKey.includes('prefer') || lowerKey.includes('like') || lowerKey.includes('favorite')) {
      categorized['Preferences'].push([key, value]);
    } else if (lowerKey.includes('skill') || lowerKey.includes('expert') || lowerKey.includes('experience')) {
      categorized['Skills & Expertise'].push([key, value]);
    } else if (lowerKey.includes('goal') || lowerKey.includes('interest') || lowerKey.includes('hobby')) {
      categorized['Goals & Interests'].push([key, value]);
    } else {
      categorized['General'].push([key, value]);
    }
  });

  // Remove empty categories
  Object.keys(categorized).forEach(category => {
    if (categorized[category].length === 0) {
      delete categorized[category];
    }
  });

  return categorized;
};

/**
 * Format key from camelCase or snake_case to readable text
 */
const formatKey = (key) => {
  return key
    .replace(/([A-Z])/g, ' $1') // camelCase
    .replace(/_/g, ' ') // snake_case
    .replace(/\b\w/g, char => char.toUpperCase()) // Capitalize
    .trim();
};

/**
 * Format value for display
 */
const formatValue = (value) => {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  
  return String(value);
};

/**
 * Get icon for category
 */
const getCategoryIcon = (category) => {
  const icons = {
    'Personal Information': '📋',
    'Preferences': '⭐',
    'Skills & Expertise': '🎯',
    'Goals & Interests': '🎨',
    'General': '📌',
  };
  return icons[category] || '📌';
};

export default ProfileView;
