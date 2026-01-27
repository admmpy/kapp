/**
 * LessonView - Main lesson interface with exercises
 */
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { Lesson, ExerciseResult } from '../types';
import ExerciseRenderer from './ExerciseRenderer';
import ProgressBar from './ProgressBar';
import './LessonView.css';

interface Props {
  lessonId: number;
  onComplete: () => void;
  onBack: () => void;
}

export default function LessonView({ lessonId, onComplete, onBack }: Props) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [showGrammar, setShowGrammar] = useState(true);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [totalAnswered, setTotalAnswered] = useState(0);
  const [lastResult, setLastResult] = useState<ExerciseResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    async function loadLesson() {
      try {
        const data = await apiClient.getLesson(lessonId);
        setLesson(data);
        await apiClient.startLesson(lessonId);
      } catch (err) {
        console.error('Failed to load lesson:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLesson();
  }, [lessonId]);

  async function handleSubmitAnswer(answer: string) {
    if (!lesson?.exercises || submitting) return;

    const exercise = lesson.exercises[currentExerciseIndex];
    setSubmitting(true);

    try {
      const result = await apiClient.submitExercise(exercise.id, answer);
      setLastResult(result);
      setTotalAnswered(prev => prev + 1);
      if (result.correct) {
        setCorrectAnswers(prev => prev + 1);
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleNextExercise() {
    if (!lesson?.exercises) return;

    setLastResult(null);

    if (currentExerciseIndex < lesson.exercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
    } else {
      // Lesson complete
      const timeSpent = Math.round((Date.now() - startTime) / 1000);
      const score = totalAnswered > 0 ? (correctAnswers / totalAnswered) * 100 : 0;

      try {
        await apiClient.completeLesson(lessonId, {
          score,
          time_spent_seconds: timeSpent
        });
      } catch (err) {
        console.error('Failed to complete lesson:', err);
      }

      onComplete();
    }
  }

  function handleStartExercises() {
    setShowGrammar(false);
  }

  if (loading) {
    return (
      <div className="lesson-view loading">
        <div className="loading-spinner"></div>
        <p>Loading lesson...</p>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="lesson-view error">
        <p>Lesson not found</p>
        <button onClick={onBack}>Back</button>
      </div>
    );
  }

  const exercises = lesson.exercises || [];
  const currentExercise = exercises[currentExerciseIndex];
  const isLastExercise = currentExerciseIndex === exercises.length - 1;

  // Show grammar explanation first
  if (showGrammar && lesson.grammar_explanation) {
    return (
      <div className="lesson-view">
        <header className="lesson-header">
          <button className="back-button" onClick={onBack}>← Back</button>
          <h1>{lesson.title}</h1>
        </header>

        <div className="grammar-section">
          <h2>Grammar</h2>
          <div className="grammar-content">
            {lesson.grammar_explanation.split('\n').map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
          {lesson.grammar_tip && (
            <div className="grammar-tip">
              <strong>Tip:</strong> {lesson.grammar_tip}
            </div>
          )}
          <button className="start-exercises-btn" onClick={handleStartExercises}>
            Start Exercises ({exercises.length})
          </button>
        </div>
      </div>
    );
  }

  // No exercises
  if (exercises.length === 0) {
    return (
      <div className="lesson-view">
        <header className="lesson-header">
          <button className="back-button" onClick={onBack}>← Back</button>
          <h1>{lesson.title}</h1>
        </header>
        <div className="no-exercises">
          <p>No exercises available for this lesson.</p>
          <button onClick={onComplete}>Complete Lesson</button>
        </div>
      </div>
    );
  }

  return (
    <div className="lesson-view">
      <header className="lesson-header">
        <button className="back-button" onClick={onBack}>← Back</button>
        <h1>{lesson.title}</h1>
        <ProgressBar
          current={currentExerciseIndex + 1}
          total={exercises.length}
          correct={correctAnswers}
        />
      </header>

      <div className="exercise-container">
        <ExerciseRenderer
          exercise={currentExercise}
          onSubmit={handleSubmitAnswer}
          result={lastResult}
          submitting={submitting}
        />

        {lastResult && (
          <div className={`result-feedback ${lastResult.correct ? 'correct' : 'incorrect'}`}>
            <div className="result-icon">
              {lastResult.correct ? '✓' : '✗'}
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
              {isLastExercise ? 'Complete Lesson' : 'Next Exercise'}
            </button>
          </div>
        )}
      </div>

      <div className="lesson-progress-summary">
        <span>{correctAnswers} correct</span>
        <span>{totalAnswered - correctAnswers} incorrect</span>
      </div>
    </div>
  );
}
