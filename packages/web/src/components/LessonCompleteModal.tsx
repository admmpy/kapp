/**
 * LessonCompleteModal - Shows completion stats and next lesson preview
 */
import './LessonCompleteModal.css';

interface Lesson {
  id: number;
  title: string;
  estimated_minutes: number;
  exercise_count: number;
}

interface PatternMasteryResult {
  pattern_title: string;
  mastery_score: number;
  attempts: number;
}

interface Props {
  lessonTitle: string;
  score: number;
  correctAnswers: number;
  totalAnswers: number;
  nextLesson?: Lesson;
  isLastInUnit: boolean;
  isLastInCourse: boolean;
  onNextLesson?: (lessonId: number) => void;
  onBackToCourse: () => void;
  patternMasteryResults?: PatternMasteryResult[];
}

export default function LessonCompleteModal({
  lessonTitle,
  score,
  correctAnswers,
  totalAnswers,
  nextLesson,
  isLastInUnit,
  isLastInCourse,
  onNextLesson,
  onBackToCourse,
  patternMasteryResults
}: Props) {
  const percentage = totalAnswers > 0 ? (correctAnswers / totalAnswers) * 100 : 0;
  const getScoreColor = () => {
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    return 'needs-work';
  };

  const getScoreMessage = () => {
    if (percentage >= 80) return 'Excellent work! 🎉';
    if (percentage >= 60) return 'Great job! 👍';
    return 'Keep practicing! 💪';
  };

  return (
    <div className="modal-overlay">
      <div className="lesson-complete-modal">
        <div className="modal-header">
          <h1>Lesson Complete!</h1>
          <p className="lesson-title">{lessonTitle}</p>
        </div>

        <div className={`score-section ${getScoreColor()}`}>
          <div className="score-circle">
            <div className="score-value">{Math.round(score)}%</div>
          </div>
          <p className="score-message">{getScoreMessage()}</p>
          <div className="score-details">
            <p>
              <strong>{correctAnswers}</strong> correct out of <strong>{totalAnswers}</strong> exercises
            </p>
          </div>
        </div>

        <div className="modal-body">
          {isLastInCourse ? (
            <div className="completion-message">
              <h2>🎊 Course Complete!</h2>
              <p>You've completed this course. Great achievement!</p>
            </div>
          ) : isLastInUnit ? (
            <div className="completion-message">
              <h2>✨ Unit Complete!</h2>
              <p>You've finished all lessons in this unit.</p>
            </div>
          ) : null}

          {nextLesson && !isLastInCourse && (
            <div className="next-lesson-preview">
              <h3>Next Lesson</h3>
              <div className="lesson-card">
                <div className="lesson-icon">→</div>
                <div className="lesson-info">
                  <h4>{nextLesson.title}</h4>
                  <p className="lesson-meta">
                    <span>{nextLesson.estimated_minutes} min</span>
                    <span>{nextLesson.exercise_count} exercises</span>
                  </p>
                </div>
              </div>
            </div>
          )}

          {patternMasteryResults && patternMasteryResults.length > 0 && (() => {
            const weakest = [...patternMasteryResults]
              .sort((a, b) => a.mastery_score - b.mastery_score)
              .slice(0, 2);
            return (
              <div className="weakest-patterns">
                <h3>Weakest Patterns</h3>
                <ul className="weakest-patterns-list">
                  {weakest.map((p, i) => (
                    <li key={i} className="weakest-pattern-item">
                      <span className="pattern-name">{p.pattern_title}</span>
                      <span className={`pattern-score ${
                        p.mastery_score >= 80 ? 'score-high' :
                        p.mastery_score >= 50 ? 'score-mid' : 'score-low'
                      }`}>
                        {Math.round(p.mastery_score)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })()}
        </div>

        <div className="modal-footer">
          {nextLesson && !isLastInCourse && onNextLesson && (
            <button
              className="button button-primary"
              onClick={() => onNextLesson(nextLesson.id)}
            >
              Start Next Lesson →
            </button>
          )}
          <button className="button button-secondary" onClick={onBackToCourse}>
            {isLastInCourse ? 'Back to Courses' : 'Back to Unit'}
          </button>
        </div>
      </div>
    </div>
  );
}
