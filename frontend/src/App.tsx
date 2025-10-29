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

  // Navigation functions
  const goToDashboard = () => {
    window.location.hash = '';
    setCurrentPage('dashboard');
  };

  const goToReview = () => {
    window.location.hash = 'review';
    setCurrentPage('review');
  };

  // Override window.location.href assignments with hash-based routing
  useEffect(() => {
    const originalLocation = window.location;
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: new Proxy(originalLocation, {
        set(target, prop, value) {
          if (prop === 'href') {
            if (value === '/') {
              goToDashboard();
              return true;
            } else if (value === '/review') {
              goToReview();
              return true;
            }
          }
          return Reflect.set(target, prop, value);
        },
      }),
    });
  }, []);

  return (
    <div className="app">
      {currentPage === 'dashboard' ? <Dashboard /> : <ReviewSession />}
    </div>
  );
}

export default App;
