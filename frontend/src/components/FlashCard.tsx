/**
 * FlashCard component displays a Korean learning card with audio playback
 */
import { useState, useRef, useEffect } from 'react';
import type { Card } from '../types';
import './FlashCard.css';

interface FlashCardProps {
  card: Card;
  showBack?: boolean;
  onFlip?: () => void;
}

export default function FlashCard({ card, showBack = false, onFlip }: FlashCardProps) {
  const [isFlipped, setIsFlipped] = useState(showBack);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Sync internal state with prop changes
  useEffect(() => {
    setIsFlipped(showBack);
  }, [showBack]);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
    if (onFlip) onFlip();
  };

  const handlePlayAudio = async () => {
    if (!card.audio_url) return;

    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }

      const audio = new Audio(card.audio_url);
      audioRef.current = audio;

      audio.onplay = () => setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setIsPlaying(false);
        console.error('Audio playback failed');
      };

      await audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
    }
  };

  return (
    <div className="flashcard-container">
      <div className={`flashcard ${isFlipped ? 'flipped' : ''}`} onClick={handleFlip}>
        <div className="flashcard-inner">
          {/* Front of card */}
          <div className="flashcard-front">
            <div className="card-level">Level {card.level}</div>
            
            <div className="card-content">
              <h1 className="korean-text">{card.front_korean}</h1>
              
              {card.front_romanization && (
                <p className="romanization">{card.front_romanization}</p>
              )}
              
              {card.is_new && (
                <span className="badge badge-new">NEW</span>
              )}
            </div>

            {card.audio_url && (
              <button
                className={`audio-button ${isPlaying ? 'playing' : ''}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handlePlayAudio();
                }}
                disabled={isPlaying}
                aria-label="Play audio"
              >
                {isPlaying ? '🔊' : '🔉'}
              </button>
            )}

            <div className="flip-hint">Click to reveal</div>
          </div>

          {/* Back of card */}
          <div className="flashcard-back">
            <div className="card-level">Level {card.level}</div>
            
            <div className="card-content">
              <h2 className="korean-text-back">{card.front_korean}</h2>
              
              {card.front_romanization && (
                <p className="romanization-back">{card.front_romanization}</p>
              )}
              
              <div className="translation-divider">→</div>
              
              <h2 className="english-text">{card.back_english}</h2>
              
              {card.example_sentence && (
                <div className="example">
                  <p className="example-label">Example:</p>
                  <p className="example-text">{card.example_sentence}</p>
                </div>
              )}
              
              <div className="card-stats">
                <span>Reviews: {card.repetitions}</span>
                {card.repetitions > 0 && (
                  <span>Interval: {card.interval} days</span>
                )}
              </div>
            </div>

            <div className="flip-hint">Click to flip back</div>
          </div>
        </div>
      </div>
    </div>
  );
}
