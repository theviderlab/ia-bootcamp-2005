import { useState, useCallback } from 'react';

/**
 * FileUploader Component
 * Provides drag-and-drop and file picker functionality for uploading documents
 */
export const FileUploader = ({ onFilesSelected, accept = '.txt,.md,.log', disabled = false }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        onFilesSelected(files);
      }
    },
    [disabled, onFilesSelected]
  );

  const handleFileInputChange = useCallback(
    (e) => {
      const files = e.target.files;
      if (files.length > 0) {
        onFilesSelected(files);
      }
      // Reset input so the same file can be uploaded again
      e.target.value = '';
    },
    [onFilesSelected]
  );

  const handleClick = useCallback(() => {
    if (!disabled) {
      document.getElementById('file-upload-input').click();
    }
  }, [disabled]);

  return (
    <div
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-colors duration-200
        ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        id="file-upload-input"
        type="file"
        multiple
        accept={accept}
        onChange={handleFileInputChange}
        className="hidden"
        disabled={disabled}
      />

      <div className="space-y-2">
        <div className="text-4xl">📁</div>
        <p className="text-sm text-gray-600">
          {isDragging ? (
            <span className="text-blue-600 font-medium">Drop files here</span>
          ) : (
            <>
              <span className="text-blue-600 font-medium">Click to upload</span> or drag
              and drop
            </>
          )}
        </p>
        <p className="text-xs text-gray-500">.txt, .md, .log files (max 10MB each)</p>
      </div>
    </div>
  );
};
