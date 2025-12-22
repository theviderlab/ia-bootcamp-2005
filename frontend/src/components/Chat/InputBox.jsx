import { useState, useRef } from 'react';
import clsx from 'clsx';

/**
 * InputBox Component
 * 
 * Message input area with send functionality.
 * Features:
 * - Multi-line textarea with auto-expand
 * - Enter to send, Shift+Enter for new line
 * - Disabled while loading
 * - Send button with icon
 */
export const InputBox = ({ onSend, loading, disabled }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !loading && !disabled) {
      onSend(message);
      setMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
    // Auto-expand textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="flex items-end gap-2">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          disabled={loading || disabled}
          rows={1}
          className={clsx(
            'flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-3',
            'bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'placeholder-gray-400 dark:placeholder-gray-500',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed',
            'max-h-32 overflow-y-auto'
          )}
        />

        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || loading || disabled}
          className={clsx(
            'px-6 py-3 rounded-lg font-medium transition-colors',
            'bg-primary-500 text-white',
            'hover:bg-primary-600 active:bg-primary-700',
            'disabled:bg-gray-300 disabled:cursor-not-allowed',
            'flex items-center gap-2'
          )}
        >
          {loading ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Sending...</span>
            </>
          ) : (
            <>
              <span>📤</span>
              <span>Send</span>
            </>
          )}
        </button>
      </div>

      {/* Helper Text */}
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Press Enter to send, Shift+Enter for a new line
      </p>
    </form>
  );
};
