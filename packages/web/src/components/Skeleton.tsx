/**
 * Skeleton - Pulsing skeleton placeholders for loading states
 */
import './Skeleton.css';

interface SkeletonProps {
  variant?: 'text' | 'circle' | 'rect' | 'card';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export function Skeleton({
  variant = 'rect',
  width,
  height,
  className = ''
}: SkeletonProps) {
  const style: React.CSSProperties = {};

  if (width) {
    style.width = typeof width === 'number' ? `${width}px` : width;
  }
  if (height) {
    style.height = typeof height === 'number' ? `${height}px` : height;
  }

  return (
    <div
      className={`skeleton skeleton-${variant} ${className}`}
      style={style}
    />
  );
}

export function SkeletonText({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`skeleton-text-group ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={i === lines - 1 ? '60%' : '100%'}
        />
      ))}
    </div>
  );
}

export function CourseCardSkeleton() {
  return (
    <div className="skeleton-course-card">
      <Skeleton variant="rect" className="skeleton-course-image" />
      <div className="skeleton-course-content">
        <Skeleton variant="text" width="70%" height={24} />
        <SkeletonText lines={2} />
        <div className="skeleton-course-meta">
          <Skeleton variant="rect" width={60} height={20} />
          <Skeleton variant="rect" width={80} height={20} />
        </div>
        <Skeleton variant="rect" className="skeleton-progress-bar" />
      </div>
    </div>
  );
}

export function LessonCardSkeleton() {
  return (
    <div className="skeleton-lesson-card">
      <div className="skeleton-lesson-content">
        <Skeleton variant="text" width="80%" height={20} />
        <Skeleton variant="text" width="50%" height={14} />
      </div>
      <Skeleton variant="circle" width={32} height={32} />
    </div>
  );
}

export function ExerciseSkeleton() {
  return (
    <div className="skeleton-exercise">
      <Skeleton variant="rect" width={80} height={24} className="skeleton-badge" />
      <Skeleton variant="text" width="90%" height={24} />
      <div className="skeleton-korean-display">
        <Skeleton variant="text" width="40%" height={32} />
        <Skeleton variant="text" width="30%" height={16} />
      </div>
      <div className="skeleton-options">
        <Skeleton variant="rect" className="skeleton-option" />
        <Skeleton variant="rect" className="skeleton-option" />
        <Skeleton variant="rect" className="skeleton-option" />
        <Skeleton variant="rect" className="skeleton-option" />
      </div>
    </div>
  );
}

export default Skeleton;
