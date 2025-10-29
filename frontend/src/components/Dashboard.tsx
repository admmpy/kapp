/**
 * Dashboard component displays learning statistics and progress
 */
import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import type { Stats } from '../types';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const handleStartReview = () => {
    window.location.href = '/review';
  };

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="spinner"></div>
        <p>Loading statistics...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="dashboard error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={loadStats} className="button button-primary">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🇰🇷 Kapp</h1>
        <p className="tagline">Korean Learning with Spaced Repetition</p>
      </header>

      {/* Quick Stats */}
      <div className="stats-overview">
        <div className="stat-card highlight">
          <div className="stat-value">{stats.cards_due_today}</div>
          <div className="stat-label">Cards Due Today</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats.cards_reviewed_today}</div>
          <div className="stat-label">Reviewed Today</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats.accuracy_rate}%</div>
          <div className="stat-label">Accuracy Rate</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats.streak_days}</div>
          <div className="stat-label">Day Streak 🔥</div>
        </div>
      </div>

      {/* Action Button */}
      {stats.cards_due_today > 0 ? (
        <button
          onClick={handleStartReview}
          className="button button-large button-primary start-review-btn"
        >
          Start Reviewing ({stats.cards_due_today} cards)
        </button>
      ) : (
        <div className="no-cards-message">
          <h3>🎉 All caught up!</h3>
          <p>No cards due for review right now.</p>
          <p className="next-review-hint">Come back tomorrow to continue learning!</p>
        </div>
      )}

      {/* Overall Progress */}
      <div className="progress-section">
        <h2>Overall Progress</h2>
        <div className="progress-stats">
          <div className="progress-item">
            <span className="progress-label">Total Cards</span>
            <span className="progress-value">{stats.total_cards}</span>
          </div>
          <div className="progress-item">
            <span className="progress-label">New Cards</span>
            <span className="progress-value">{stats.new_cards}</span>
          </div>
          <div className="progress-item">
            <span className="progress-label">Total Reviews</span>
            <span className="progress-value">{stats.total_reviews}</span>
          </div>
        </div>
      </div>

      {/* Decks */}
      <div className="decks-section">
        <h2>Your Decks</h2>
        <div className="decks-grid">
          {stats.decks.map((deck) => (
            <div key={deck.id} className="deck-card">
              <h3 className="deck-name">{deck.name}</h3>
              {deck.description && (
                <p className="deck-description">{deck.description}</p>
              )}
              <div className="deck-stats">
                <span className="deck-stat">
                  <strong>{deck.due_cards || 0}</strong> due
                </span>
                <span className="deck-stat">
                  <strong>{deck.total_cards || 0}</strong> total
                </span>
                <span className="deck-level">Level {deck.level}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>Keep practicing daily to improve your Korean! 화이팅! 💪</p>
      </footer>
    </div>
  );
}
