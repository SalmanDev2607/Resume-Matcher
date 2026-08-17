import React, { useState } from 'react';
import { FileText, CheckCircle, AlertCircle, Award } from 'lucide-react';
import axios from 'axios';

export default function ResumeAnalyzer({ resumeText, disabled }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleAnalyze = async () => {
    if (!resumeText) return;
    setIsAnalyzing(true);
    setErrorMsg('');
    setResult(null);

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8004';
    try {
      const response = await axios.post(`${API_BASE_URL}/api/resume/score`, {
        resume_text: resumeText
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing resume:', error);
      setErrorMsg('Failed to analyze resume. Please make sure the backend server is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <h3 style={{ fontSize: '1.2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <FileText size={20} className="dropzone-icon" style={{ margin: 0 }} />
        Resume Scorer
      </h3>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        Analyze your resume for formatting, quantifiable impact, action verbs, and common mistakes.
      </p>

      <button
        className="btn"
        onClick={handleAnalyze}
        disabled={disabled || isAnalyzing}
        style={{ width: '100%' }}
      >
        {isAnalyzing ? 'Analyzing...' : 'Analyze My Resume'}
      </button>

      {errorMsg && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: 'var(--danger)', fontSize: '0.9rem', textAlign: 'center' }}>
          {errorMsg}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '2rem', animation: 'fadeIn 0.5s ease' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', padding: '1.5rem', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
            <Award size={40} color="var(--success)" />
            <div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>Overall Score</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-color)', lineHeight: 1 }}>
                {result.score} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>
            </div>
            <div style={{ marginLeft: 'auto', textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Engine: {result.engine}
            </div>
          </div>

          <div style={{ display: 'grid', gap: '1.5rem' }}>
            <div style={{ padding: '1.5rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
              <h4 style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <CheckCircle size={18} /> Strengths
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.strengths && result.strengths.length > 0 ? (
                  result.strengths.map((s, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.95rem' }}>
                      <span style={{ color: 'var(--success)' }}>•</span> <span>{s}</span>
                    </li>
                  ))
                ) : (
                  <li style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No particular strengths detected.</li>
                )}
              </ul>
            </div>

            <div style={{ padding: '1.5rem', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
              <h4 style={{ color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <AlertCircle size={18} /> Areas for Improvement
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.mistakes && result.mistakes.length > 0 ? (
                  result.mistakes.map((m, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.95rem' }}>
                      <span style={{ color: 'var(--warning)' }}>•</span> <span>{m}</span>
                    </li>
                  ))
                ) : (
                  <li style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Your resume looks great! No major mistakes found.</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
