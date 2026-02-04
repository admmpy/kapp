/**
 * ExerciseRenderer - Renders different types of exercises
 */
import { useState } from 'react';
import type { Exercise, ExerciseResult } from '../types';
import { API_BASE_URL } from '../api/client';
import SentenceArrangeExercise from './SentenceArrangeExercise';
import './ExerciseRenderer.css';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string) => void;
  result: ExerciseResult | null;
  submitting: boolean;
}

export default function ExerciseRenderer({ exercise, onSubmit, result, submitting }: Props) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [textAnswer, setTextAnswer] = useState('');

  // Route sentence_arrange exercises to dedicated component
  if (exercise.exercise_type === 'sentence_arrange') {
    return (
      <SentenceArrangeExercise
        exercise={exercise}
        onSubmit={onSubmit}
        result={result}
        submitting={submitting}
      />
    );
  }

  const hasOptions = exercise.options && exercise.options.length > 0;
  const isAnswered = result !== null;

  function handleOptionSelect(option: string) {
    if (isAnswered || submitting) return;
    setSelectedOption(option);
  }

  function handleSubmit() {
    if (submitting || isAnswered) return;

    if (hasOptions && selectedOption) {
      onSubmit(selectedOption);
    } else if (!hasOptions && textAnswer.trim()) {
      onSubmit(textAnswer.trim());
    }
  }

  function handleKeyPress(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function getOptionClass(option: string): string {
    let classes = 'option-button';

    if (selectedOption === option) {
      classes += ' selected';
    }

    if (isAnswered) {
      if (option === result?.correct_answer) {
        classes += ' correct';
      } else if (selectedOption === option && !result?.correct) {
        classes += ' incorrect';
      }
    }

    return classes;
  }

  function playAudio() {
    if (exercise.audio_url) {
      const audio = new Audio(`${API_BASE_URL}${exercise.audio_url}`);
      audio.play().catch(err => console.error('Audio playback failed:', err));
    }
  }

  return (
    <div className={`exercise-renderer ${exercise.exercise_type}`}>
      {/* Exercise type badge */}
      <div className="exercise-type-badge">
        {exercise.exercise_type.charAt(0).toUpperCase() + exercise.exercise_type.slice(1)}
      </div>

      {/* Instruction */}
      {exercise.instruction && (
        <p className="exercise-instruction">{exercise.instruction}</p>
      )}

      {/* Question */}
      <div className="exercise-question">
        <p>{exercise.question}</p>
      </div>

      {/* Korean text display (for vocabulary exercises, NOT listening) */}
      {exercise.korean_text && exercise.exercise_type !== 'listening' && (
        <div className="korean-display">
          <div className="korean-text">{exercise.korean_text}</div>
          {exercise.romanization && (
            <div className="romanization">{exercise.romanization}</div>
          )}
          {exercise.audio_url && (
            <button className="audio-button" onClick={playAudio} title="Play audio">
              🔊
            </button>
          )}
        </div>
      )}

      {/* Reading content */}
      {exercise.content_text && exercise.exercise_type === 'reading' && (
        <div className="reading-content">
          {exercise.content_text}
        </div>
      )}

      {/* Listening exercise audio */}
      {exercise.exercise_type === 'listening' && exercise.audio_url && (
        <div className="listening-controls">
          <button className="play-audio-btn" onClick={playAudio}>
            🔊 Play Audio
          </button>
        </div>
      )}

      {/* Answer section */}
      <div className="answer-section">
        {hasOptions ? (
          <div className="options-grid">
            {(exercise.options as string[]).map((option, index) => (
              <button
                key={index}
                className={getOptionClass(option)}
                onClick={() => handleOptionSelect(option)}
                disabled={isAnswered || submitting}
              >
                {option}
              </button>
            ))}
          </div>
        ) : (
          <div className="text-answer">
            <input
              type="text"
              value={textAnswer}
              onChange={(e) => setTextAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your answer..."
              disabled={isAnswered || submitting}
              autoFocus
            />
          </div>
        )}
      </div>

      {/* Submit button */}
      {!isAnswered && (
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={submitting || (hasOptions ? !selectedOption : !textAnswer.trim())}
        >
          {submitting ? 'Checking...' : 'Check Answer'}
        </button>
      )}
    </div>
  );
}
