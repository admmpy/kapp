/**
 * Explanation Modal - displays AI-generated card explanations
 */
import { useState, useEffect } from 'react';
import { llmClient } from '../api/llm';
import type { Card } from '../types';
import './ExplanationModal.css';

interface Props {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  userContext?: {
    level?: number;
    previous_ratings?: number[];
    time_spent?: number;
  };
}

export default function ExplanationModal({ card, isOpen, onClose, userContext }: Props) {
  const [explanation, setExplanation] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchExplanation();
    }
  }, [isOpen, card.id]);

  const fetchExplanation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await llmClient.explainCard({
        card_id: card.id,
        user_context: userContext,
      });
      setExplanation(result.explanation);
    } catch (err) {
      console.error('Error fetching explanation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load explanation');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>💡 Explanation</h2>
          <button className="close-button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        
        <div className="modal-body">
          <div className="card-reference">
            <div className="korean">{card.front_korean}</div>
            {card.front_romanization && (
              <div className="romanization">{card.front_romanization}</div>
            )}
            <div className="english">{card.back_english}</div>
          </div>

          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Generating explanation...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button onClick={fetchExplanation} className="button button-secondary">
                Try Again
              </button>
            </div>
          )}

          {explanation && !loading && (
            <div className="explanation-content">
              {explanation.split('\n').map((paragraph, i) => (
                paragraph.trim() && <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="button button-primary">
            Got It!
          </button>
        </div>
      </div>
    </div>
  );
}

