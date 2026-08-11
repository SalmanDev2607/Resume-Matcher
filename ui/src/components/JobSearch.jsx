import React, { useState } from 'react';
import { Search, MapPin, Briefcase } from 'lucide-react';
import axios from 'axios';

export default function JobSearch({ resumeText, onJobsFound, disabled }) {
  const [what, setWhat] = useState('');
  const [where, setWhere] = useState('Hyderabad');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!what) return;

    setIsSearching(true);

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8004';
    try {
      const response = await axios.post(`${API_BASE_URL}/api/jobs/search`, {
        what,
        where,
        pages: 1
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
        if (jobs.length === 0) alert('No jobs found for this search.');
      }

    } catch (error) {
      console.error('Error searching jobs:', error);
      alert('Failed to search jobs. Make sure Adzuna API keys are set in the backend environment.');
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
      </form>
    </div>
  );
}
