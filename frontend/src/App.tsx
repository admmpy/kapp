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
  const [dashboardKey, setDashboardKey] = useState(0);
  const [reviewKey, setReviewKey] = useState(0);

  // Simple routing based on URL hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1); // Remove #
      // Check if hash starts with 'review' (handles both #review and #review?deck_id=1)
      if (hash.startsWith('review')) {
        setCurrentPage('review');
        setReviewKey(prev => prev + 1);
      } else {
        setCurrentPage('dashboard');
        // Increment key to force Dashboard remount and refresh stats
        setDashboardKey(prev => prev + 1);
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
      {currentPage === 'dashboard' ? (
        <Dashboard key={dashboardKey} />
      ) : (
        <ReviewSession key={reviewKey} />
      )}
    </div>
  );
}

export default App;
