/**
 * CourseList - Displays available courses
 */
import { useState, useEffect } from 'react';
import { apiClient, IMMERSION_MODE_ENABLED } from '@kapp/core';
import type { Course, OverallProgress, ImmersionLevel } from '@kapp/core';
import { CourseCardSkeleton, Skeleton } from './Skeleton';
import './CourseList.css';

interface Props {
  onSelectCourse: (courseId: number) => void;
  onStartConversation?: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  immersionLevel?: ImmersionLevel;
  onImmersionChange?: (level: ImmersionLevel) => void;
}

const IMMERSION_LABELS: Record<ImmersionLevel, string> = {
  1: 'Full',
  2: 'Reduced',
  3: 'Minimal',
};

export default function CourseList({
  onSelectCourse,
  onStartConversation,
  theme,
  onToggleTheme,
  immersionLevel = 1,
  onImmersionChange,
}: Props) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [progress, setProgress] = useState<OverallProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [coursesData, progressData] = await Promise.all([
          apiClient.getCourses(),
          apiClient.getProgress()
        ]);
        setCourses(coursesData);
        setProgress(progressData);
      } catch (err) {
        console.error('Failed to load courses:', err);
        setError('Failed to load courses. Please try again.');
        setCourses([]);
        setProgress(null);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="course-list">
        <header className="course-list-header">
          <div className="header-top">
            <Skeleton variant="text" width={200} height={32} />
          </div>
          <div className="skeleton-stats">
            <div className="skeleton-stat">
              <Skeleton variant="rect" width={40} height={24} />
              <Skeleton variant="text" width={60} height={12} />
            </div>
            <div className="skeleton-stat">
              <Skeleton variant="rect" width={40} height={24} />
              <Skeleton variant="text" width={60} height={12} />
            </div>
            <div className="skeleton-stat">
              <Skeleton variant="rect" width={40} height={24} />
              <Skeleton variant="text" width={60} height={12} />
            </div>
          </div>
        </header>
        <div className="courses-grid">
          <CourseCardSkeleton />
          <CourseCardSkeleton />
          <CourseCardSkeleton />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="course-list error">
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  const getCourseProgress = (courseId: number) => {
    return progress?.courses.find(c => c.id === courseId);
  };

  return (
    <div className="course-list">
      <header className="course-list-header">
        <div className="header-top">
          <h1>Korean Learning</h1>
          <div className="header-actions">
            {onStartConversation && (
              <button className="practice-speaking-btn" onClick={onStartConversation}>
                Practice Speaking
              </button>
            )}
            <div className="theme-toggle">
              <span className="theme-label">{theme === 'dark' ? 'Dark' : 'Light'}</span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={theme === 'dark'}
                  onChange={onToggleTheme}
                  aria-label="Toggle dark mode"
                />
                <span className="slider" />
              </label>
            </div>
            {IMMERSION_MODE_ENABLED && onImmersionChange && (
              <div className="immersion-toggle">
                <span className="immersion-label">Immersion</span>
                <div className="immersion-buttons">
                  {([1, 2, 3] as ImmersionLevel[]).map(level => (
                    <button
                      key={level}
                      className={`immersion-btn ${immersionLevel === level ? 'active' : ''}`}
                      onClick={() => onImmersionChange(level)}
                      title={level === 1 ? 'Korean + romanization + English' : level === 2 ? 'Korean + English (no romanization)' : 'Korean only (English in feedback)'}
                    >
                      {IMMERSION_LABELS[level]}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        {progress && (
          <div className="overall-stats">
            <div className="stat">
              <span className="stat-value">{progress.completed_lessons}</span>
              <span className="stat-label">Lessons Done</span>
            </div>
            <div className="stat">
              <span className="stat-value">{progress.current_streak}</span>
              <span className="stat-label">Day Streak</span>
            </div>
            {progress.average_score && (
              <div className="stat">
                <span className="stat-value">{Math.round(progress.average_score)}%</span>
                <span className="stat-label">Avg Score</span>
              </div>
            )}
          </div>
        )}
      </header>

      <div className="courses-grid">
        {courses.map(course => {
          const courseProgress = getCourseProgress(course.id);
          return (
            <div
              key={course.id}
              className="course-card"
              onClick={() => onSelectCourse(course.id)}
            >
              {course.image_url && (
                <div className="course-image">
                  <img src={course.image_url} alt={course.title} />
                </div>
              )}
              <div className="course-info">
                <h2>{course.title}</h2>
                <p className="course-description">{course.description}</p>
                <div className="course-meta">
                  <span className="course-level">{course.level}</span>
                  <span className="course-lessons">{course.total_lessons} lessons</span>
                </div>
                {courseProgress && (
                  <div className="course-progress">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${courseProgress.percentage}%` }}
                      />
                    </div>
                    <span className="progress-text">
                      {courseProgress.completed_lessons}/{courseProgress.total_lessons}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {courses.length === 0 && (
        <div className="no-courses">
          <p>No courses available yet.</p>
          <p>Run the import script to add lesson content.</p>
        </div>
      )}
    </div>
  );
}
