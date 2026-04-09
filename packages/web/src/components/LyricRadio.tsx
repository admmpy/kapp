/**
 * LyricRadio — F-09 Passive listening mode from lyric lessons
 * Auto-advances TTS clips; optional comprehension questions every 3 clips
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient, API_BASE_URL } from '@kapp/core';
import type { Exercise } from '@kapp/core';
import './LyricRadio.css';

interface RadioTrack {
  exercise: Exercise;
  lessonTitle: string;
}

interface SessionStats {
  clipsPlayed: number;
  questionsAnswered: number;
  questionsCorrect: number;
  startedAt: number;
}

interface Props {
  onBack: () => void;
}

const QUESTION_EVERY_N = 3; // show a comprehension card every N clips

export default function LyricRadio({ onBack }: Props) {
  const [tracks, setTracks] = useState<RadioTrack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);

  // Playback state
  const [trackIdx, setTrackIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<0.75 | 1.0>(1.0);

  // Question card state
  const [showQuestion, setShowQuestion] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [questionAnswered, setQuestionAnswered] = useState(false);

  const [stats, setStats] = useState<SessionStats>({
    clipsPlayed: 0, questionsAnswered: 0, questionsCorrect: 0, startedAt: Date.now(),
  });

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Load lyric lesson tracks on mount
  useEffect(() => {
    async function loadTracks() {
      try {
        const courses = await apiClient.getCourses();
        if (!courses.length) { setError('No courses found'); setLoading(false); return; }

        const course = await apiClient.getCourse(courses[0].id);
        const lyricUnit = course.units.find(u => u.title.toLowerCase().includes('lyric'));
        if (!lyricUnit) { setError('No Lyric Lessons unit found. Complete some lessons first!'); setLoading(false); return; }

        const { lessons } = await apiClient.getUnitLessons(lyricUnit.id);
        const collected: RadioTrack[] = [];

        for (const summary of lessons) {
          const lesson = await apiClient.getLesson(summary.id);
          if (!lesson.exercises) continue;
          for (const ex of lesson.exercises) {
            if (ex.audio_url && ex.korean_text) {
              collected.push({ exercise: ex, lessonTitle: lesson.title });
            }
          }
        }

        if (!collected.length) {
          setError('No audio clips found in lyric lessons yet.');
          setLoading(false);
          return;
        }

        setTracks(collected);
        setLoading(false);
      } catch (err) {
        setError('Failed to load lyric lessons. Is the app online?');
        setLoading(false);
      }
    }
    loadTracks();
  }, []);

  const currentTrack = tracks[trackIdx] ?? null;

  const advanceTrack = useCallback(() => {
    setStats(s => ({ ...s, clipsPlayed: s.clipsPlayed + 1 }));
    const next = (trackIdx + 1) % tracks.length;

    // Show question every N clips if the exercise has options
    const nextTrack = tracks[next];
    const hasOptions = Array.isArray(nextTrack?.exercise.options) && (nextTrack.exercise.options as string[]).length > 1;
    const shouldAsk = (Math.floor((trackIdx + 1) / QUESTION_EVERY_N)) > Math.floor(trackIdx / QUESTION_EVERY_N);

    if (shouldAsk && hasOptions) {
      setShowQuestion(true);
      setSelectedAnswer(null);
      setQuestionAnswered(false);
    }

    setTrackIdx(next);
    setIsPlaying(false);
  }, [trackIdx, tracks]);

  function playCurrentTrack() {
    if (!currentTrack?.exercise.audio_url) return;
    stopAudio();
    const audio = new Audio(`${API_BASE_URL}${currentTrack.exercise.audio_url}`);
    audio.playbackRate = speed;
    audioRef.current = audio;
    audio.addEventListener('ended', advanceTrack, { once: true });
    audio.play().catch(() => {});
    setIsPlaying(true);
  }

  function stopAudio() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlaying(false);
  }

  function handleSpeedToggle() {
    setSpeed(s => s === 1.0 ? 0.75 : 1.0);
  }

  function handleAnswerQuestion(option: string) {
    if (questionAnswered) return;
    setSelectedAnswer(option);
    setQuestionAnswered(true);
    const correct = option === currentTrack?.exercise.correct_answer;
    setStats(s => ({
      ...s,
      questionsAnswered: s.questionsAnswered + 1,
      questionsCorrect: s.questionsCorrect + (correct ? 1 : 0),
    }));
  }

  function handleDismissQuestion() {
    setShowQuestion(false);
    setSelectedAnswer(null);
    setQuestionAnswered(false);
  }

  const elapsedMin = Math.round((Date.now() - stats.startedAt) / 60000);

  if (loading) {
    return (
      <div className="lyric-radio">
        <header className="radio-header">
          <button className="back-button" onClick={onBack}>← Back</button>
          <h1>🎵 Lyric Radio</h1>
        </header>
        <div className="radio-loading">Loading lyric tracks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lyric-radio">
        <header className="radio-header">
          <button className="back-button" onClick={onBack}>← Back</button>
          <h1>🎵 Lyric Radio</h1>
        </header>
        <div className="radio-error"><p>⚠️ {error}</p></div>
      </div>
    );
  }

  return (
    <div className="lyric-radio">
      <header className="radio-header">
        <button className="back-button" onClick={onBack}>← Back</button>
        <h1>🎵 Lyric Radio</h1>
        <p className="subtitle">Passive listening — R&B lyric clips</p>
      </header>

      {!started ? (
        <div className="radio-intro">
          <div className="radio-intro-card">
            <div className="radio-icon">🎵</div>
            <h2>Ready to listen?</h2>
            <p>{tracks.length} clips from your lyric lessons</p>
            <p className="radio-tip">Sit back and let the Korean wash over you. A comprehension card appears every few clips — answer or skip freely.</p>
          </div>
          <div className="radio-speed-choice">
            <p>Starting speed:</p>
            <div className="speed-toggle">
              <button
                className={`speed-button${speed === 0.75 ? ' active' : ''}`}
                onClick={() => setSpeed(0.75)}
              >0.75x</button>
              <button
                className={`speed-button${speed === 1.0 ? ' active' : ''}`}
                onClick={() => setSpeed(1.0)}
              >1x</button>
            </div>
          </div>
          <button className="radio-start-btn" onClick={() => setStarted(true)}>
            Start Listening
          </button>
        </div>
      ) : (
        <div className="radio-player">
          {/* Session stats bar */}
          <div className="radio-stats">
            <span>🎵 {stats.clipsPlayed} clips</span>
            {stats.questionsAnswered > 0 && (
              <span>✓ {stats.questionsCorrect}/{stats.questionsAnswered} questions</span>
            )}
            <span>⏱ {elapsedMin}m</span>
          </div>

          {/* Now playing card */}
          {currentTrack && (
            <div className="radio-now-playing">
              <p className="radio-lesson-label">{currentTrack.lessonTitle}</p>
              <div className="radio-korean">{currentTrack.exercise.korean_text}</div>
              {currentTrack.exercise.romanization && (
                <div className="radio-romanization">{currentTrack.exercise.romanization}</div>
              )}
              {currentTrack.exercise.english_text && (
                <div className="radio-english">{currentTrack.exercise.english_text}</div>
              )}
            </div>
          )}

          {/* Controls */}
          <div className="radio-controls">
            {isPlaying ? (
              <button className="radio-btn stop" onClick={stopAudio}>⏸ Pause</button>
            ) : (
              <button className="radio-btn play" onClick={playCurrentTrack}>▶ Play</button>
            )}
            <button className="radio-btn skip" onClick={advanceTrack}>⏭ Next</button>
            <button
              className={`speed-button${speed === 0.75 ? ' active' : ''}`}
              onClick={handleSpeedToggle}
            >
              {speed}x
            </button>
          </div>

          <div className="radio-progress">
            <span>{trackIdx + 1} / {tracks.length}</span>
          </div>

          {/* Comprehension question card */}
          {showQuestion && currentTrack && Array.isArray(currentTrack.exercise.options) && (currentTrack.exercise.options as string[]).length > 1 && (
            <div className="radio-question-card">
              <p className="radio-q-label">Quick check</p>
              <p className="radio-q-text">{currentTrack.exercise.question}</p>
              <div className="radio-q-options">
                {(currentTrack.exercise.options as string[]).map((opt, i) => {
                  let cls = 'option-button';
                  if (questionAnswered) {
                    if (opt === currentTrack.exercise.correct_answer) cls += ' correct';
                    else if (opt === selectedAnswer) cls += ' incorrect';
                  } else if (opt === selectedAnswer) cls += ' selected';
                  return (
                    <button key={i} className={cls} onClick={() => handleAnswerQuestion(opt)} disabled={questionAnswered}>
                      {opt}
                    </button>
                  );
                })}
              </div>
              <button className="radio-skip-question" onClick={handleDismissQuestion}>
                {questionAnswered ? 'Continue →' : 'Skip question'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
