/**
 * ExerciseRenderer - Renders different types of exercises
 */
import { useState } from 'react';
import type { Exercise, ExerciseResult, PronunciationSelfCheck as PronCheck, ImmersionLevel } from '@kapp/core';
import { API_BASE_URL, PRONUNCIATION_SELF_CHECK_ENABLED, savePronunciationCheck } from '@kapp/core';
import SentenceArrangeExercise from './SentenceArrangeExercise';
import './ExerciseRenderer.css';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string, meta?: { peeked?: boolean }) => void;
  result: ExerciseResult | null;
  submitting: boolean;
  immersionLevel?: ImmersionLevel;
  forceAttemptFirst?: boolean;
}

type PlaybackSpeed = 0.5 | 1.0 | 1.2;

export default function ExerciseRenderer({
  exercise,
  onSubmit,
  result,
  submitting,
  immersionLevel = 1,
  forceAttemptFirst = false,
}: Props) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [textAnswer, setTextAnswer] = useState('');
  const [writingAnswer, setWritingAnswer] = useState('');
  const [attemptText, setAttemptText] = useState('');
  const [attemptUnlocked, setAttemptUnlocked] = useState(false);
  const [usedAssist, setUsedAssist] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1.0);
  const [selfCheckDone, setSelfCheckDone] = useState(false);
  const [selfCheckRating, setSelfCheckRating] = useState<PronCheck['rating'] | null>(null);

  const hideRomanization = immersionLevel >= 2;
  const hideEnglishHints = immersionLevel >= 3;

  // Route sentence_arrange exercises to dedicated component
  if (exercise.exercise_type === 'sentence_arrange') {
    return (
      <SentenceArrangeExercise
        exercise={exercise}
        onSubmit={onSubmit}
        result={result}
        submitting={submitting}
        immersionLevel={immersionLevel}
      />
    );
  }

  const hasOptions = exercise.options && exercise.options.length > 0;
  const isAnswered = result !== null;
  const attemptFirstRequired =
    forceAttemptFirst
    && hasOptions
    && (exercise.exercise_type === 'vocabulary' || exercise.exercise_type === 'listening');
  const canShowOptions = !attemptFirstRequired || attemptUnlocked || isAnswered;

  function handleOptionSelect(option: string) {
    if (isAnswered || submitting) return;
    setSelectedOption(option);
  }

  function handleSubmit() {
    if (submitting || isAnswered) return;

    if (exercise.exercise_type === 'writing' && writingAnswer.trim()) {
      onSubmit(writingAnswer.trim());
    } else if (hasOptions && selectedOption) {
      onSubmit(selectedOption, { peeked: usedAssist });
    } else if (!hasOptions && textAnswer.trim()) {
      onSubmit(textAnswer.trim());
    }
  }

  function unlockOptionsFromAttempt() {
    if (submitting || isAnswered || !attemptText.trim()) return;
    setAttemptUnlocked(true);
  }

  function unlockOptionsWithHint() {
    if (submitting || isAnswered) return;
    setAttemptUnlocked(true);
    setUsedAssist(true);
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

  function playAudio(speed: PlaybackSpeed = playbackSpeed) {
    if (exercise.audio_url) {
      const audio = new Audio(`${API_BASE_URL}${exercise.audio_url}`);
      audio.playbackRate = speed;
      audio.play().catch(err => console.error('Audio playback failed:', err));
    }
  }

  const showSelfCheck = PRONUNCIATION_SELF_CHECK_ENABLED
    && exercise.audio_url
    && (exercise.exercise_type === 'listening' || exercise.exercise_type === 'vocabulary');

  async function handleSelfCheck(rating: PronCheck['rating']) {
    setSelfCheckRating(rating);
    setSelfCheckDone(true);
    try {
      await savePronunciationCheck({
        exerciseId: exercise.id,
        rating,
        timestamp: Date.now(),
      });
    } catch (err) {
      console.error('Failed to save pronunciation check:', err);
    }
  }

  return (
    <div className={`exercise-renderer ${exercise.exercise_type}`}>
      {/* Exercise type badge */}
      <div className="exercise-type-badge">
        {exercise.exercise_type.charAt(0).toUpperCase() + exercise.exercise_type.slice(1)}
      </div>

      {/* Instruction (hidden at level 3 — minimal immersion) */}
      {exercise.instruction && !hideEnglishHints && (
        <p className="exercise-instruction">{exercise.instruction}</p>
      )}

      {/* Question */}
      <div className="exercise-question">
        <p>{exercise.question}</p>
      </div>

      {/* Korean text display (for vocabulary exercises, NOT listening) */}
      {exercise.korean_text && exercise.exercise_type !== 'listening' && (
        <>
          <div className="korean-display">
            <div className="korean-text">{exercise.korean_text}</div>
            {exercise.romanization && !hideRomanization && (
              <div className="romanization">{exercise.romanization}</div>
            )}
          </div>
          {exercise.audio_url && (
            <div className="vocab-audio-controls">
              <button className="audio-button" onClick={() => playAudio()} title="Play audio">
                🔊
              </button>
              <div className="speed-toggle listening-speed">
                <button
                  className={`speed-button ${playbackSpeed === 0.5 ? 'active' : ''}`}
                  onClick={() => setPlaybackSpeed(0.5)}
                >
                  0.5x
                </button>
                <button
                  className={`speed-button ${playbackSpeed === 1.0 ? 'active' : ''}`}
                  onClick={() => setPlaybackSpeed(1.0)}
                >
                  1x
                </button>
                <button
                  className={`speed-button ${playbackSpeed === 1.2 ? 'active' : ''}`}
                  onClick={() => setPlaybackSpeed(1.2)}
                >
                  1.2x
                </button>
              </div>
            </div>
          )}
        </>
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
          <button className="play-audio-btn" onClick={() => playAudio()}>
            🔊 Play Audio
          </button>
          <div className="speed-toggle listening-speed">
            <button
              className={`speed-button ${playbackSpeed === 0.5 ? 'active' : ''}`}
              onClick={() => setPlaybackSpeed(0.5)}
            >
              0.5x
            </button>
            <button
              className={`speed-button ${playbackSpeed === 1.0 ? 'active' : ''}`}
              onClick={() => setPlaybackSpeed(1.0)}
            >
              1x
            </button>
            <button
              className={`speed-button ${playbackSpeed === 1.2 ? 'active' : ''}`}
              onClick={() => setPlaybackSpeed(1.2)}
            >
              1.2x
            </button>
          </div>
        </div>
      )}

      {/* Pronunciation self-check */}
      {showSelfCheck && (
        <div className="pronunciation-self-check">
          {selfCheckDone ? (
            <p className="self-check-confirmation">
              Pronunciation marked: <strong>{selfCheckRating}</strong>
            </p>
          ) : (
            <>
              <p className="self-check-prompt">How did your pronunciation sound?</p>
              <div className="self-check-buttons">
                <button className="self-check-btn good" onClick={() => handleSelfCheck('good')}>
                  Good
                </button>
                <button className="self-check-btn okay" onClick={() => handleSelfCheck('okay')}>
                  Okay
                </button>
                <button className="self-check-btn again" onClick={() => handleSelfCheck('again')}>
                  Again
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Answer section */}
      <div className="answer-section">
        {exercise.exercise_type === 'writing' ? (
          <div className="writing-answer">
            <textarea
              value={writingAnswer}
              onChange={(e) => setWritingAnswer(e.target.value)}
              placeholder="Write your answer in Korean..."
              disabled={isAnswered || submitting}
              rows={4}
              autoFocus
            />
          </div>
        ) : hasOptions ? (
          <>
            {attemptFirstRequired && !canShowOptions && (
              <div className="attempt-first-gate">
                <p className="attempt-first-title">Attempt first, then use options.</p>
                <input
                  type="text"
                  value={attemptText}
                  onChange={(e) => setAttemptText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your Korean recall..."
                  disabled={isAnswered || submitting}
                />
                <div className="attempt-first-actions">
                  <button
                    className="attempt-first-btn primary"
                    onClick={unlockOptionsFromAttempt}
                    disabled={!attemptText.trim() || isAnswered || submitting}
                  >
                    Check Attempt
                  </button>
                  <button
                    className="attempt-first-btn secondary"
                    onClick={unlockOptionsWithHint}
                    disabled={isAnswered || submitting}
                  >
                    Need a Hint
                  </button>
                </div>
              </div>
            )}

            {canShowOptions && (
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
            )}
          </>
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
          disabled={
            submitting ||
            (exercise.exercise_type === 'writing'
              ? !writingAnswer.trim()
              : hasOptions
              ? !selectedOption || !canShowOptions
              : !textAnswer.trim())
          }
        >
          {submitting ? 'Checking...' : 'Check Answer'}
        </button>
      )}
    </div>
  );
}
