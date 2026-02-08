/**
 * Main App component - handles routing for lesson-based learning
 */
import { useState, useEffect } from 'react';
import CourseList from './components/CourseList';
import UnitView from './components/UnitView';
import LessonView from './components/LessonView';
import ConversationView from './components/ConversationView';
import Dashboard from './components/Dashboard';
import VocabularyReview from './components/VocabularyReview';
import WeaknessReview from './components/WeaknessReview';
import ErrorBoundary from './components/ErrorBoundary';
import IosInstallPrompt from './components/IosInstallPrompt';
import BottomNav from './components/BottomNav';
import type { Tab } from './components/BottomNav';
import { initDB, setupOnlineListener, WEAKNESS_REVIEW_ENABLED } from '@kapp/core';
import './App.css';

type Page = 'courses' | 'units' | 'lesson' | 'conversation' | 'dashboard' | 'vocabulary-review' | 'weakness-review';
type Theme = 'light' | 'dark';

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
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

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

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Parse URL hash for routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);

      if (hash === 'conversation') {
        setState({ page: 'conversation', courseId: null, lessonId: null });
        return;
      }

      if (hash === 'dashboard') {
        setState({ page: 'dashboard', courseId: null, lessonId: null });
        return;
      }

      if (hash === 'review') {
        setState({ page: 'vocabulary-review', courseId: null, lessonId: null });
        return;
      }

      if (hash === 'weakness-review') {
        setState({ page: 'weakness-review', courseId: null, lessonId: null });
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

  function navigateToDashboard() {
    window.location.hash = 'dashboard';
    setState({ page: 'dashboard', courseId: null, lessonId: null });
  }

  function navigateToReview() {
    window.location.hash = 'review';
    setState({ page: 'vocabulary-review', courseId: null, lessonId: null });
  }

  function navigateToWeaknessReview() {
    window.location.hash = 'weakness-review';
    setState({ page: 'weakness-review', courseId: null, lessonId: null });
  }

  function handleToggleTheme() {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  }

  function handleBottomNavNavigate(tab: Tab) {
    switch (tab) {
      case 'courses': navigateToCourses(); break;
      case 'dashboard': navigateToDashboard(); break;
      case 'vocabulary-review': navigateToReview(); break;
      case 'conversation': navigateToConversation(); break;
    }
  }

  const showBottomNav = ['courses', 'dashboard', 'vocabulary-review', 'weakness-review', 'conversation'].includes(state.page);

  // Map current page to a bottom nav tab (units maps to courses since it's a drill-down)
  const activeTab: Tab = (state.page === 'units' || state.page === 'lesson')
    ? 'courses'
    : state.page === 'weakness-review'
    ? 'dashboard'
    : state.page as Tab;

  return (
    <ErrorBoundary>
      <div className={`app ${showBottomNav ? 'has-bottom-nav' : ''}`}>
        {!isOnline && (
          <div className="offline-banner">
            Offline - Your progress will sync when reconnected
          </div>
        )}
        <IosInstallPrompt />
        {state.page === 'courses' && (
          <ErrorBoundary>
            <CourseList
              onSelectCourse={navigateToCourse}
              onStartConversation={navigateToConversation}
              theme={theme}
              onToggleTheme={handleToggleTheme}
            />
          </ErrorBoundary>
        )}

        {state.page === 'conversation' && (
          <ErrorBoundary>
            <ConversationView onBack={navigateToCourses} />
          </ErrorBoundary>
        )}

        {state.page === 'dashboard' && (
          <ErrorBoundary>
            <Dashboard onClose={navigateToCourses} onStartReview={navigateToReview} onStartWeaknessReview={navigateToWeaknessReview} />
          </ErrorBoundary>
        )}

        {state.page === 'vocabulary-review' && (
          <ErrorBoundary>
            <VocabularyReview onClose={navigateToDashboard} />
          </ErrorBoundary>
        )}

        {state.page === 'weakness-review' && WEAKNESS_REVIEW_ENABLED && (
          <ErrorBoundary>
            <WeaknessReview onClose={navigateToDashboard} />
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

        {showBottomNav && (
          <BottomNav activeTab={activeTab} onNavigate={handleBottomNavNavigate} />
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;
