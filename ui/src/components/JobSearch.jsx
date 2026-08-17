import React, { useState } from 'react';
import { Search, MapPin, Briefcase } from 'lucide-react';
import axios from 'axios';

export default function JobSearch({ resumeText, onJobsFound, disabled }) {
  const [what, setWhat] = useState('');
  const [where, setWhere] = useState('Hyderabad');
  const [experience, setExperience] = useState('');
  const [source, setSource] = useState('both');
  const [isSearching, setIsSearching] = useState(false);
  const [searchMessage, setSearchMessage] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!what) return;

    setIsSearching(true);
    setSearchMessage('');

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8004';
    try {
      const response = await axios.post(`${API_BASE_URL}/api/jobs/search`, {
        what,
        where,
        pages: 1,
        source,
        experience
      });

      const jobs = response.data.jobs;

      if (jobs.length > 0 && resumeText) {
        // Now run the comparison
        const compareRes = await axios.post(`${API_BASE_URL}/api/jobs/compare`, {
          resume_text: resumeText,
          jobs: jobs
        });
        onJobsFound(compareRes.data.results);
      } else {
        onJobsFound([]);
        if (jobs.length === 0) {
          setSearchMessage('No jobs found for this search. The selected platform(s) might be blocking the request or have no results.');
        }
      }

    } catch (error) {
      console.error('Error searching jobs:', error);
      setSearchMessage('Failed to search jobs. Make sure the backend server is running and credentials are set.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className={`glass-card ${disabled ? 'opacity-50' : ''}`} style={{ opacity: disabled ? 0.6 : 1, transition: 'opacity 0.3s' }}>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: 600 }}>2. Search Jobs</h2>

      <form onSubmit={handleSearch}>
        <div className="input-group">
          <label htmlFor="what"><Briefcase size={14} style={{ display: 'inline', marginRight: '4px' }} /> Job Title or Keywords</label>
          <input
            type="text"
            id="what"
            className="input-field"
            placeholder="e.g. Backend Developer Node.js"
            value={what}
            onChange={(e) => setWhat(e.target.value)}
            disabled={disabled || isSearching}
            required
          />
        </div>

        <div className="input-group">
          <label htmlFor="where"><MapPin size={14} style={{ display: 'inline', marginRight: '4px' }} /> Location</label>
          <input
            type="text"
            id="where"
            className="input-field"
            placeholder="e.g. Hyderabad, India"
            value={where}
            onChange={(e) => setWhere(e.target.value)}
            disabled={disabled || isSearching}
          />
        </div>

        <div className="input-group">
          <label htmlFor="experience"><Briefcase size={14} style={{ display: 'inline', marginRight: '4px' }} /> Experience Level</label>
          <select
            id="experience"
            className="input-field"
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
            disabled={disabled || isSearching}
            style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-color)', color: 'var(--text-color)' }}
          >
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="">Any Experience</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="Entry Level / Fresher">Entry Level / Fresher</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="Mid Level (1-3 years)">Mid Level (1-3 years)</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="Senior Level (4+ years)">Senior Level (4+ years)</option>
          </select>
        </div>

        <div className="input-group">
          <label htmlFor="source"><Briefcase size={14} style={{ display: 'inline', marginRight: '4px' }} /> Source</label>
          <select
            id="source"
            className="input-field"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            disabled={disabled || isSearching}
            style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'var(--bg-color)', color: 'var(--text-color)' }}
          >
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="both">All Sources</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="linkedin">LinkedIn</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="indeed">Indeed</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="glassdoor">Glassdoor</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="zip_recruiter">ZipRecruiter</option>
            <option style={{ background: 'var(--bg-color)', color: 'var(--text-color)' }} value="adzuna">Adzuna</option>
          </select>
        </div>

        <button
          type="submit"
          className="btn"
          style={{ width: '100%', marginTop: '0.5rem' }}
          disabled={disabled || isSearching || !what}
        >
          {isSearching ? (
            <>
              <Search className="spinner" size={18} />
              Searching & Scoring...
            </>
          ) : (
            <>
              <Search size={18} />
              Find Matches
            </>
          )}
        </button>
        
        {searchMessage && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: 'var(--danger)', fontSize: '0.9rem', textAlign: 'center' }}>
            {searchMessage}
          </div>
        )}
      </form>
    </div>
  );
}
