/**
 * Highlight Utility
 * 
 * Function to highlight search terms in text.
 */

/**
 * Highlight matching text with HTML mark tags
 * @param {string} text - Original text
 * @param {string} query - Search query
 * @returns {Array} Array of text segments with highlight info
 */
export const highlightText = (text, query) => {
  if (!query || !query.trim()) {
    return [{ text, highlighted: false }];
  }

  const normalizedQuery = query.toLowerCase();
  const normalizedText = text.toLowerCase();
  const segments = [];
  let lastIndex = 0;

  let index = normalizedText.indexOf(normalizedQuery);
  
  while (index !== -1) {
    // Add non-highlighted text before match
    if (index > lastIndex) {
      segments.push({
        text: text.substring(lastIndex, index),
        highlighted: false,
      });
    }

    // Add highlighted match
    segments.push({
      text: text.substring(index, index + query.length),
      highlighted: true,
    });

    lastIndex = index + query.length;
    index = normalizedText.indexOf(normalizedQuery, lastIndex);
  }

  // Add remaining text
  if (lastIndex < text.length) {
    segments.push({
      text: text.substring(lastIndex),
      highlighted: false,
    });
  }

  return segments;
};
