/**
 * LessonView - Main lesson interface with exercises
 */
import { useState, useEffect, useMemo, useRef } from 'react';
import { apiClient, cacheLesson, getCachedLesson, saveProgress, SPEAKING_FIRST_ENABLED, GRAMMAR_MASTERY_ENABLED, IMMERSION_MODE_ENABLED } from '@kapp/core';
import type { Lesson, Exercise, ExerciseResult, ImmersionLevel } from '@kapp/core';
import ExerciseRenderer from './ExerciseRenderer';
import ProgressBar from './ProgressBar';
import Breadcrumb from './Breadcrumb';
import ImmersionSelector from './ImmersionSelector';
import LessonCompleteModal from './LessonCompleteModal';
import ExerciseExplanationModal from './ExerciseExplanationModal';
import { Skeleton, ExerciseSkeleton } from './Skeleton';
import './LessonView.css';

interface NextLessonInfo {
  id: number;
  title: string;
  estimated_minutes: number;
  exercise_count: number;
}

interface ExerciseHistoryEntry {
  result: ExerciseResult | null;
  answer: string | null;
}

interface Props {
  lessonId: number;
  courseId?: number | null;
  onComplete: () => void;
  onBack: () => void;
  onBackToCourse?: (courseId: number) => void;
  onBackToCourses?: () => void;
  onNavigateToLesson?: (lessonId: number) => void;
  immersionLevel?: ImmersionLevel;
  onImmersionChange?: (level: ImmersionLevel) => void;
}

function sortExercisesForSpeakingFirst(exercises: Exercise[]): Exercise[] {
  const audioFirst = exercises.filter(
    ex => ex.exercise_type === 'listening'
      || ((ex.exercise_type === 'vocabulary' || ex.exercise_type === 'sentence_arrange') && ex.audio_url)
  );
  const rest = exercises.filter(ex => !audioFirst.includes(ex));
  const sorted = [...audioFirst, ...rest];
  const firstThirdEnd = Math.max(1, Math.ceil(sorted.length / 3));
  const hasEarlyProduction = sorted
    .slice(0, firstThirdEnd)
    .some(ex => ex.exercise_type === 'writing' || ex.exercise_type === 'sentence_arrange');

  if (!hasEarlyProduction) {
    const productionIndex = sorted.findIndex(
      ex => ex.exercise_type === 'writing' || ex.exercise_type === 'sentence_arrange'
    );
    if (productionIndex > -1) {
      const [productionExercise] = sorted.splice(productionIndex, 1);
      sorted.splice(firstThirdEnd - 1, 0, productionExercise);
    }
  }

  return sorted;
}

export default function LessonView({ lessonId, courseId, onComplete, onBack, onBackToCourse, onBackToCourses, onNavigateToLesson, immersionLevel = 1, onImmersionChange }: Props) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [showGrammar, setShowGrammar] = useState(true);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [totalAnswered, setTotalAnswered] = useState(0);
  const [lastResult, setLastResult] = useState<ExerciseResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());
  const [courseName, setCourseName] = useState<string | undefined>();
  const [unitName, setUnitName] = useState<string | undefined>();
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [nextLessonInfo, setNextLessonInfo] = useState<NextLessonInfo | null>(null);
  const [isLastInUnit, setIsLastInUnit] = useState(false);
  const [isLastInCourse, setIsLastInCourse] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [showExplanationModal, setShowExplanationModal] = useState(false);
  const [patternMasteryResults, setPatternMasteryResults] = useState<
    Array<{ pattern_title: string; mastery_score: number; attempts: number }>
  >([]);

  // Skip / Back navigation
  const [skippedCount, setSkippedCount] = useState(0);
  const [navDirection, setNavDirection] = useState<'forward' | 'backward'>('forward');
  const exerciseHistoryRef = useRef<Map<number, ExerciseHistoryEntry>>(new Map());
  // Pending answer for storing before API result arrives
  const pendingAnswerRef = useRef<string | null>(null);

  const exercises = useMemo(() => {
    if (!lesson?.exercises) return [];
    return SPEAKING_FIRST_ENABLED
      ? sortExercisesForSpeakingFirst(lesson.exercises)
      : lesson.exercises;
  }, [lesson]);

  useEffect(() => {
    async function loadLesson() {
      try {
        // Try to load from cache first
        const cached = await getCachedLesson(lessonId.toString());
        if (cached && typeof cached === 'object' && 'id' in cached) {
          setLesson(cached as Lesson);
        }

        if (!navigator.onLine) {
          setLoading(false);
          return;
        }

        // Fetch from network and cache
        const data = await apiClient.getLesson(lessonId);
        setLesson(data);

        // Cache the lesson for offline use
        await cacheLesson(lessonId.toString(), data);

        await apiClient.startLesson(lessonId);

        // Load breadcrumb data if we have courseId
        if (courseId) {
          try {
            const course = await apiClient.getCourse(courseId);
            setCourseName(course.title);

            // Get unit name from loaded lesson
            const unit = await apiClient.getUnit(data.unit_id);
            setUnitName(unit.title);
          } catch (err) {
            console.error('Failed to load breadcrumb data:', err);
          }
        }
      } catch (err) {
        console.error('Failed to load lesson:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLesson();
  }, [lessonId, courseId]);

  // Restore or clear result when exercise index changes
  useEffect(() => {
    const history = exerciseHistoryRef.current.get(currentExerciseIndex);
    setLastResult(history?.result ?? null);
  }, [currentExerciseIndex]);

  async function handleSubmitAnswer(answer: string, meta?: { peeked?: boolean }) {
    if (!exercises.length || submitting) return;

    const exercise = exercises[currentExerciseIndex];
    pendingAnswerRef.current = answer;
    setSubmitting(true);

    try {
      const result = await apiClient.submitExercise(exercise.id, { answer, peeked: meta?.peeked });
      setLastResult(result);

      // Store in history
      exerciseHistoryRef.current.set(currentExerciseIndex, { result, answer });

      setTotalAnswered(prev => prev + 1);
      if (result.correct) {
        setCorrectAnswers(prev => prev + 1);
      }
      if (GRAMMAR_MASTERY_ENABLED && result.pattern_mastery) {
        setPatternMasteryResults(prev => {
          const existing = prev.findIndex(
            p => p.pattern_title === result.pattern_mastery!.pattern_title
          );
          if (existing >= 0) {
            const updated = [...prev];
            updated[existing] = result.pattern_mastery!;
            return updated;
          }
          return [...prev, result.pattern_mastery!];
        });
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
    } finally {
      setSubmitting(false);
      pendingAnswerRef.current = null;
    }
  }

  async function handleNextExercise() {
    if (!exercises.length) return;

    setNavDirection('forward');

    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
    } else {
      await completLesson();
    }
  }

  function handleSkipExercise() {
    if (!exercises.length || lastResult) return; // don't skip after answering

    // Record as skipped (no result, no answer)
    exerciseHistoryRef.current.set(currentExerciseIndex, { result: null, answer: null });
    setSkippedCount(prev => prev + 1);
    setNavDirection('forward');

    if (currentExerciseIndex < exercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
    } else {
      completLesson();
    }
  }

  function handlePreviousExercise() {
    if (currentExerciseIndex === 0) return;
    setNavDirection('backward');
    setCurrentExerciseIndex(prev => prev - 1);
  }

  async function completLesson() {
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
    const score = totalAnswered > 0 ? (correctAnswers / totalAnswered) * 100 : 0;

    try {
      await saveProgress(lessonId.toString(), true, score);

      if (navigator.onLine) {
        await apiClient.completeLesson(lessonId, {
          score,
          time_spent_seconds: timeSpent
        });

        const nextLessonData = await apiClient.getNextLesson(lessonId);
        if (nextLessonData.next_lesson) {
          setNextLessonInfo({
            id: nextLessonData.next_lesson.id,
            title: nextLessonData.next_lesson.title,
            estimated_minutes: nextLessonData.next_lesson.estimated_minutes,
            exercise_count: nextLessonData.next_lesson.exercise_count
          });
        }
        setIsLastInUnit(nextLessonData.is_last_in_unit);
        setIsLastInCourse(nextLessonData.is_last_in_course);
      } else {
        setNextLessonInfo(null);
        setIsLastInUnit(false);
        setIsLastInCourse(false);
      }
    } catch (err) {
      console.error('Failed to complete lesson:', err);
    }

    setFinalScore(score);
    setShowCompleteModal(true);
  }

  function handleNextLesson(nextLessonId: number) {
    setShowCompleteModal(false);
    if (onNavigateToLesson) {
      onNavigateToLesson(nextLessonId);
    }
  }

  function handleBackToCourse() {
    setShowCompleteModal(false);
    onComplete();
  }

  function handleStartExercises() {
    setShowGrammar(false);
  }

  if (loading) {
    return (
      <div className="lesson-view">
        <header className="lesson-header">
          <Skeleton variant="text" width={60} height={20} />
          <Skeleton variant="text" width="70%" height={28} />
          <Skeleton variant="rect" height={8} />
        </header>
        <div className="exercise-container">
          <ExerciseSkeleton />
        </div>
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

  const currentExercise = exercises[currentExerciseIndex];
  const isLastExercise = currentExerciseIndex === exercises.length - 1;
  const isFirstExercise = currentExerciseIndex === 0;
  const currentHistory = exerciseHistoryRef.current.get(currentExerciseIndex);
  const previousAnswer = currentHistory?.answer ?? null;

  // Show grammar explanation first
  if (showGrammar && lesson.grammar_explanation) {
    return (
      <div className="lesson-view">
        <Breadcrumb
          courseId={courseId}
          unitId={lesson.unit_id}
          courseName={courseName}
          unitName={unitName}
          onNavigateToCourse={onBackToCourse}
          onNavigateToCourses={onBackToCourses}
        />

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
          {IMMERSION_MODE_ENABLED && onImmersionChange && (
            <ImmersionSelector level={immersionLevel} onChange={onImmersionChange} />
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
        <Breadcrumb
          courseId={courseId}
          unitId={lesson.unit_id}
          courseName={courseName}
          unitName={unitName}
          onNavigateToCourse={onBackToCourse}
          onNavigateToCourses={onBackToCourses}
        />

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

      {/* Navigation toolbar */}
      <div className="exercise-nav-toolbar">
        <button
          className="nav-back-btn"
          onClick={handlePreviousExercise}
          disabled={isFirstExercise}
          aria-label="Previous exercise"
        >
          ← Back
        </button>
        <span className="nav-counter">
          {currentExerciseIndex + 1} / {exercises.length}
        </span>
        {!lastResult && (
          <button
            className="nav-skip-btn"
            onClick={handleSkipExercise}
            aria-label="Skip exercise"
          >
            Skip →
          </button>
        )}
        {lastResult && <span className="nav-skip-placeholder" />}
      </div>

      <div className={`exercise-container exercise-slide-${navDirection}`}>
        <ExerciseRenderer
          key={currentExercise.id}
          exercise={currentExercise}
          onSubmit={handleSubmitAnswer}
          result={lastResult}
          submitting={submitting}
          immersionLevel={immersionLevel}
          forceAttemptFirst
          previousAnswer={previousAnswer}
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
            {GRAMMAR_MASTERY_ENABLED && lastResult.pattern_mastery && (
              <div className={`mastery-pill ${
                lastResult.pattern_mastery.mastery_score >= 80 ? 'mastery-high' :
                lastResult.pattern_mastery.mastery_score >= 50 ? 'mastery-mid' : 'mastery-low'
              }`}>
                {lastResult.pattern_mastery.pattern_title} — {Math.round(lastResult.pattern_mastery.mastery_score)}%
              </div>
            )}
            <div className="result-actions">
              {!lastResult.correct && (
                <button
                  className="explain-button"
                  onClick={() => setShowExplanationModal(true)}
                >
                  Explain
                </button>
              )}
              <button className="next-button" onClick={handleNextExercise}>
                {isLastExercise ? 'Complete Lesson' : 'Next Exercise'}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="lesson-progress-summary">
        <span>{correctAnswers} correct</span>
        <span>{totalAnswered - correctAnswers} incorrect</span>
        {skippedCount > 0 && <span>{skippedCount} skipped</span>}
      </div>

      {showCompleteModal && (
        <LessonCompleteModal
          lessonTitle={lesson.title}
          score={finalScore}
          correctAnswers={correctAnswers}
          totalAnswers={totalAnswered}
          skippedCount={skippedCount}
          nextLesson={nextLessonInfo || undefined}
          isLastInUnit={isLastInUnit}
          isLastInCourse={isLastInCourse}
          onNextLesson={handleNextLesson}
          onBackToCourse={handleBackToCourse}
          patternMasteryResults={GRAMMAR_MASTERY_ENABLED ? patternMasteryResults : undefined}
        />
      )}

      {showExplanationModal && lastResult && currentExercise && (
        <ExerciseExplanationModal
          exercise={currentExercise}
          correctAnswer={lastResult.correct_answer}
          basicExplanation={lastResult.explanation}
          isOpen={showExplanationModal}
          onClose={() => setShowExplanationModal(false)}
        />
      )}
    </div>
  );
}
