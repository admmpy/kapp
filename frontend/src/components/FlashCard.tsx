/**
 * FlashCard component displays a Korean learning card with audio playback
 */
import { useRef, useState, useEffect } from 'react';
import type { Card } from '../types';
import { API_BASE_URL } from '../api/client';
import './FlashCard.css';

interface FlashCardProps {
  card: Card;
  showBack?: boolean;
  onFlip?: () => void;
  autoPlayOnFlip?: boolean;
}

export default function FlashCard({ card, showBack = false, onFlip, autoPlayOnFlip = true }: FlashCardProps) {
  const isFlipped = showBack;
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const retryCountRef = useRef(0);
  const maxRetries = 3;

  // Auto-play audio when card flips to reveal answer
  useEffect(() => {
    if (autoPlayOnFlip && showBack && card.audio_url) {
      // Small delay to allow flip animation to complete
      const timer = setTimeout(() => {
        handlePlayAudio();
      }, 400); // 400ms matches the flip animation duration

      return () => clearTimeout(timer);
    }
  }, [showBack, card.id, autoPlayOnFlip]); // Re-run when showBack changes or card changes

  const handleFlip = () => {
    if (onFlip) onFlip();
  };

  const handlePlayAudio = async (isRetry: boolean = false) => {
    if (!card.audio_url) return;

    // Don't retry if we've exceeded max retries
    if (isRetry && retryCountRef.current >= maxRetries) {
      console.error(`[Card ${card.id}] Max retries (${maxRetries}) exceeded for audio playback`);
      setAudioError(true);
      setAudioLoading(false);
      return;
    }

    try {
      setAudioLoading(true);
      setAudioError(false);

      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }

      // Construct full URL - audio_url from backend is relative (e.g., "/api/audio/file.mp3")
      const fullAudioUrl = `${API_BASE_URL}${card.audio_url}`;
      const audio = new Audio(fullAudioUrl);
      audioRef.current = audio;

      audio.onloadstart = () => {
        setAudioLoading(true);
      };

      audio.oncanplaythrough = () => {
        setAudioLoading(false);
      };

      audio.onplay = () => {
        setIsPlaying(true);
        setAudioLoading(false);
        setAudioError(false);
        retryCountRef.current = 0; // Reset retry count on success
      };

      audio.onended = () => {
        setIsPlaying(false);
      };

      audio.onerror = (e) => {
        setIsPlaying(false);
        setAudioLoading(false);
        console.error(`[Card ${card.id}] Audio playback failed:`, e);
        console.error(`[Card ${card.id}] Audio URL: ${fullAudioUrl}`);
        
        // Retry with exponential backoff
        if (retryCountRef.current < maxRetries) {
          retryCountRef.current++;
          const backoffDelay = Math.pow(2, retryCountRef.current - 1) * 1000; // 1s, 2s, 4s
          console.log(`[Card ${card.id}] Retrying audio in ${backoffDelay}ms (attempt ${retryCountRef.current}/${maxRetries})`);
          
          setTimeout(() => {
            handlePlayAudio(true);
          }, backoffDelay);
        } else {
          setAudioError(true);
          console.error(`[Card ${card.id}] Audio failed after ${maxRetries} retries`);
        }
      };

      await audio.play();
    } catch (error) {
      console.error(`[Card ${card.id}] Error playing audio:`, error);
      setIsPlaying(false);
      setAudioLoading(false);
      setAudioError(true);
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
                className={`audio-button ${isPlaying ? 'playing' : ''} ${audioError ? 'error' : ''} ${audioLoading ? 'loading' : ''}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handlePlayAudio();
                }}
                disabled={isPlaying || audioLoading}
                aria-label={audioError ? 'Audio error - click to retry' : isPlaying ? 'Playing audio' : audioLoading ? 'Loading audio' : 'Play audio'}
                title={audioError ? 'Audio failed to load - click to retry' : isPlaying ? 'Playing...' : audioLoading ? 'Loading...' : 'Play pronunciation'}
              >
                {audioError ? '⚠️' : audioLoading ? '⏳' : isPlaying ? '🔊' : '🔉'}
              </button>
            )}

            <div className="flip-hint">Click to reveal</div>
          </div>

          {/* Back of card */}
          <div className="flashcard-back">
            <div className="card-level">Level {card.level}</div>
            
            <div className="card-content">
              <h2 className="english-text">{card.back_english || 'Translation unavailable'}</h2>
              
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
