/**
 * DailyMission - Today's focused learning plan card
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@kapp/core';
import './DailyMission.css';

interface MissionTask {
  type: string;
  label: string;
  description: string;
  lesson_id?: number;
  estimated_minutes: number;
  icon: string;
  action: string;
}

interface Props {
  onStartLesson?: (lessonId: number) => void;
  onStartReview?: () => void;
}

export default function DailyMission({ onStartLesson, onStartReview }: Props) {
  const [tasks, setTasks] = useState<MissionTask[]>([]);
  const [totalMinutes, setTotalMinutes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    apiClient.getDailyMission().then((data) => {
      setTasks(data.tasks);
      setTotalMinutes(data.total_estimated_minutes);
    }).catch(() => {
      // Silent fail — mission card is non-critical
    }).finally(() => {
      setLoading(false);
    });
  }, []);

  if (loading || tasks.length === 0) return null;

  function handleTaskClick(task: MissionTask) {
    if (task.action === 'review' && onStartReview) {
      onStartReview();
    } else if (task.action === 'lesson' && task.lesson_id && onStartLesson) {
      onStartLesson(task.lesson_id);
    }
  }

  return (
    <div className="daily-mission">
      <button
        className="daily-mission-header"
        onClick={() => setCollapsed((c) => !c)}
        aria-expanded={!collapsed}
      >
        <div className="daily-mission-title">
          <span className="daily-mission-icon">🎯</span>
          <span>Today's Mission</span>
        </div>
        <div className="daily-mission-meta">
          <span className="daily-mission-time">{totalMinutes} min</span>
          <span className="daily-mission-chevron">{collapsed ? '▸' : '▾'}</span>
        </div>
      </button>

      {!collapsed && (
        <ul className="daily-mission-tasks">
          {tasks.map((task, i) => (
            <li key={i} className="daily-mission-task">
              <button
                className="mission-task-btn"
                onClick={() => handleTaskClick(task)}
                disabled={task.action === 'home'}
              >
                <span className="task-icon">{task.icon}</span>
                <div className="task-body">
                  <span className="task-label">{task.label}</span>
                  <span className="task-desc">{task.description}</span>
                </div>
                <span className="task-time">{task.estimated_minutes}m</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
