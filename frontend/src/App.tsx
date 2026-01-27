/**
 * Main App component - handles routing for lesson-based learning
 */
import { useState, useEffect } from 'react';
import CourseList from './components/CourseList';
import UnitView from './components/UnitView';
import LessonView from './components/LessonView';
import './App.css';

type Page = 'courses' | 'units' | 'lesson';

interface AppState {
  page: Page;
  courseId: number | null;
  lessonId: number | null;
}

function App() {
  const [state, setState] = useState<AppState>({
    page: 'courses',
    courseId: null,
    lessonId: null
  });

  // Parse URL hash for routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);

      if (hash.startsWith('lesson/')) {
        const lessonId = parseInt(hash.split('/')[1]);
        if (!isNaN(lessonId)) {
          setState({ page: 'lesson', courseId: null, lessonId });
          return;
        }
      }

      if (hash.startsWith('course/')) {
        const courseId = parseInt(hash.split('/')[1]);
        if (!isNaN(courseId)) {
          setState({ page: 'units', courseId, lessonId: null });
          return;
        }
      }

      setState({ page: 'courses', courseId: null, lessonId: null });
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  function navigateToCourses() {
    window.location.hash = '';
    setState({ page: 'courses', courseId: null, lessonId: null });
  }

  function navigateToCourse(courseId: number) {
    window.location.hash = `course/${courseId}`;
    setState({ page: 'units', courseId, lessonId: null });
  }

  function navigateToLesson(lessonId: number) {
    window.location.hash = `lesson/${lessonId}`;
    setState({ page: 'lesson', courseId: state.courseId, lessonId });
  }

  function handleLessonComplete() {
    // Go back to course view after completing a lesson
    if (state.courseId) {
      navigateToCourse(state.courseId);
    } else {
      navigateToCourses();
    }
  }

  function handleLessonBack() {
    if (state.courseId) {
      navigateToCourse(state.courseId);
    } else {
      navigateToCourses();
    }
  }

  return (
    <div className="app">
      {state.page === 'courses' && (
        <CourseList onSelectCourse={navigateToCourse} />
      )}

      {state.page === 'units' && state.courseId && (
        <UnitView
          courseId={state.courseId}
          onSelectLesson={navigateToLesson}
          onBack={navigateToCourses}
        />
      )}

      {state.page === 'lesson' && state.lessonId && (
        <LessonView
          lessonId={state.lessonId}
          onComplete={handleLessonComplete}
          onBack={handleLessonBack}
        />
      )}
    </div>
  );
}

export default App;
