/**
 * VocabularyReview - Spaced repetition vocabulary review component
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import type { VocabularyItem, ImmersionLevel } from '@kapp/core';
import { Skeleton } from './Skeleton';
import './VocabularyReview.css';

interface Props {
  onClose?: () => void;
  immersionLevel?: ImmersionLevel;
}

export default function VocabularyReview({ onClose, immersionLevel = 1 }: Props) {
  const [dueItems, setDueItems] = useState<VocabularyItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ totalDue: 0, newItems: 0 });
  const [sessionStats, setSessionStats] = useState({ reviewed: 0, correct: 0 });
  const [peekedCurrent, setPeekedCurrent] = useState(false);

  useEffect(() => {
    loadDueVocabulary();
  }, []);

  async function loadDueVocabulary() {
    try {
      setLoading(true);
      const data = await apiClient.getVocabularyDue(20);
      setDueItems(data.vocabulary);
      setStats({ totalDue: data.total_due, newItems: data.new_items });
    } catch (err) {
      console.error('Failed to load due vocabulary:', err);
      setError('Failed to load vocabulary. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleQualityRating(quality: number) {
    const currentItem = dueItems[currentIndex];
    if (!currentItem) return;

    try {
      const effectiveQuality = peekedCurrent ? Math.min(quality, 3) : quality;
      await apiClient.recordVocabularyReview(currentItem.id, effectiveQuality);

      // Update session stats
      setSessionStats(prev => ({
        reviewed: prev.reviewed + 1,
        correct: prev.correct + (effectiveQuality >= 3 ? 1 : 0)
      }));

      // Move to next item or finish
      if (currentIndex < dueItems.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setShowAnswer(false);
        setPeekedCurrent(false);
      } else {
        // Session complete
        handleSessionComplete(effectiveQuality);
      }
    } catch (err) {
      console.error('Failed to record review:', err);
      setError('Failed to save review. Please try again.');
    }
  }

  function handleSessionComplete(lastQuality: number) {
    const finalReviewed = sessionStats.reviewed + 1;
    const finalCorrect = sessionStats.correct + (lastQuality >= 3 ? 1 : 0);
    alert(`Review session complete!\n\nReviewed: ${finalReviewed}\nCorrect: ${finalCorrect}`);
    if (onClose) {
      onClose();
    }
  }

  function playAudio() {
    const currentItem = dueItems[currentIndex];
    if (currentItem?.audio_url) {
      const audio = new Audio(currentItem.audio_url);
      audio.play();
    }
  }

  if (loading) {
    return (
      <div className="vocabulary-review">
        <div className="review-header">
          <Skeleton variant="text" width={200} height={28} />
          <Skeleton variant="text" width={150} height={20} />
        </div>
        <div className="review-card">
          <Skeleton variant="rect" width="100%" height={200} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="vocabulary-review error">
        <p>{error}</p>
        <button onClick={loadDueVocabulary}>Retry</button>
      </div>
    );
  }

  if (dueItems.length === 0) {
    return (
      <div className="vocabulary-review empty">
        <h2>No vocabulary due for review</h2>
        <p>Great job! Come back later to review more words.</p>
        {onClose && <button onClick={onClose}>Close</button>}
      </div>
    );
  }

  const currentItem = dueItems[currentIndex];
  const progress = ((currentIndex + 1) / dueItems.length) * 100;

  return (
    <div className="vocabulary-review">
      <div className="review-header">
        <div className="header-info">
          <h2>Vocabulary Review</h2>
          <p className="review-progress">
            {currentIndex + 1} / {dueItems.length}
          </p>
        </div>
        <div className="session-stats">
          <span>Reviewed: {sessionStats.reviewed}</span>
          <span>Correct: {sessionStats.correct}</span>
          {stats.newItems > 0 && <span>New: {stats.newItems}</span>}
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="review-card">
        <div className="card-front">
          <h3 className="korean-text">{currentItem.korean}</h3>
          {currentItem.romanization && !showAnswer && immersionLevel < 2 && (
            <p className="romanization">{currentItem.romanization}</p>
          )}
          {currentItem.audio_url && (
            <button className="audio-button" onClick={playAudio}>
              Play Audio
            </button>
          )}
        </div>

        {showAnswer && (
          <div className="card-back">
            <p className="english-text">{currentItem.english}</p>
            {currentItem.part_of_speech && (
              <p className="part-of-speech">{currentItem.part_of_speech}</p>
            )}
            {currentItem.example_sentence_korean && (
              <div className="example">
                <p className="example-korean">{currentItem.example_sentence_korean}</p>
                {currentItem.example_sentence_english && immersionLevel < 3 && (
                  <p className="example-english">{currentItem.example_sentence_english}</p>
                )}
              </div>
            )}

            <div className="quality-buttons">
              <p className="rating-prompt">How well did you remember this?</p>
              {peekedCurrent && (
                <p className="peeked-note">Hint path used: max rating capped at 3.</p>
              )}
              <div className="button-grid">
                <button
                  className="quality-btn quality-0"
                  onClick={() => handleQualityRating(0)}
                  title="Complete blackout"
                >
                  0 - Forgot
                </button>
                <button
                  className="quality-btn quality-1"
                  onClick={() => handleQualityRating(1)}
                  title="Incorrect, but familiar"
                >
                  1 - Hard
                </button>
                <button
                  className="quality-btn quality-2"
                  onClick={() => handleQualityRating(2)}
                  title="Incorrect, seemed easy"
                >
                  2 - Wrong
                </button>
                <button
                  className="quality-btn quality-3"
                  onClick={() => handleQualityRating(3)}
                  title="Correct, but difficult"
                >
                  3 - Good
                </button>
                <button
                  className="quality-btn quality-4"
                  onClick={() => handleQualityRating(4)}
                  title="Correct with hesitation"
                  disabled={peekedCurrent}
                >
                  4 - Easy
                </button>
                <button
                  className="quality-btn quality-5"
                  onClick={() => handleQualityRating(5)}
                  title="Perfect recall"
                  disabled={peekedCurrent}
                >
                  5 - Perfect
                </button>
              </div>
            </div>
          </div>
        )}

        {!showAnswer && (
          <button
            className="show-answer-btn"
            onClick={() => {
              setShowAnswer(true);
              setPeekedCurrent(true);
            }}
          >
            Show Answer
          </button>
        )}
      </div>

      {onClose && (
        <button className="close-btn" onClick={onClose}>
          Exit Review
        </button>
      )}
    </div>
  );
}
