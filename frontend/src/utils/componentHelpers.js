/**
 * Component Helper Utilities
 * Reusable utilities for React components
 */

/**
 * Format timestamp to readable date/time
 */
export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  try {
    return new Date(timestamp).toLocaleString();
  } catch {
    return timestamp;
  }
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Format bytes to human-readable size
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Debounce function for performance optimization
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Async error handler wrapper
 */
export const asyncHandler = async (asyncFn, errorCallback) => {
  try {
    return await asyncFn();
  } catch (error) {
    if (errorCallback) {
      errorCallback(error);
    }
    console.error('Async error:', error);
    return null;
  }
};

/**
 * API call wrapper with loading state
 */
export const apiCall = async (url, options = {}, callbacks = {}) => {
  const { onStart, onSuccess, onError, onFinally } = callbacks;
  
  try {
    if (onStart) onStart();
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Request failed');
    }
    
    if (onSuccess) onSuccess(data);
    return { success: true, data };
    
  } catch (error) {
    if (onError) onError(error);
    return { success: false, error: error.message };
    
  } finally {
    if (onFinally) onFinally();
  }
};

/**
 * Class name helper for conditional classes
 */
export const classNames = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

/**
 * Check if value is empty (null, undefined, empty string, empty array)
 */
export const isEmpty = (value) => {
  return (
    value === null ||
    value === undefined ||
    value === '' ||
    (Array.isArray(value) && value.length === 0) ||
    (typeof value === 'object' && Object.keys(value).length === 0)
  );
};
