/**
 * ExerciseReview - Sentence-level spaced repetition review
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import type { DueExercise, ExerciseResult } from '@kapp/core';
import ExerciseRenderer from './ExerciseRenderer';
import { Skeleton, ExerciseSkeleton } from './Skeleton';
import './ExerciseReview.css';

interface Props {
  onClose?: () => void;
}

export default function ExerciseReview({ onClose }: Props) {
  const [dueExercises, setDueExercises] = useState<DueExercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<ExerciseResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sessionStats, setSessionStats] = useState({ reviewed: 0, correct: 0 });
  const [sessionComplete, setSessionComplete] = useState(false);

  useEffect(() => {
    loadDueExercises();
  }, []);

  // Clear result when exercise changes
  useEffect(() => {
    setLastResult(null);
  }, [currentIndex]);

  async function loadDueExercises() {
    try {
      setLoading(true);
      const data = await apiClient.getExercisesDue(20);
      setDueExercises(data.exercises);
    } catch (err) {
      console.error('Failed to load due exercises:', err);
      setError('Failed to load exercises for review. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitAnswer(answer: string) {
    if (submitting || lastResult) return;
    const exercise = dueExercises[currentIndex];
    if (!exercise) return;

    setSubmitting(true);
    try {
      const result = await apiClient.submitExercise(exercise.id, answer);
      setLastResult(result);

      // Auto-rate: correct = quality 4, incorrect = quality 1
      const quality = result.correct ? 4 : 1;
      await apiClient.recordExerciseReview(exercise.id, quality);

      setSessionStats(prev => ({
        reviewed: prev.reviewed + 1,
        correct: prev.correct + (result.correct ? 1 : 0),
      }));
    } catch (err) {
      console.error('Failed to submit review:', err);
      setError('Failed to save review. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  function handleNextExercise() {
    if (currentIndex < dueExercises.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setSessionComplete(true);
    }
  }

  if (loading) {
    return (
      <div className="exercise-review">
        <div className="review-header">
          <Skeleton variant="text" width={200} height={28} />
          <Skeleton variant="text" width={150} height={20} />
        </div>
        <ExerciseSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="exercise-review error">
        <p>{error}</p>
        <button onClick={loadDueExercises}>Retry</button>
      </div>
    );
  }

  if (dueExercises.length === 0) {
    return (
      <div className="exercise-review empty">
        <h2>No exercises due for review</h2>
        <p>Complete more lessons to build your review queue.</p>
        {onClose && <button onClick={onClose}>Close</button>}
      </div>
    );
  }

  if (sessionComplete) {
    const accuracy = sessionStats.reviewed > 0
      ? Math.round((sessionStats.correct / sessionStats.reviewed) * 100)
      : 0;

    return (
      <div className="exercise-review session-complete">
        <h2>Review Complete</h2>
        <div className="session-summary">
          <div className="summary-stat">
            <span className="stat-value">{sessionStats.reviewed}</span>
            <span className="stat-label">Reviewed</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{sessionStats.correct}</span>
            <span className="stat-label">Correct</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{accuracy}%</span>
            <span className="stat-label">Accuracy</span>
          </div>
        </div>
        {onClose && (
          <button className="done-btn" onClick={onClose}>Done</button>
        )}
      </div>
    );
  }

  const currentExercise = dueExercises[currentIndex];
  const progress = ((currentIndex + 1) / dueExercises.length) * 100;
  const isLastExercise = currentIndex === dueExercises.length - 1;

  return (
    <div className="exercise-review">
      <div className="review-header">
        <div className="header-info">
          <h2>Exercise Review</h2>
          <p className="review-progress">
            {currentIndex + 1} / {dueExercises.length}
          </p>
        </div>
        <div className="session-stats">
          <span>Correct: {sessionStats.correct}</span>
          <span>Reviewed: {sessionStats.reviewed}</span>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>

      {currentExercise.lesson_title && (
        <p className="exercise-source">From: {currentExercise.lesson_title}</p>
      )}

      <div className="exercise-container">
        <ExerciseRenderer
          key={currentExercise.id}
          exercise={currentExercise}
          onSubmit={handleSubmitAnswer}
          result={lastResult}
          submitting={submitting}
        />

        {lastResult && (
          <div className={`result-feedback ${lastResult.correct ? 'correct' : 'incorrect'}`}>
            <div className="result-icon">
              {lastResult.correct ? '\u2713' : '\u2717'}
            </div>
            <div className="result-message">
              {lastResult.correct ? 'Correct!' : 'Not quite...'}
            </div>
            {!lastResult.correct && (
              <div className="correct-answer">
                Correct answer: <strong>{lastResult.correct_answer}</strong>
              </div>
            )}
            {lastResult.explanation && (
              <div className="result-explanation">
                {lastResult.explanation}
              </div>
            )}
            <button className="next-button" onClick={handleNextExercise}>
              {isLastExercise ? 'Finish Review' : 'Next Exercise'}
            </button>
          </div>
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
