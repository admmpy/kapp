/**
 * ImmersionSelector - Shared segmented button for immersion level
 */
import type { ImmersionLevel } from '@kapp/core';
import './ImmersionSelector.css';

interface Props {
  level: ImmersionLevel;
  onChange: (level: ImmersionLevel) => void;
  compact?: boolean;
}

const IMMERSION_LABELS: Record<ImmersionLevel, string> = {
  1: 'Full',
  2: 'Reduced',
  3: 'Minimal',
};

const IMMERSION_TITLES: Record<ImmersionLevel, string> = {
  1: 'Korean + romanization + English',
  2: 'Korean + English (no romanization)',
  3: 'Korean only (English in feedback)',
};

export default function ImmersionSelector({ level, onChange, compact = false }: Props) {
  return (
    <div className={`immersion-selector ${compact ? 'immersion-selector--compact' : ''}`}>
      <span className="immersion-selector__label">
        {compact ? 'Immersion' : 'Immersion Level'}
      </span>
      <div className="immersion-selector__buttons">
        {([1, 2, 3] as ImmersionLevel[]).map(l => (
          <button
            key={l}
            className={`immersion-selector__btn ${level === l ? 'active' : ''}`}
            onClick={() => onChange(l)}
            title={IMMERSION_TITLES[l]}
          >
            {IMMERSION_LABELS[l]}
          </button>
        ))}
      </div>
    </div>
  );
}
