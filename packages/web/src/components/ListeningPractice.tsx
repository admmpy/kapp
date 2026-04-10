/**
 * ListeningPractice - AI-generated listening comprehension practice
 * Includes Speed Ramp mode (F-06): same clips at ascending playback speeds
 */
import { useState } from 'react';
import { apiClient, API_BASE_URL } from '@kapp/core';
import type { ListeningPracticeResponse, ListeningPracticeCheckResponse } from '@kapp/core';
import './ListeningPractice.css';

type PlaybackSpeed = 0.5 | 0.7 | 0.85 | 1.0 | 1.2;
type Mode = 'standard' | 'speed-ramp';

const RAMP_SPEEDS: PlaybackSpeed[] = [0.5, 0.7, 0.85, 1.0];

interface Props {
  onBack: () => void;
  onLyricRadio?: () => void;
}

const LEVELS = [
  { value: 1, label: 'Beginner (TOPIK I-1)' },
  { value: 2, label: 'Elementary (TOPIK I-2)' },
  { value: 3, label: 'Intermediate (TOPIK II-3)' },
  { value: 4, label: 'Upper-Intermediate (TOPIK II-4)' },
  { value: 5, label: 'Advanced (TOPIK II-5-6)' },
];

export default function ListeningPractice({ onBack, onLyricRadio }: Props) {
  const [mode, setMode] = useState<Mode>('standard');
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exercise, setExercise] = useState<ListeningPracticeResponse | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [checkingAnswer, setCheckingAnswer] = useState(false);
  const [checkResult, setCheckResult] = useState<ListeningPracticeCheckResponse | null>(null);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1.0);
  const [hasPlayed, setHasPlayed] = useState(false);

  // Speed Ramp state
  const [rampStep, setRampStep] = useState(0); // index into RAMP_SPEEDS
  const [rampResults, setRampResults] = useState<boolean[]>([]);

  async function handleGenerate() {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);
    setExercise(null);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setCheckingAnswer(false);
    setCheckResult(null);
    setHasPlayed(false);
    setRampStep(0);
    setRampResults([]);

    if (mode === 'speed-ramp') {
      setPlaybackSpeed(RAMP_SPEEDS[0]);
    }

    try {
      const response = await apiClient.generateListeningPractice({
        topic: topic.trim(),
        level,
      });
      setExercise(response);
    } catch (err) {
      console.error('Failed to generate listening practice:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate practice. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function playAudio() {
    if (!exercise?.audio_url) return;
    const audio = new Audio(`${API_BASE_URL}${exercise.audio_url}`);
    audio.playbackRate = playbackSpeed;
    audio.play().catch(err => console.error('Audio playback failed:', err));
    setHasPlayed(true);
  }

  async function handleSubmit() {
    if (!selectedAnswer || isAnswered || !exercise) return;
    setCheckingAnswer(true);
    setError(null);

    try {
      const result = await apiClient.checkListeningPracticeAnswer({
        answer_key: exercise.answer_key,
        selected_answer: selectedAnswer,
      });
      setCheckResult(result);
      setIsAnswered(true);

      if (mode === 'speed-ramp') {
        setRampResults((prev) => [...prev, result.correct]);
      }
    } catch (err) {
      console.error('Failed to check listening practice answer:', err);
      setError(err instanceof Error ? err.message : 'Failed to check answer. Please try again.');
    } finally {
      setCheckingAnswer(false);
    }
  }

  function handleRampNext() {
    const nextStep = rampStep + 1;
    if (nextStep >= RAMP_SPEEDS.length) {
      // Session complete — reset to show summary then allow new session
      setIsAnswered(false);
      setSelectedAnswer(null);
      setCheckResult(null);
      setHasPlayed(false);
      setRampStep(RAMP_SPEEDS.length); // sentinel: session done
      return;
    }
    setRampStep(nextStep);
    setPlaybackSpeed(RAMP_SPEEDS[nextStep]);
    setIsAnswered(false);
    setSelectedAnswer(null);
    setCheckResult(null);
    setHasPlayed(false);
  }

  function handleNext() {
    setExercise(null);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setCheckingAnswer(false);
    setCheckResult(null);
    setHasPlayed(false);
    setRampStep(0);
    setRampResults([]);
    if (mode === 'speed-ramp') {
      setPlaybackSpeed(RAMP_SPEEDS[0]);
    }
  }

  function getOptionClass(option: string): string {
    let classes = 'option-button';

    if (selectedAnswer === option) {
      classes += ' selected';
    }

    if (isAnswered && checkResult) {
      if (option === checkResult.correct_answer) {
        classes += ' correct';
      } else if (selectedAnswer === option) {
        classes += ' incorrect';
      }
    }

    return classes;
  }

  const rampDone = mode === 'speed-ramp' && rampStep >= RAMP_SPEEDS.length;

  return (
    <div className="listening-practice">
      <header className="practice-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h1>Listening Practice</h1>
        <p className="subtitle">AI-generated comprehension exercises</p>
        {onLyricRadio && (
          <button className="lyric-radio-btn" onClick={onLyricRadio} title="Lyric Radio — passive listening">
            🎵 Lyric Radio
          </button>
        )}
      </header>

      <div className="practice-content">
        {!exercise ? (
          <div className="practice-setup">
            <div className="mode-toggle">
              <button
                className={`mode-btn${mode === 'standard' ? ' active' : ''}`}
                onClick={() => setMode('standard')}
              >
                Standard
              </button>
              <button
                className={`mode-btn${mode === 'speed-ramp' ? ' active' : ''}`}
                onClick={() => setMode('speed-ramp')}
              >
                🚀 Speed Ramp
              </button>
            </div>

            {mode === 'speed-ramp' && (
              <div className="ramp-info">
                <p>Same audio clip played at 4 increasing speeds: <strong>0.5x → 0.7x → 0.85x → 1.0x</strong></p>
                <p>Answer a comprehension question after each speed.</p>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="topic">Topic</label>
              <input
                id="topic"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., ordering coffee, asking directions, shopping..."
                disabled={loading}
                className="topic-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="level">Difficulty Level</label>
              <select
                id="level"
                value={level}
                onChange={(e) => setLevel(Number(e.target.value))}
                disabled={loading}
                className="level-select"
              >
                {LEVELS.map((l) => (
                  <option key={l.value} value={l.value}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="generate-button"
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                'Generate Practice'
              )}
            </button>

            {error && (
              <div className="error-message">
                <p>⚠️ {error}</p>
              </div>
            )}
          </div>
        ) : rampDone ? (
          <div className="ramp-summary">
            <h2>Speed Ramp Complete! 🎉</h2>
            <div className="ramp-results-grid">
              {RAMP_SPEEDS.map((speed, i) => (
                <div key={speed} className={`ramp-result-row ${rampResults[i] ? 'correct' : 'incorrect'}`}>
                  <span className="ramp-speed-label">{speed}x</span>
                  <span className="ramp-result-icon">{rampResults[i] ? '✓' : '✗'}</span>
                </div>
              ))}
            </div>
            <p className="ramp-score">
              {rampResults.filter(Boolean).length}/{RAMP_SPEEDS.length} correct
            </p>
            <button className="next-button" onClick={handleNext}>New Session</button>
          </div>
        ) : (
          <div className="exercise-container">
            <div className="exercise-meta">
              <span className="topic-badge">{exercise.topic}</span>
              <span className="level-badge">Level {exercise.level}</span>
              {mode === 'speed-ramp' && (
                <span className="ramp-badge">Speed Ramp {rampStep + 1}/{RAMP_SPEEDS.length} — {RAMP_SPEEDS[rampStep]}x</span>
              )}
            </div>

            <div className="audio-section">
              <button
                className={`play-audio-btn ${!hasPlayed ? 'pulse' : ''}`}
                onClick={playAudio}
              >
                🔊 Play Audio {mode === 'speed-ramp' ? `(${RAMP_SPEEDS[rampStep]}x)` : ''}
              </button>
              {mode !== 'speed-ramp' && (
                <div className="speed-toggle">
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
              )}
            </div>

            <div className="question-section">
              <p className="question">{exercise.question}</p>
            </div>

            <div className="options-grid">
              {exercise.options.map((option, index) => (
                <button
                  key={index}
                  className={getOptionClass(option)}
                  onClick={() => !isAnswered && setSelectedAnswer(option)}
                  disabled={isAnswered}
                >
                  {option}
                </button>
              ))}
            </div>

            {isAnswered && checkResult && (
              <div className={`result-feedback ${checkResult.correct ? 'correct' : 'incorrect'}`}>
                <div className="result-icon">
                  {checkResult.correct ? '✓' : '✗'}
                </div>
                <div className="result-message">
                  {checkResult.correct ? 'Correct!' : 'Not quite...'}
                </div>
                {!checkResult.correct && (
                  <div className="correct-answer">
                    Correct answer: <strong>{checkResult.correct_answer}</strong>
                  </div>
                )}
                {exercise.explanation && (
                  <div className="result-explanation">
                    {exercise.explanation}
                  </div>
                )}
                {exercise.korean_text && (
                  <div className="korean-text-section">
                    <p className="korean-label">Korean text:</p>
                    <p className="korean-text">{exercise.korean_text}</p>
                    {exercise.romanization && (
                      <p className="romanization">{exercise.romanization}</p>
                    )}
                    {exercise.english_translation && (
                      <p className="english-translation">{exercise.english_translation}</p>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="action-buttons">
              {!isAnswered ? (
                <button
                  className="submit-button"
                  onClick={handleSubmit}
                  disabled={!selectedAnswer || checkingAnswer}
                >
                  {checkingAnswer ? 'Checking...' : 'Check Answer'}
                </button>
              ) : mode === 'speed-ramp' ? (
                <button className="next-button" onClick={handleRampNext}>
                  {rampStep + 1 < RAMP_SPEEDS.length
                    ? `Next Speed (${RAMP_SPEEDS[rampStep + 1]}x) →`
                    : 'See Results'}
                </button>
              ) : (
                <div className="next-actions">
                  <button className="next-button" onClick={handleNext}>
                    Same Topic
                  </button>
                  <button className="try-another-button" onClick={() => { handleNext(); setTopic(''); }}>
                    Try Another Topic
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
