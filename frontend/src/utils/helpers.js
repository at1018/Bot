// Format date to readable format
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

// Copy text to clipboard
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy:', error);
    return false;
  }
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

// Format session ID for display
export const formatSessionId = (sessionId) => {
  return sessionId.substring(0, 8).toUpperCase();
};
