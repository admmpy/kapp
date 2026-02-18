/**
 * ListeningPractice - AI-generated listening comprehension practice
 */
import { useState } from 'react';
import { apiClient, API_BASE_URL } from '@kapp/core';
import type { ListeningPracticeResponse } from '@kapp/core';
import './ListeningPractice.css';

type PlaybackSpeed = 0.5 | 1.0 | 1.2;

interface Props {
  onBack: () => void;
}

const LEVELS = [
  { value: 1, label: 'Beginner (TOPIK I-1)' },
  { value: 2, label: 'Elementary (TOPIK I-2)' },
  { value: 3, label: 'Intermediate (TOPIK II-3)' },
  { value: 4, label: 'Upper-Intermediate (TOPIK II-4)' },
  { value: 5, label: 'Advanced (TOPIK II-5-6)' },
];

export default function ListeningPractice({ onBack }: Props) {
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exercise, setExercise] = useState<ListeningPracticeResponse | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1.0);
  const [hasPlayed, setHasPlayed] = useState(false);

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
    setHasPlayed(false);

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

  function handleSubmit() {
    if (!selectedAnswer || isAnswered) return;
    setIsAnswered(true);
  }

  function handleNext() {
    setExercise(null);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setHasPlayed(false);
  }

  function getOptionClass(option: string): string {
    let classes = 'option-button';

    if (selectedAnswer === option) {
      classes += ' selected';
    }

    if (isAnswered && exercise) {
      if (option === exercise.correct_answer) {
        classes += ' correct';
      } else if (selectedAnswer === option) {
        classes += ' incorrect';
      }
    }

    return classes;
  }

  return (
    <div className="listening-practice">
      <header className="practice-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h1>Listening Practice</h1>
        <p className="subtitle">AI-generated comprehension exercises</p>
      </header>

      <div className="practice-content">
        {!exercise ? (
          <div className="practice-setup">
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
        ) : (
          <div className="exercise-container">
            <div className="exercise-meta">
              <span className="topic-badge">{exercise.topic}</span>
              <span className="level-badge">Level {exercise.level}</span>
            </div>

            <div className="audio-section">
              <button
                className={`play-audio-btn ${!hasPlayed ? 'pulse' : ''}`}
                onClick={playAudio}
              >
                🔊 Play Audio
              </button>
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

            {isAnswered && (
              <div className={`result-feedback ${selectedAnswer === exercise.correct_answer ? 'correct' : 'incorrect'}`}>
                <div className="result-icon">
                  {selectedAnswer === exercise.correct_answer ? '✓' : '✗'}
                </div>
                <div className="result-message">
                  {selectedAnswer === exercise.correct_answer ? 'Correct!' : 'Not quite...'}
                </div>
                {selectedAnswer !== exercise.correct_answer && (
                  <div className="correct-answer">
                    Correct answer: <strong>{exercise.correct_answer}</strong>
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
                  disabled={!selectedAnswer}
                >
                  Check Answer
                </button>
              ) : (
                <button className="next-button" onClick={handleNext}>
                  Next Practice
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}