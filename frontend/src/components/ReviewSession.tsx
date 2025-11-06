/**
 * ReviewSession component handles the main learning workflow
 */
import { useState, useEffect } from 'react';
import FlashCard from './FlashCard';
import apiClient from '../api/client';
import type { Card } from '../types';
import './ReviewSession.css';

const QUALITY_RATINGS = [
  { value: 0, label: 'Complete blackout', emoji: '😰', color: '#f44336' },
  { value: 1, label: 'Incorrect; familiar', emoji: '😕', color: '#ff9800' },
  { value: 2, label: 'Incorrect; correct remembered', emoji: '😐', color: '#ff9800' },
  { value: 3, label: 'Correct with difficulty', emoji: '🙂', color: '#ffc107' },
  { value: 4, label: 'Correct after hesitation', emoji: '😊', color: '#8bc34a' },
  { value: 5, label: 'Perfect response', emoji: '😄', color: '#4caf50' },
];

function parseHashParams() {
  const query = window.location.hash.split('?')[1] || '';
  const params = new URLSearchParams(query);
  const deckIdParam = params.get('deck_id');
  const levelParam = params.get('level');
  return {
    deck_id: deckIdParam ? Number(deckIdParam) : undefined,
    level: levelParam ? Number(levelParam) : undefined,
  };
}

export default function ReviewSession() {
  const [cards, setCards] = useState<Card[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showBack, setShowBack] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());

  useEffect(() => {
    const handleHashChange = () => {
      loadCards();
    };

    loadCards();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const loadCards = async () => {
    try {
      setLoading(true);
      setError(null);
      const filters = parseHashParams();
      const response = await apiClient.getDueCards({ limit: 20, deck_id: filters.deck_id, level: filters.level });
      
      if (response.cards.length === 0) {
        setSessionComplete(true);
      } else {
        setCards(response.cards);
        setCurrentIndex(0);
        setShowBack(false);
        setStartTime(Date.now());
      }
    } catch (err) {
      console.error('Error loading cards:', err);
      setError('Failed to load cards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (rating: number) => {
    if (submitting || !currentCard) return;

    try {
      setSubmitting(true);
      
      // Calculate time spent in seconds
      const timeSpent = (Date.now() - startTime) / 1000;

      // Submit review
      await apiClient.submitReview({
        card_id: currentCard.id,
        quality_rating: rating,
        time_spent: timeSpent,
      });

      setReviewedCount(prev => prev + 1);

      // Move to next card
      if (currentIndex < cards.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setShowBack(false);
        setStartTime(Date.now());
      } else {
        setSessionComplete(true);
      }
    } catch (err) {
      console.error('Error submitting review:', err);
      setError('Failed to submit review. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevealAnswer = () => {
    setShowBack(true);
  };

  const handleSkipCard = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setShowBack(false);
      setStartTime(Date.now());
    } else {
      setSessionComplete(true);
    }
  };

  const handleRestart = () => {
    setSessionComplete(false);
    setReviewedCount(0);
    loadCards();
  };

  if (loading) {
    return (
      <div className="review-session loading">
        <div className="spinner"></div>
        <p>Loading cards...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="review-session error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={loadCards} className="button button-primary">
          Try Again
        </button>
      </div>
    );
  }

  if (sessionComplete) {
    return (
      <div className="review-session complete">
        <div className="completion-message">
          <h1>🎉 Session Complete!</h1>
          <p className="stats">You reviewed <strong>{reviewedCount}</strong> cards</p>
          <div className="completion-actions">
            <button onClick={handleRestart} className="button button-primary">
              Start New Session
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="button button-secondary"
            >
              View Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const progress = ((currentIndex + 1) / cards.length) * 100;

  return (
    <div className="review-session">
      {/* Home button */}
      <div className="review-header">
        <button
          onClick={() => window.location.hash = ''}
          className="home-button"
          aria-label="Return to dashboard"
        >
          ← Dashboard
        </button>
      </div>

      {/* Progress bar */}
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      {/* Card counter */}
      <div className="card-counter">
        Card {currentIndex + 1} of {cards.length}
      </div>

      {/* FlashCard */}
      <FlashCard 
        card={currentCard} 
        showBack={showBack} 
        onFlip={() => setShowBack(prev => !prev)}
        autoPlayOnFlip={true}
      />

      {/* Action buttons */}
      <div className="actions">
        {!showBack ? (
          <div className="action-buttons-row">
            <button
              onClick={handleRevealAnswer}
              className="button button-large button-primary"
            >
              Show Answer
            </button>
            <button
              onClick={handleSkipCard}
              className="button button-large button-secondary"
            >
              Skip →
            </button>
          </div>
        ) : (
          <div className="rating-buttons">
            <p className="rating-prompt">How well did you remember?</p>
            <div className="rating-grid">
              {QUALITY_RATINGS.map((rating) => (
                <button
                  key={rating.value}
                  onClick={() => handleRating(rating.value)}
                  disabled={submitting}
                  className="rating-button"
                  style={{ borderColor: rating.color }}
                >
                  <span className="rating-emoji">{rating.emoji}</span>
                  <span className="rating-value">{rating.value}</span>
                  <span className="rating-label">{rating.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {submitting && (
        <div className="submitting-overlay">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
}
