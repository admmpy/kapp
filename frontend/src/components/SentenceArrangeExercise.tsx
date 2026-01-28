/**
 * SentenceArrangeExercise - Arrange Korean word tiles to form a sentence
 * LingoDeer-style exercise implementing Active Recall and Context Learning
 */
import { useState } from 'react';
import type { Exercise, ExerciseResult, SentenceTile } from '../types';
import './SentenceArrangeExercise.css';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string) => void;
  result: ExerciseResult | null;
  submitting: boolean;
}

export default function SentenceArrangeExercise({ exercise, onSubmit, result, submitting }: Props) {
  const [selectedTiles, setSelectedTiles] = useState<SentenceTile[]>([]);

  const tiles = exercise.options as SentenceTile[] | undefined;
  const isAnswered = result !== null;

  if (!tiles || tiles.length === 0) {
    return <div className="error">No tiles available for this exercise</div>;
  }

  // Get available tiles (not yet selected)
  const availableTiles = tiles.filter(
    tile => !selectedTiles.some(selected => selected.id === tile.id)
  );

  function handleTileClick(tile: SentenceTile) {
    if (isAnswered || submitting) return;
    setSelectedTiles([...selectedTiles, tile]);
  }

  function handleRemoveTile(tile: SentenceTile) {
    if (isAnswered || submitting) return;
    setSelectedTiles(selectedTiles.filter(t => t.id !== tile.id));
  }

  function handleSubmit() {
    if (submitting || isAnswered || selectedTiles.length === 0) return;
    // Submit array of tile IDs as JSON string
    const answerIds = selectedTiles.map(t => t.id);
    onSubmit(JSON.stringify(answerIds));
  }

  function handleClear() {
    if (isAnswered || submitting) return;
    setSelectedTiles([]);
  }

  // Parse correct answer for feedback
  function getCorrectTileOrder(): SentenceTile[] {
    if (!result?.correct_answer || !tiles) return [];
    try {
      const correctIds = JSON.parse(result.correct_answer) as number[];
      return correctIds.map(id => tiles.find(t => t.id === id)).filter((t): t is SentenceTile => t !== undefined);
    } catch {
      return [];
    }
  }

  const correctOrder = isAnswered ? getCorrectTileOrder() : [];

  return (
    <div className="sentence-arrange-exercise">
      {/* Exercise type badge */}
      <div className="exercise-type-badge">Sentence Arrange</div>

      {/* Instruction */}
      {exercise.instruction && (
        <p className="exercise-instruction">{exercise.instruction}</p>
      )}

      {/* Question (English sentence to translate) */}
      <div className="exercise-question">
        <p>{exercise.question}</p>
      </div>

      {/* Drop zone - where selected tiles appear */}
      <div className={`drop-zone ${isAnswered ? (result?.correct ? 'correct' : 'incorrect') : ''}`}>
        {selectedTiles.length === 0 ? (
          <span className="drop-zone-placeholder">Tap words below to build your sentence</span>
        ) : (
          <div className="selected-tiles">
            {selectedTiles.map((tile, index) => (
              <button
                key={`selected-${tile.id}-${index}`}
                className="word-tile selected"
                onClick={() => handleRemoveTile(tile)}
                disabled={isAnswered || submitting}
              >
                <span className="tile-korean">{tile.korean}</span>
                <span className="tile-romanization">{tile.romanization}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Show correct answer if wrong */}
      {isAnswered && !result?.correct && correctOrder.length > 0 && (
        <div className="correct-answer-display">
          <span className="correct-label">Correct order:</span>
          <div className="correct-tiles">
            {correctOrder.map((tile, index) => (
              <span key={`correct-${tile.id}-${index}`} className="correct-tile">
                {tile.korean}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Word bank - available tiles to select */}
      {!isAnswered && (
        <div className="word-bank">
          {availableTiles.map((tile, index) => (
            <button
              key={`available-${tile.id}-${index}`}
              className="word-tile"
              onClick={() => handleTileClick(tile)}
              disabled={submitting}
            >
              <span className="tile-korean">{tile.korean}</span>
              <span className="tile-romanization">{tile.romanization}</span>
            </button>
          ))}
        </div>
      )}

      {/* Action buttons */}
      {!isAnswered && (
        <div className="action-buttons">
          <button
            className="clear-button"
            onClick={handleClear}
            disabled={submitting || selectedTiles.length === 0}
          >
            Clear
          </button>
          <button
            className="submit-button"
            onClick={handleSubmit}
            disabled={submitting || selectedTiles.length === 0}
          >
            {submitting ? 'Checking...' : 'Check Answer'}
          </button>
        </div>
      )}

      {/* Explanation after answering */}
      {isAnswered && result?.explanation && (
        <div className="explanation">
          {result.explanation}
        </div>
      )}
    </div>
  );
}
