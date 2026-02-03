/**
 * Main App component - handles routing for lesson-based learning
 */
import { useState, useEffect } from 'react';
import CourseList from './components/CourseList';
import UnitView from './components/UnitView';
import LessonView from './components/LessonView';
import ConversationView from './components/ConversationView';
import ErrorBoundary from './components/ErrorBoundary';
import IosInstallPrompt from './components/IosInstallPrompt';
import { initDB, setupOnlineListener } from '@kapp/core';
import './App.css';

type Page = 'courses' | 'units' | 'lesson' | 'conversation';

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
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Initialize IndexedDB and setup online/offline listeners
  useEffect(() => {
    initDB().catch(err => {
      console.error('Failed to initialize IndexedDB:', err);
    });

    const cleanup = setupOnlineListener();

    const handleOnlineStatus = () => setIsOnline(navigator.onLine);
    const handleOfflineStatus = () => setIsOnline(navigator.onLine);

    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);

    return () => {
      cleanup();
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOfflineStatus);
    };
  }, []);

  // Parse URL hash for routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);

      if (hash === 'conversation') {
        setState({ page: 'conversation', courseId: null, lessonId: null });
        return;
      }

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

  function handleLessonExit() {
    if (state.courseId) {
      navigateToCourse(state.courseId);
    } else {
      navigateToCourses();
    }
  }

  function navigateToConversation() {
    window.location.hash = 'conversation';
    setState({ page: 'conversation', courseId: null, lessonId: null });
  }

  return (
    <ErrorBoundary>
      <div className="app">
        {!isOnline && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '8px 16px',
            textAlign: 'center',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: 9999,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            Offline - Your progress will sync when reconnected
          </div>
        )}
        <IosInstallPrompt />
        {state.page === 'courses' && (
          <ErrorBoundary>
            <CourseList
              onSelectCourse={navigateToCourse}
              onStartConversation={navigateToConversation}
            />
          </ErrorBoundary>
        )}

        {state.page === 'conversation' && (
          <ErrorBoundary>
            <ConversationView onBack={navigateToCourses} />
          </ErrorBoundary>
        )}

        {state.page === 'units' && state.courseId && (
          <ErrorBoundary>
            <UnitView
              courseId={state.courseId}
              onSelectLesson={navigateToLesson}
              onBack={navigateToCourses}
            />
          </ErrorBoundary>
        )}

        {state.page === 'lesson' && state.lessonId && (
          <ErrorBoundary>
            <LessonView
              lessonId={state.lessonId}
              courseId={state.courseId}
              onComplete={handleLessonExit}
              onBack={handleLessonExit}
              onBackToCourse={navigateToCourse}
              onBackToCourses={navigateToCourses}
              onNavigateToLesson={navigateToLesson}
            />
          </ErrorBoundary>
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;
