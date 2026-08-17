import React, { useState } from 'react';
import { ExternalLink, Check, X, Award } from 'lucide-react';

export default function MatchResults({ results }) {
  const [activeFilter, setActiveFilter] = useState('All');

  if (!results || results.length === 0) return null;

  const uniqueSources = Array.from(new Set(results.map(r => r.source).filter(Boolean)));
  const filteredResults = activeFilter === 'All' 
    ? results 
    : results.filter(r => r.source === activeFilter);

  return (
    <div className="results-section">
      <h2 style={{ marginBottom: '2rem', fontSize: '1.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Award size={28} color="var(--accent-primary)" />
        Top Matched Jobs
      </h2>
      
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <button 
          onClick={() => setActiveFilter('All')}
          style={{ padding: '0.4rem 1rem', borderRadius: '20px', border: '1px solid var(--glass-border)', background: activeFilter === 'All' ? 'var(--accent-primary)' : 'rgba(30, 41, 59, 0.4)', color: activeFilter === 'All' ? 'white' : 'var(--text-color)', cursor: 'pointer', transition: 'all 0.2s' }}
        >
          All
        </button>
        {uniqueSources.map(source => (
          <button 
            key={source}
            onClick={() => setActiveFilter(source)}
            style={{ padding: '0.4rem 1rem', borderRadius: '20px', border: '1px solid var(--glass-border)', background: activeFilter === source ? 'var(--accent-primary)' : 'rgba(30, 41, 59, 0.4)', color: activeFilter === source ? 'white' : 'var(--text-color)', cursor: 'pointer', transition: 'all 0.2s' }}
          >
            {source}
          </button>
        ))}
      </div>
      
      <div className="results-grid">
        {filteredResults.map((job, idx) => (
          <div key={idx} className="glass-card match-card">
            <div className="match-header">
              <div className="job-info">
                <h3 className="job-title">{job.title}</h3>
                <div className="job-company">{job.company}</div>
                <div className="job-location">{job.location}</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                <div className="score-badge">
                  {Math.round(job.match_score * 100)}% Match
                </div>
                {job.source && (
                  <div style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', color: 'var(--text-secondary)', fontWeight: '500' }}>
                    Source: {job.source}
                  </div>
                )}
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Skill Overlap</p>
                <div style={{ fontWeight: 600 }}>{job.skill_overlap_pct}%</div>
              </div>
              <div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>Semantic Similarity</p>
                <div style={{ fontWeight: 600 }}>{job.semantic_similarity_pct}%</div>
              </div>
            </div>

            {job.matched_skills.length > 0 && (
              <div className="skills-container">
                <div className="skills-label"><Check size={14} style={{display:'inline', marginRight: '4px'}}/> Skills you have</div>
                <div>
                  {job.matched_skills.map(skill => (
                    <span key={skill} className="skill-tag skill-matched">{skill}</span>
                  ))}
                </div>
              </div>
            )}
            
            {job.missing_skills.length > 0 && (
              <div className="skills-container">
                <div className="skills-label"><X size={14} style={{display:'inline', marginRight: '4px'}}/> Missing skills to address</div>
                <div>
                  {job.missing_skills.map(skill => (
                    <span key={skill} className="skill-tag skill-missing">{skill}</span>
                  ))}
                </div>
              </div>
            )}
            
            {job.apply_url && (
              <a href={job.apply_url} target="_blank" rel="noopener noreferrer" className="btn apply-btn">
                Apply Now <ExternalLink size={16} />
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
