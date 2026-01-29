/**
 * ProgressBar - Shows lesson progress
 */
import './ProgressBar.css';

interface Props {
  current: number;
  total: number;
  correct: number;
}

export default function ProgressBar({ current, total, correct }: Props) {
  const progress = (current / total) * 100;

  return (
    <div className="progress-bar-container">
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
        <div className="progress-markers">
          {Array.from({ length: total }, (_, i) => (
            <div
              key={i}
              className={`progress-marker ${i < current - 1 ? 'completed' : ''} ${i === current - 1 ? 'current' : ''}`}
            />
          ))}
        </div>
      </div>
      <div className="progress-info">
        <span className="progress-count">{current}/{total}</span>
        <span className="progress-correct">{correct} correct</span>
      </div>
    </div>
  );
}
