/**
 * WeaknessReview - Practice weakest grammar patterns and vocabulary
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import type { WeaknessData, Exercise, ExerciseResult } from '@kapp/core';
import ExerciseRenderer from './ExerciseRenderer';
import { Skeleton } from './Skeleton';
import './WeaknessReview.css';

interface Props {
  onClose?: () => void;
}

type ViewMode = 'summary' | 'practice';

export default function WeaknessReview({ onClose }: Props) {
  const [weaknesses, setWeaknesses] = useState<WeaknessData | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<ExerciseResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sessionStats, setSessionStats] = useState({ reviewed: 0, correct: 0 });

  useEffect(() => {
    loadWeaknesses();
  }, []);

  useEffect(() => {
    setLastResult(null);
  }, [currentIndex]);

  async function loadWeaknesses() {
    try {
      setLoading(true);
      const data = await apiClient.getWeaknesses();
      setWeaknesses(data);
    } catch (err) {
      console.error('Failed to load weaknesses:', err);
      setError('Failed to load weakness data.');
    } finally {
      setLoading(false);
    }
  }

  async function startPractice() {
    try {
      setLoading(true);
      const data = await apiClient.getWeaknessExercises(20);
      setExercises(data.exercises);
      setViewMode('practice');
      setCurrentIndex(0);
      setSessionStats({ reviewed: 0, correct: 0 });
    } catch (err) {
      console.error('Failed to load weakness exercises:', err);
      setError('Failed to load exercises.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitAnswer(answer: string) {
    if (submitting || lastResult) return;
    const exercise = exercises[currentIndex];
    if (!exercise) return;

    setSubmitting(true);
    try {
      const result = await apiClient.submitExercise(exercise.id, answer);
      setLastResult(result);
      setSessionStats(prev => ({
        reviewed: prev.reviewed + 1,
        correct: prev.correct + (result.correct ? 1 : 0),
      }));
    } catch (err) {
      console.error('Failed to submit answer:', err);
    } finally {
      setSubmitting(false);
    }
  }

  function handleNextExercise() {
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setViewMode('summary');
      loadWeaknesses();
    }
  }

  if (loading) {
    return (
      <div className="weakness-review">
        <div className="weakness-header">
          <Skeleton variant="text" width={200} height={28} />
        </div>
        <Skeleton variant="rect" width="100%" height={200} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="weakness-review error">
        <p>{error}</p>
        <button onClick={loadWeaknesses}>Retry</button>
      </div>
    );
  }

  // Practice mode
  if (viewMode === 'practice' && exercises.length > 0) {
    const currentExercise = exercises[currentIndex];
    const progress = ((currentIndex + 1) / exercises.length) * 100;
    const isLastExercise = currentIndex === exercises.length - 1;

    return (
      <div className="weakness-review">
        <div className="weakness-header">
          <h2>Weakness Practice</h2>
          <p className="review-progress">{currentIndex + 1} / {exercises.length}</p>
        </div>

        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>

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
              <button className="next-button" onClick={handleNextExercise}>
                {isLastExercise ? 'Finish' : 'Next'}
              </button>
            </div>
          )}
        </div>

        <div className="session-stats-bar">
          <span>Correct: {sessionStats.correct} / {sessionStats.reviewed}</span>
        </div>
      </div>
    );
  }

  // Summary mode
  const hasWeaknesses = weaknesses &&
    (weaknesses.weak_grammar.length > 0 || weaknesses.weak_vocabulary.length > 0);

  return (
    <div className="weakness-review">
      <div className="weakness-header">
        <h2>Weak Areas</h2>
        {onClose && (
          <button className="close-btn" onClick={onClose}>Close</button>
        )}
      </div>

      {!hasWeaknesses ? (
        <div className="no-weaknesses">
          <h3>No weak areas detected</h3>
          <p>Complete more exercises to identify areas that need practice.</p>
        </div>
      ) : (
        <>
          {weaknesses!.weak_grammar.length > 0 && (
            <div className="weakness-section">
              <h3>Weak Grammar Patterns</h3>
              <div className="weakness-list">
                {weaknesses!.weak_grammar.map(item => (
                  <div key={item.pattern_id} className="weakness-item">
                    <div className="weakness-info">
                      <span className="weakness-title">{item.pattern_title}</span>
                      <span className="weakness-detail">
                        {item.correct}/{item.attempts} correct
                      </span>
                    </div>
                    <div className="mastery-bar">
                      <div
                        className="mastery-fill"
                        style={{ width: `${item.mastery_score}%` }}
                      />
                    </div>
                    <span className="mastery-score">{Math.round(item.mastery_score)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {weaknesses!.weak_vocabulary.length > 0 && (
            <div className="weakness-section">
              <h3>Weak Vocabulary</h3>
              <div className="weakness-list">
                {weaknesses!.weak_vocabulary.map(item => (
                  <div key={item.id} className="weakness-item">
                    <div className="weakness-info">
                      <span className="weakness-title">{item.korean}</span>
                      <span className="weakness-detail">{item.english}</span>
                    </div>
                    <div className="mastery-bar">
                      <div
                        className="mastery-fill"
                        style={{ width: `${item.accuracy_rate}%` }}
                      />
                    </div>
                    <span className="mastery-score">{Math.round(item.accuracy_rate)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button className="practice-btn" onClick={startPractice}>
            Practice Weak Areas
          </button>
        </>
      )}
    </div>
  );
}
