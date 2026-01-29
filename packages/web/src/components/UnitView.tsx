/**
 * UnitView - Displays units and lessons within a course
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import type { Course, Unit, LessonSummary } from '@kapp/core';
import Breadcrumb from './Breadcrumb';
import './UnitView.css';

interface Props {
  courseId: number;
  onSelectLesson: (lessonId: number) => void;
  onBack: () => void;
}

export default function UnitView({ courseId, onSelectLesson, onBack }: Props) {
  const [course, setCourse] = useState<(Course & { units: Unit[] }) | null>(null);
  const [expandedUnit, setExpandedUnit] = useState<number | null>(null);
  const [unitLessons, setUnitLessons] = useState<Record<number, LessonSummary[]>>({});
  const [loading, setLoading] = useState(true);
  const [loadingLessons, setLoadingLessons] = useState<number | null>(null);

  useEffect(() => {
    async function loadCourse() {
      try {
        const data = await apiClient.getCourse(courseId);
        setCourse(data);
        // Auto-expand first unit
        if (data.units.length > 0) {
          await loadUnitLessons(data.units[0].id);
          setExpandedUnit(data.units[0].id);
        }
      } catch (err) {
        console.error('Failed to load course:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCourse();
  }, [courseId]);

  async function loadUnitLessons(unitId: number) {
    if (unitLessons[unitId]) return; // Already loaded

    setLoadingLessons(unitId);
    try {
      const data = await apiClient.getUnitLessons(unitId);
      setUnitLessons(prev => ({ ...prev, [unitId]: data.lessons }));
    } catch (err) {
      console.error('Failed to load unit lessons:', err);
    } finally {
      setLoadingLessons(null);
    }
  }

  function toggleUnit(unitId: number) {
    if (expandedUnit === unitId) {
      setExpandedUnit(null);
    } else {
      setExpandedUnit(unitId);
      loadUnitLessons(unitId);
    }
  }

  function getLessonStatus(lesson: LessonSummary): 'completed' | 'in-progress' | 'locked' | 'available' {
    if (lesson.is_locked) return 'locked';
    if (lesson.is_completed) return 'completed';
    if (lesson.is_started) return 'in-progress';
    return 'available';
  }

  if (loading) {
    return (
      <div className="unit-view loading">
        <div className="loading-spinner"></div>
        <p>Loading course...</p>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="unit-view error">
        <p>Course not found</p>
        <button onClick={onBack}>Back to Courses</button>
      </div>
    );
  }

  return (
    <div className="unit-view">
      <Breadcrumb
        courseId={courseId}
        courseName={course.title}
        onNavigateToCourse={onBack}
        onNavigateToCourses={onBack}
      />

      <header className="unit-view-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <div className="course-title">
          <h1>{course.title}</h1>
          <p>{course.description}</p>
        </div>
      </header>

      <div className="units-container">
        {course.units.map((unit, index) => {
          const isExpanded = expandedUnit === unit.id;
          const lessons = unitLessons[unit.id] || [];
          const completedCount = lessons.filter(l => l.is_completed).length;

          return (
            <div key={unit.id} className={`unit-card ${isExpanded ? 'expanded' : ''}`}>
              <div
                className="unit-header"
                onClick={() => toggleUnit(unit.id)}
              >
                <div className="unit-number">Unit {index + 1}</div>
                <div className="unit-info">
                  <h2>{unit.title}</h2>
                  {unit.description && <p>{unit.description}</p>}
                  <div className="unit-meta">
                    <span>{unit.lesson_count} lessons</span>
                    {lessons.length > 0 && (
                      <span className="unit-progress">
                        {completedCount}/{unit.lesson_count} completed
                      </span>
                    )}
                  </div>
                </div>
                <div className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                  ▼
                </div>
              </div>

              {isExpanded && (
                <div className="lessons-list">
                  {loadingLessons === unit.id ? (
                    <div className="loading-lessons">
                      <div className="loading-spinner small"></div>
                    </div>
                  ) : (
                    lessons.map((lesson, lessonIndex) => {
                      const status = getLessonStatus(lesson);
                      return (
                        <div
                          key={lesson.id}
                          className={`lesson-item ${status}`}
                          onClick={() => status !== 'locked' && onSelectLesson(lesson.id)}
                        >
                          <div className="lesson-status-icon">
                            {status === 'completed' && '✓'}
                            {status === 'in-progress' && '●'}
                            {status === 'locked' && '🔒'}
                            {status === 'available' && (lessonIndex + 1)}
                          </div>
                          <div className="lesson-info">
                            <h3>{lesson.title}</h3>
                            <div className="lesson-meta">
                              <span>{lesson.estimated_minutes} min</span>
                              <span>{lesson.exercise_count} exercises</span>
                              {lesson.score && <span className="lesson-score">{Math.round(lesson.score)}%</span>}
                            </div>
                          </div>
                          {status !== 'locked' && (
                            <div className="lesson-arrow">→</div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
