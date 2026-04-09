/**
 * ReadAloudExercise — F-08 Phase A
 * Show Korean text, play TTS model audio, self-rate pronunciation
 */
import { useState } from 'react';
import type { Exercise, ExerciseResult, ImmersionLevel } from '@kapp/core';
import { API_BASE_URL, savePronunciationCheck } from '@kapp/core';
import './ReadAloudExercise.css';

type Rating = 'good' | 'close' | 'again';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string) => void;
  result: ExerciseResult | null;
  submitting: boolean;
  immersionLevel?: ImmersionLevel;
}

export default function ReadAloudExercise({
  exercise,
  onSubmit,
  result,
  submitting,
  immersionLevel = 1,
}: Props) {
  const [hasPlayed, setHasPlayed] = useState(false);
  const [rating, setRating] = useState<Rating | null>(null);
  const isAnswered = result !== null;
  const hideRomanization = immersionLevel >= 2;

  function playAudio() {
    if (!exercise.audio_url) return;
    const audio = new Audio(`${API_BASE_URL}${exercise.audio_url}`);
    audio.play().catch(() => {});
    setHasPlayed(true);
  }

  async function handleRate(r: Rating) {
    setRating(r);
    try {
      await savePronunciationCheck({ exerciseId: exercise.id, rating: r === 'close' ? 'okay' : r, timestamp: Date.now() });
    } catch {}
  }

  function handleSubmit() {
    if (submitting || isAnswered) return;
    // Always submits as 'read_aloud' — backend auto-marks correct
    onSubmit('read_aloud');
  }

  return (
    <div className="read-aloud-exercise">
      <div className="exercise-type-badge">Read Aloud</div>

      {exercise.instruction && (
        <p className="exercise-instruction">{exercise.instruction}</p>
      )}

      <div className="exercise-question">
        <p>{exercise.question}</p>
      </div>

      {/* Large Korean text to read */}
      <div className="ra-text-card">
        <div className="ra-korean">{exercise.korean_text}</div>
        {exercise.romanization && !hideRomanization && (
          <div className="ra-romanization">{exercise.romanization}</div>
        )}
        {exercise.english_text && immersionLevel < 3 && (
          <div className="ra-english">{exercise.english_text}</div>
        )}
      </div>

      {/* Model audio */}
      {exercise.audio_url && (
        <div className="ra-audio-section">
          <button
            className={`ra-play-btn${hasPlayed ? ' played' : ' pulse'}`}
            onClick={playAudio}
            disabled={isAnswered}
          >
            {hasPlayed ? '🔊 Play Again' : '🔊 Hear Model Pronunciation'}
          </button>
        </div>
      )}

      {/* Self-rate section — shown after first play */}
      {hasPlayed && !isAnswered && (
        <div className="ra-self-check">
          <p className="ra-prompt">How did your pronunciation sound?</p>
          <div className="ra-rating-buttons">
            <button
              className={`ra-rating-btn good${rating === 'good' ? ' selected' : ''}`}
              onClick={() => handleRate('good')}
            >
              Good
            </button>
            <button
              className={`ra-rating-btn close${rating === 'close' ? ' selected' : ''}`}
              onClick={() => handleRate('close')}
            >
              Close
            </button>
            <button
              className={`ra-rating-btn again${rating === 'again' ? ' selected' : ''}`}
              onClick={() => handleRate('again')}
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {isAnswered && (
        <div className="ra-complete">
          <p className="ra-complete-text">
            {rating === 'good' && '✓ Great pronunciation practice!'}
            {rating === 'close' && '✓ Keep practicing — you\'re getting there!'}
            {rating === 'again' && '✓ Listen and repeat a few more times.'}
            {!rating && '✓ Practice recorded.'}
          </p>
          {exercise.explanation && (
            <p className="ra-explanation">{exercise.explanation}</p>
          )}
        </div>
      )}

      {!isAnswered && (
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={submitting || (!hasPlayed && !!exercise.audio_url)}
        >
          {submitting ? 'Saving...' : exercise.audio_url ? (hasPlayed ? 'Mark Complete' : 'Play audio first') : 'Mark Complete'}
        </button>
      )}
    </div>
  );
}
