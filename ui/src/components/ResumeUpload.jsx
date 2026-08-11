import React, { useCallback, useState } from 'react';
import { UploadCloud, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

export default function ResumeUpload({ onResumeUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [fileName, setFileName] = useState('');

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const onFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    setFileName(file.name);
    setIsUploading(true);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append('file', file);

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8004';
    try {
      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onResumeUploaded(response.data.resume_text);
      setUploadSuccess(true);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-card">
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: 600 }}>1. Upload Resume</h2>

      {uploadSuccess ? (
        <div className="dropzone">
          <div className="upload-success">
            <CheckCircle2 size={48} />
            <h3 style={{ fontSize: '1.2rem', marginTop: '0.5rem' }}>Upload Successful!</h3>
            <p style={{ color: 'var(--text-muted)' }}>{fileName}</p>
          </div>
          <button
            className="btn"
            style={{ marginTop: '1.5rem', background: 'rgba(255,255,255,0.1)' }}
            onClick={() => { setUploadSuccess(false); onResumeUploaded(null); }}
          >
            Upload Different Resume
          </button>
        </div>
      ) : (
        <label
          className={`dropzone ${isDragging ? 'active' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          <input
            type="file"
            style={{ display: 'none' }}
            onChange={onFileChange}
            accept=".pdf,.docx,.txt,.md"
          />

          {isUploading ? (
            <div className="loader-container" style={{ padding: 0 }}>
              <UploadCloud size={48} className="spinner dropzone-icon" />
              <p>Extracting text...</p>
            </div>
          ) : (
            <>
              <UploadCloud size={64} className="dropzone-icon" />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Drag & Drop your resume here</h3>
              <p style={{ color: 'var(--text-muted)' }}>or click to browse (.pdf, .docx, .txt)</p>
            </>
          )}
        </label>
      )}
    </div>
  );
}
