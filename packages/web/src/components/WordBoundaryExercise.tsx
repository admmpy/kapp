/**
 * WordBoundaryExercise - Tap between characters to insert word spaces
 * F-05: Phonological chunking trainer
 */
import { useState } from 'react';
import type { Exercise, ExerciseResult } from '@kapp/core';
import './WordBoundaryExercise.css';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string) => void;
  result: ExerciseResult | null;
  submitting: boolean;
}

export default function WordBoundaryExercise({ exercise, onSubmit, result, submitting }: Props) {
  const chars = (exercise.korean_text || '').split('');
  // gaps[i] = true means there's a space between chars[i] and chars[i+1]
  const [gaps, setGaps] = useState<boolean[]>(() => new Array(Math.max(0, chars.length - 1)).fill(false));

  const isAnswered = result !== null;

  function toggleGap(i: number) {
    if (isAnswered || submitting) return;
    setGaps((prev) => prev.map((v, idx) => (idx === i ? !v : v)));
  }

  function buildAnswer(): string {
    let out = '';
    for (let i = 0; i < chars.length; i++) {
      out += chars[i];
      if (i < gaps.length && gaps[i]) out += ' ';
    }
    return out;
  }

  function handleSubmit() {
    if (submitting || isAnswered) return;
    onSubmit(buildAnswer());
  }

  // Compute per-gap correctness for feedback
  const correctSpaced = exercise.correct_answer || '';
  const correctChars = correctSpaced.split('');
  // Build a set of gap positions where a space should appear
  const correctGaps = new Set<number>();
  if (isAnswered) {
    let origIdx = 0;
    for (let ci = 0; ci < correctChars.length; ci++) {
      if (correctChars[ci] === ' ') {
        // gap before next char, which is chars[origIdx]
        correctGaps.add(origIdx - 1);
      } else {
        origIdx++;
      }
    }
  }

  return (
    <div className="word-boundary-exercise">
      <div className="exercise-type-badge">Word Boundary</div>

      {exercise.instruction && (
        <p className="exercise-instruction">{exercise.instruction}</p>
      )}

      <div className="exercise-question">
        <p>{exercise.question}</p>
      </div>

      <div className="wb-char-row">
        {chars.map((ch, i) => (
          <span key={i} className="wb-char-group">
            <span className="wb-char">{ch}</span>
            {i < gaps.length && (
              <button
                className={`wb-gap${gaps[i] ? ' active' : ''}${
                  isAnswered
                    ? correctGaps.has(i)
                      ? gaps[i] ? ' gap-correct' : ' gap-missed'
                      : gaps[i] ? ' gap-wrong' : ''
                    : ''
                }`}
                onClick={() => toggleGap(i)}
                disabled={isAnswered || submitting}
                aria-label={gaps[i] ? 'Remove space' : 'Add space'}
              >
                {gaps[i] ? '|' : '·'}
              </button>
            )}
          </span>
        ))}
      </div>

      {isAnswered && (
        <div className={`wb-result ${result?.correct ? 'correct' : 'incorrect'}`}>
          <div className="result-icon">{result?.correct ? '✓' : '✗'}</div>
          {!result?.correct && (
            <div className="wb-correct-answer">
              <span className="wb-correct-label">Correct: </span>
              <span className="wb-correct-text">{exercise.correct_answer}</span>
            </div>
          )}
          {exercise.explanation && (
            <div className="wb-explanation">{exercise.explanation}</div>
          )}
        </div>
      )}

      {!isAnswered && (
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={submitting || gaps.every((g) => !g)}
        >
          {submitting ? 'Checking...' : 'Check Boundaries'}
        </button>
      )}
    </div>
  );
}
