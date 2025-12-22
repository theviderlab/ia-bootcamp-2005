/**
 * Utility functions for formatting dates and text
 */

/**
 * Format timestamp to relative time (e.g., "2 minutes ago")
 * @param {string|Date} timestamp - ISO string or Date object
 * @returns {string} Formatted relative time
 */
export const formatRelativeTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (diffInSeconds < 10) return 'just now';
  if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`;
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  
  // For older dates, show the actual date
  return date.toLocaleDateString();
};

/**
 * Truncate text to a maximum length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

/**
 * Parse context text into sections based on markdown headers (##)
 * @param {string} text - Context text with markdown sections
 * @returns {Array<{title: string, content: string}>} Parsed sections
 */
export const parseContextSections = (text) => {
  if (!text || text.trim().length === 0) return [];

  // Split by ## headers
  const sections = text.split(/^## /m).filter(Boolean);

  return sections.map(section => {
    const lines = section.split('\n');
    const title = lines[0].trim();
    const content = lines.slice(1).join('\n').trim();

    return { title, content };
  });
};

/**
 * Format token count with thousand separators
 * @param {number} count - Token count
 * @returns {string} Formatted count (e.g., "1,234")
 */
export const formatTokenCount = (count) => {
  if (typeof count !== 'number' || isNaN(count)) return '0';
  return count.toLocaleString();
};

/**
 * Download data as JSON file
 * @param {Object} data - Data to download
 * @param {string} filename - Filename without extension
 */
export const downloadJSON = (data, filename = 'context') => {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Clean up the URL object
  URL.revokeObjectURL(url);
};

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    // Fallback for older browsers
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    } catch (fallbackErr) {
      console.error('Fallback copy failed:', fallbackErr);
      return false;
    }
  }
};
