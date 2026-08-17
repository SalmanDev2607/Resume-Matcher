import React, { useState } from 'react';
import ResumeUpload from './components/ResumeUpload';
import JobSearch from './components/JobSearch';
import MatchResults from './components/MatchResults';
import ResumeAnalyzer from './components/ResumeAnalyzer';

function App() {
  const [appMode, setAppMode] = useState('matcher'); // 'matcher' or 'scorer'
  const [resumeText, setResumeText] = useState(null);
  const [matchResults, setMatchResults] = useState([]);

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 className="title">Resume Matcher</h1>
        <p className="subtitle">Find the perfect job for your skills and optimize your resume</p>
      </header>

      <main>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
          <button 
             className="btn"
             style={{ background: appMode === 'matcher' ? 'var(--accent-primary)' : 'rgba(30, 41, 59, 0.4)', color: appMode === 'matcher' ? 'white' : 'var(--text-muted)', border: '1px solid var(--glass-border)', boxShadow: appMode === 'matcher' ? '0 4px 14px 0 var(--accent-glow)' : 'none' }}
             onClick={() => setAppMode('matcher')}
          >Job Matcher</button>
          <button 
             className="btn"
             style={{ background: appMode === 'scorer' ? 'var(--accent-primary)' : 'rgba(30, 41, 59, 0.4)', color: appMode === 'scorer' ? 'white' : 'var(--text-muted)', border: '1px solid var(--glass-border)', boxShadow: appMode === 'scorer' ? '0 4px 14px 0 var(--accent-glow)' : 'none' }}
             onClick={() => setAppMode('scorer')}
          >Resume Scorer</button>
        </div>

        <div className="app-grid">
          <ResumeUpload onResumeUploaded={setResumeText} />
          {appMode === 'matcher' ? (
            <JobSearch 
              resumeText={resumeText} 
              onJobsFound={setMatchResults} 
              disabled={!resumeText}
            />
          ) : (
            <ResumeAnalyzer 
              resumeText={resumeText} 
              disabled={!resumeText} 
            />
          )}
        </div>

        {appMode === 'matcher' && matchResults.length > 0 && (
          <MatchResults results={matchResults} />
        )}
      </main>
    </div>
  );
}

export default App;
