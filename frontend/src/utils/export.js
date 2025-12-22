/**
 * Export Utilities
 * 
 * Functions for exporting conversation data in different formats.
 */

/**
 * Format date for export headers
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
const formatExportDate = (date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Export conversation as JSON
 * @param {Array} messages - Array of message objects
 * @param {string} sessionId - Session ID
 * @returns {string} JSON string
 */
export const exportAsJSON = (messages, sessionId) => {
  const exportData = {
    metadata: {
      exportDate: new Date().toISOString(),
      sessionId: sessionId || 'unknown',
      messageCount: messages.length,
      version: '1.0',
    },
    messages: messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp,
      id: msg.id,
    })),
  };

  return JSON.stringify(exportData, null, 2);
};

/**
 * Export conversation as Markdown
 * @param {Array} messages - Array of message objects
 * @param {string} sessionId - Session ID
 * @returns {string} Markdown string
 */
export const exportAsMarkdown = (messages, sessionId) => {
  const exportDate = formatExportDate(new Date());
  
  let markdown = `# Agent Lab Conversation\n\n`;
  markdown += `**Exported:** ${exportDate}\n`;
  markdown += `**Session ID:** ${sessionId || 'Unknown'}\n`;
  markdown += `**Messages:** ${messages.length}\n\n`;
  markdown += `---\n\n`;

  messages.forEach((msg, index) => {
    const timestamp = msg.timestamp 
      ? formatExportDate(new Date(msg.timestamp)) 
      : 'Unknown time';
    
    markdown += `## Message ${index + 1}\n\n`;
    markdown += `**Role:** ${msg.role === 'user' ? 'User' : 'Assistant'}\n`;
    markdown += `**Time:** ${timestamp}\n\n`;
    markdown += `${msg.content}\n\n`;
    markdown += `---\n\n`;
  });

  return markdown;
};

/**
 * Download file with given content
 * @param {string} content - File content
 * @param {string} filename - File name
 * @param {string} mimeType - MIME type
 */
export const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Generate filename for export
 * @param {string} format - 'json' or 'md'
 * @param {string} sessionId - Session ID
 * @returns {string} Filename
 */
export const generateExportFilename = (format, sessionId) => {
  const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const session = sessionId ? sessionId.substring(0, 8) : 'unknown';
  return `agentlab-${session}-${timestamp}.${format}`;
};
