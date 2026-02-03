/**
 * ExerciseExplanationModal - Shows detailed explanation for exercise answers
 */
import { useState } from 'react';
import { apiClient } from '@kapp/core';
import type { Exercise } from '@kapp/core';
import './ExerciseExplanationModal.css';

interface Props {
  exercise: Exercise;
  correctAnswer: string;
  basicExplanation?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ExerciseExplanationModal({
  exercise,
  correctAnswer,
  basicExplanation,
  isOpen,
  onClose
}: Props) {
  const [enhancedExplanation, setEnhancedExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEnhancedExplanation = async () => {
    if (enhancedExplanation || loading) return;

    setLoading(true);
    setError(null);

    try {
      // Use the LLM explain endpoint if available
      const result = await apiClient.getLLMExerciseExplanation(exercise.id, { level: 1 });
      setEnhancedExplanation(result.explanation);
    } catch (err: unknown) {
      console.error('Failed to fetch enhanced explanation:', err);

      // Provide more specific error messages
      let errorMessage = 'Unable to generate explanation.';
      if (err instanceof Error) {
        if (err.message.includes('timeout') || err.message.includes('Timeout')) {
          errorMessage = 'Request timed out. The AI model may be loading. Please try again.';
        } else if (err.message.includes('connect') || err.message.includes('network')) {
          errorMessage = 'Cannot connect to AI service. Please check your connection.';
        } else if (err.message.includes('model')) {
          errorMessage = 'AI model unavailable. Please check server configuration.';
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="exercise-explanation-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Explanation</h2>
          <button className="close-button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="exercise-reference">
            <div className="question-label">Question:</div>
            <div className="question-text">{exercise.question}</div>

            {exercise.korean_text && (
              <div className="korean-display">
                <span className="korean">{exercise.korean_text}</span>
                {exercise.romanization && (
                  <span className="romanization">({exercise.romanization})</span>
                )}
              </div>
            )}

            <div className="correct-answer">
              <span className="answer-label">Correct Answer:</span>
              <span className="answer-text">{correctAnswer}</span>
            </div>
          </div>

          {basicExplanation && (
            <div className="explanation-section">
              <h3>Explanation</h3>
              <p>{basicExplanation}</p>
            </div>
          )}

          {!enhancedExplanation && !loading && (
            <button
              className="get-more-btn"
              onClick={fetchEnhancedExplanation}
            >
              Get AI-Powered Explanation
            </button>
          )}

          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Generating explanation...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>{error}</p>
            </div>
          )}

          {enhancedExplanation && (
            <div className="enhanced-explanation">
              <h3>AI Explanation</h3>
              {enhancedExplanation.split('\n').map((paragraph, i) => (
                paragraph.trim() && <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="button button-primary">
            Got It!
          </button>
        </div>
      </div>
    </div>
  );
}
