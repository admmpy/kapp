/**
 * Dashboard - Progress and statistics overview
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import type { OverallProgress, LearningStats } from '@kapp/core';
import { Skeleton } from './Skeleton';
import './Dashboard.css';

interface Props {
  onClose?: () => void;
  onStartReview?: () => void;
}

export default function Dashboard({ onClose, onStartReview }: Props) {
  const [progress, setProgress] = useState<OverallProgress | null>(null);
  const [stats, setStats] = useState<LearningStats | null>(null);
  const [vocabDueCount, setVocabDueCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    try {
      setLoading(true);
      const [progressData, statsData, vocabData] = await Promise.all([
        apiClient.getProgress(),
        apiClient.getStats(),
        apiClient.getVocabularyDue(1)
      ]);
      setProgress(progressData);
      setStats(statsData);
      setVocabDueCount(vocabData.total_due);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <Skeleton variant="text" width={200} height={32} />
        </div>
        <div className="stats-grid">
          <Skeleton variant="rect" width="100%" height={120} />
          <Skeleton variant="rect" width="100%" height={120} />
          <Skeleton variant="rect" width="100%" height={120} />
          <Skeleton variant="rect" width="100%" height={120} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard error">
        <p>{error}</p>
        <button onClick={loadDashboardData}>Retry</button>
      </div>
    );
  }

  if (!progress || !stats) {
    return (
      <div className="dashboard empty">
        <p>No progress data available yet.</p>
        <p>Start learning to see your statistics!</p>
      </div>
    );
  }

  // Calculate derived metrics
  const vocabularyMasteryPercent = progress.average_score || 0;
  const grammarPatternsCompleted = progress.completed_lessons;
  const listeningHours = Math.round(progress.total_time_spent_minutes / 60 * 10) / 10;
  const readingPassagesCompleted = Math.floor(progress.completed_lessons * 0.3); // Rough estimate
  const topik1ReadinessPercent = Math.min(100, Math.round(
    (progress.completion_percentage * 0.5) +
    (vocabularyMasteryPercent * 0.3) +
    (stats.current_streak * 2)
  ));

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Your Progress</h1>
        {onClose && (
          <button className="close-header-btn" onClick={onClose}>
            Close
          </button>
        )}
      </div>

      {/* Primary Stats */}
      <div className="primary-stats">
        <div className="stat-card streak">
          <div className="stat-icon">🔥</div>
          <div className="stat-content">
            <h2>{stats.current_streak}</h2>
            <p>Day Streak</p>
          </div>
        </div>

        <div className="stat-card lessons">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h2>{progress.completed_lessons}</h2>
            <p>Lessons Completed</p>
          </div>
        </div>

        <div className="stat-card score">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h2>{Math.round(vocabularyMasteryPercent)}%</h2>
            <p>Average Score</p>
          </div>
        </div>
      </div>

      {/* Detailed Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card-detailed">
          <h3>Vocabulary Mastery</h3>
          <div className="progress-circle">
            <svg viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="#e0e0e0"
                strokeWidth="8"
              />
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="#667eea"
                strokeWidth="8"
                strokeDasharray={`${vocabularyMasteryPercent * 2.827} 282.7`}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
              />
              <text x="50" y="55" textAnchor="middle" fontSize="20" fontWeight="bold" fill="#2c3e50">
                {Math.round(vocabularyMasteryPercent)}%
              </text>
            </svg>
          </div>
          {vocabDueCount > 0 && (
            <div className="stat-action">
              <p>{vocabDueCount} words due for review</p>
              {onStartReview && (
                <button onClick={onStartReview}>Review Now</button>
              )}
            </div>
          )}
        </div>

        <div className="stat-card-detailed">
          <h3>Grammar Patterns</h3>
          <div className="stat-value-large">{grammarPatternsCompleted}</div>
          <p className="stat-subtitle">Patterns learned</p>
          <div className="stat-bar">
            <div
              className="stat-bar-fill"
              style={{ width: `${Math.min(100, (grammarPatternsCompleted / 50) * 100)}%` }}
            />
          </div>
        </div>

        <div className="stat-card-detailed">
          <h3>Listening Practice</h3>
          <div className="stat-value-large">{listeningHours}h</div>
          <p className="stat-subtitle">Total listening time</p>
          <div className="stat-detail">
            <span>🎧 {Math.round(progress.total_time_spent_minutes)} minutes practiced</span>
          </div>
        </div>

        <div className="stat-card-detailed">
          <h3>Reading Passages</h3>
          <div className="stat-value-large">{readingPassagesCompleted}</div>
          <p className="stat-subtitle">Passages completed</p>
          <div className="stat-detail">
            <span>📖 Keep reading to improve!</span>
          </div>
        </div>
      </div>

      {/* TOPIK Readiness */}
      <div className="topik-readiness">
        <h2>TOPIK I Readiness</h2>
        <div className="readiness-meter">
          <div className="readiness-bar">
            <div
              className="readiness-fill"
              style={{ width: `${topik1ReadinessPercent}%` }}
            />
          </div>
          <span className="readiness-percent">{topik1ReadinessPercent}%</span>
        </div>
        <p className="readiness-message">
          {topik1ReadinessPercent < 30 && "Keep learning! You're building a strong foundation."}
          {topik1ReadinessPercent >= 30 && topik1ReadinessPercent < 60 && "Good progress! Continue practicing regularly."}
          {topik1ReadinessPercent >= 60 && topik1ReadinessPercent < 80 && "Great work! You're getting close to test-ready."}
          {topik1ReadinessPercent >= 80 && "Excellent! You're well-prepared for TOPIK I."}
        </p>
      </div>

      {/* This Week Stats */}
      <div className="weekly-summary">
        <h2>This Week</h2>
        <div className="weekly-stats">
          <div className="weekly-stat">
            <span className="weekly-label">Lessons completed</span>
            <span className="weekly-value">{stats.lessons_completed_this_week}</span>
          </div>
          <div className="weekly-stat">
            <span className="weekly-label">Today's lessons</span>
            <span className="weekly-value">{stats.lessons_completed_today}</span>
          </div>
          <div className="weekly-stat">
            <span className="weekly-label">Total exercises</span>
            <span className="weekly-value">{stats.total_exercises_completed}</span>
          </div>
        </div>
      </div>

      {/* Course Progress */}
      {progress.courses.length > 0 && (
        <div className="course-progress-section">
          <h2>Course Progress</h2>
          <div className="course-progress-list">
            {progress.courses.map(course => (
              <div key={course.id} className="course-progress-item">
                <div className="course-info">
                  <h3>{course.title}</h3>
                  <span className="course-stats">
                    {course.completed_lessons} / {course.total_lessons} lessons
                  </span>
                </div>
                <div className="course-bar">
                  <div
                    className="course-bar-fill"
                    style={{ width: `${course.percentage}%` }}
                  />
                </div>
                <span className="course-percent">{Math.round(course.percentage)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
