/**
 * LessonView - Main lesson interface with exercises
 */
import { useState, useEffect } from 'react';
import { apiClient, cacheLesson, getCachedLesson, saveProgress, SPEAKING_FIRST_ENABLED, GRAMMAR_MASTERY_ENABLED } from '@kapp/core';
import type { Lesson, Exercise, ExerciseResult } from '@kapp/core';
import ExerciseRenderer from './ExerciseRenderer';
import ProgressBar from './ProgressBar';
import Breadcrumb from './Breadcrumb';
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

interface Props {
  lessonId: number;
  courseId?: number | null;
  onComplete: () => void;
  onBack: () => void;
  onBackToCourse?: (courseId: number) => void;
  onBackToCourses?: () => void;
  onNavigateToLesson?: (lessonId: number) => void;
}

function sortExercisesForSpeakingFirst(exercises: Exercise[]): Exercise[] {
  const audioFirst = exercises.filter(
    ex => ex.exercise_type === 'listening'
      || ((ex.exercise_type === 'vocabulary' || ex.exercise_type === 'sentence_arrange') && ex.audio_url)
  );
  const rest = exercises.filter(ex => !audioFirst.includes(ex));
  return [...audioFirst, ...rest];
}

export default function LessonView({ lessonId, courseId, onComplete, onBack, onBackToCourse, onBackToCourses, onNavigateToLesson }: Props) {
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

  // Clear result when exercise changes to prevent state pollution
  useEffect(() => {
    setLastResult(null);
  }, [currentExerciseIndex]);

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
    }
  }

  async function handleNextExercise() {
    if (!lesson?.exercises) return;

    // Note: setLastResult(null) is handled by useEffect when currentExerciseIndex changes
    // This prevents race conditions with async state updates

    if (currentExerciseIndex < lesson.exercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
    } else {
      // Lesson complete - show completion modal
      const timeSpent = Math.round((Date.now() - startTime) / 1000);
      // Use correctAnswers + 1 if current answer is correct (since state hasn't updated yet)
      const finalCorrect = lastResult?.correct ? correctAnswers : correctAnswers;
      const finalTotal = totalAnswered;
      const score = finalTotal > 0 ? (finalCorrect / finalTotal) * 100 : 0;

      try {
        // Save progress offline (will sync when online)
        await saveProgress(lessonId.toString(), true, score);

        if (navigator.onLine) {
          await apiClient.completeLesson(lessonId, {
            score,
            time_spent_seconds: timeSpent
          });

          // Fetch next lesson info
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

  const exercises = SPEAKING_FIRST_ENABLED
    ? sortExercisesForSpeakingFirst(lesson.exercises || [])
    : (lesson.exercises || []);
  const currentExercise = exercises[currentExerciseIndex];
  const isLastExercise = currentExerciseIndex === exercises.length - 1;

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

      <div className="exercise-container">
        <ExerciseRenderer
          key={currentExercise.id}
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
      </div>

      {showCompleteModal && (
        <LessonCompleteModal
          lessonTitle={lesson.title}
          score={finalScore}
          correctAnswers={correctAnswers}
          totalAnswers={totalAnswered}
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
