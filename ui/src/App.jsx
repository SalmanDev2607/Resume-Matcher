import React, { useState } from 'react';
import ResumeUpload from './components/ResumeUpload';
import JobSearch from './components/JobSearch';
import MatchResults from './components/MatchResults';

function App() {
  const [resumeText, setResumeText] = useState(null);
  const [matchResults, setMatchResults] = useState([]);

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 className="title">Resume Matcher</h1>
        <p className="subtitle">Find the perfect job for your skills and optimize your resume</p>
      </header>

      <main>
        <div className="app-grid">
          <ResumeUpload onResumeUploaded={setResumeText} />
          <JobSearch 
            resumeText={resumeText} 
            onJobsFound={setMatchResults} 
            disabled={!resumeText}
          />
        </div>

        {matchResults.length > 0 && (
          <MatchResults results={matchResults} />
        )}
      </main>
    </div>
  );
}

export default App;
