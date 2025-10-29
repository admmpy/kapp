/**
 * Main App component - handles routing between Dashboard and Review Session
 */
import { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import ReviewSession from './components/ReviewSession';
import './App.css';

type Page = 'dashboard' | 'review';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  // Simple routing based on URL hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1); // Remove #
      if (hash === 'review') {
        setCurrentPage('review');
      } else {
        setCurrentPage('dashboard');
      }
    };

    // Initial check
    handleHashChange();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);
    
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return (
    <div className="app">
      {currentPage === 'dashboard' ? <Dashboard /> : <ReviewSession />}
    </div>
  );
}

export default App;
