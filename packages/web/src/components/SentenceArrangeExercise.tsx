/**
 * SentenceArrangeExercise - Arrange Korean word tiles to form a sentence
 * LingoDeer-style exercise implementing Active Recall and Context Learning
 */
import { useState, useMemo, useEffect, useRef } from 'react';
import type { Exercise, ExerciseResult, SentenceTile } from '@kapp/core';
import { API_BASE_URL } from '@kapp/core';
import './SentenceArrangeExercise.css';

interface Props {
  exercise: Exercise;
  onSubmit: (answer: string) => void;
  result: ExerciseResult | null;
  submitting: boolean;
}

// Fisher-Yates shuffle algorithm
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export default function SentenceArrangeExercise({ exercise, onSubmit, result, submitting }: Props) {
  const [selectedTiles, setSelectedTiles] = useState<SentenceTile[]>([]);
  const lastSelectedIdRef = useRef<number | null>(null);

  const tiles = exercise.options as SentenceTile[] | undefined;
  const isAnswered = result !== null;

  // Play audio for a tile
  function playTileAudio(tile: SentenceTile) {
    if (tile.audio_url) {
      const audio = new Audio(`${API_BASE_URL}${tile.audio_url}`);
      audio.play().catch(err => console.error('Tile audio failed:', err));
    }
  }

  // Auto-play audio when a new tile is selected
  useEffect(() => {
    if (selectedTiles.length > 0) {
      const lastTile = selectedTiles[selectedTiles.length - 1];
      // Only play if this is a newly added tile (not from initial render)
      if (lastTile.id !== lastSelectedIdRef.current) {
        lastSelectedIdRef.current = lastTile.id;
        playTileAudio(lastTile);
      }
    } else {
      lastSelectedIdRef.current = null;
    }
  }, [selectedTiles]);

  // Shuffle tiles once when exercise loads (stable during component lifetime)
  const shuffledTiles = useMemo(() => {
    if (!tiles) return [];
    return shuffleArray(tiles);
  }, [tiles]);

  if (!tiles || tiles.length === 0) {
    return <div className="error">No tiles available for this exercise</div>;
  }

  // Get available tiles (not yet selected) - maintain shuffled order
  const availableTiles = shuffledTiles.filter(
    tile => !selectedTiles.some(selected => selected.id === tile.id)
  );

  function handleRemoveTile(tile: SentenceTile) {
    if (isAnswered || submitting) return;
    setSelectedTiles(selectedTiles.filter(t => t.id !== tile.id));
  }

  function handleSelectedTileClick(tile: SentenceTile) {
    // Play audio on click (replay in drop zone)
    playTileAudio(tile);
  }

  function handleWordBankTileClick(tile: SentenceTile) {
    if (isAnswered || submitting) return;
    // Select the tile (audio will play via useEffect)
    setSelectedTiles([...selectedTiles, tile]);
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
                className={`word-tile selected ${tile.audio_url ? 'has-audio' : ''}`}
                onClick={() => {
                  if (isAnswered) {
                    // After answering, clicking plays audio
                    handleSelectedTileClick(tile);
                  } else {
                    // Before answering, clicking removes tile
                    handleRemoveTile(tile);
                  }
                }}
                onDoubleClick={(e) => {
                  // Double-click always plays audio
                  e.preventDefault();
                  playTileAudio(tile);
                }}
                disabled={submitting}
              >
                <span className="tile-korean">{tile.korean}</span>
                <span className="tile-romanization">{tile.romanization}</span>
                {tile.audio_url && <span className="tile-audio-icon">🔊</span>}
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
              className={`word-tile ${tile.audio_url ? 'has-audio' : ''}`}
              onClick={() => handleWordBankTileClick(tile)}
              disabled={submitting}
            >
              <span className="tile-korean">{tile.korean}</span>
              <span className="tile-romanization">{tile.romanization}</span>
              {tile.audio_url && <span className="tile-audio-icon">🔊</span>}
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

      {/* Note: Explanation is rendered in LessonView's result-feedback section
          to ensure consistency across all exercise types and prevent duplicate rendering */}
    </div>
  );
}
