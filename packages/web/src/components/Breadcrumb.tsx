/**
 * Breadcrumb Navigation - Shows full path and allows jumping back
 */
import { useEffect, useState } from 'react';
import { apiClient } from '@kapp/core';
import type { Course, Unit } from '@kapp/core';
import './Breadcrumb.css';

interface Props {
  courseId?: number | null;
  unitId?: number | null;
  courseName?: string;
  unitName?: string;
  onNavigateToCourse?: (courseId: number) => void;
  onNavigateToCourses?: () => void;
}

export default function Breadcrumb({
  courseId,
  unitId,
  courseName,
  unitName,
  onNavigateToCourse,
  onNavigateToCourses
}: Props) {
  const [course, setCourse] = useState<Course | null>(null);
  const [unit, setUnit] = useState<Unit | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (courseId) {
          const courseData = await apiClient.getCourse(courseId);
          setCourse(courseData);

          if (unitId) {
            const unitData = await apiClient.getUnit(unitId);
            setUnit(unitData);
          }
        }
      } catch (err) {
        console.error('Failed to load breadcrumb data:', err);
      }
    };

    loadData();
  }, [courseId, unitId]);

  // Use provided names if available, fallback to loaded data
  const displayCourseName = courseName || course?.title;
  const displayUnitName = unitName || unit?.title;

  return (
    <nav className="breadcrumb">
      <ol className="breadcrumb-list">
        <li className="breadcrumb-item">
          <button
            className="breadcrumb-link"
            onClick={onNavigateToCourses}
          >
            Courses
          </button>
        </li>

        {courseId && displayCourseName && (
          <li className="breadcrumb-item">
            <span className="breadcrumb-separator">/</span>
            <button
              className="breadcrumb-link"
              onClick={() => onNavigateToCourse?.(courseId)}
            >
              {displayCourseName}
            </button>
          </li>
        )}

        {unitId && displayUnitName && (
          <li className="breadcrumb-item">
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">
              {displayUnitName}
            </span>
          </li>
        )}
      </ol>
    </nav>
  );
}
