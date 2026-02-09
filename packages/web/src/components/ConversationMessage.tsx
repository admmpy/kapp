/**
 * ConversationMessage - Individual message bubble with audio & translate actions
 */
import { useState } from 'react';
import './ConversationMessage.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  audioUrl?: string;
  translation?: string;
}

interface Props {
  message: Message;
  onPlayAudio: (audioUrl: string) => void;
  onTranslate?: (messageId: string) => void;
  audioLoading?: boolean;
  translateLoading?: boolean;
}

export default function ConversationMessage({
  message,
  onPlayAudio,
  onTranslate,
  audioLoading,
  translateLoading,
}: Props) {
  const isUser = message.role === 'user';
  const [showTranslation, setShowTranslation] = useState(false);

  const formatTime = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const handleTranslateClick = () => {
    if (!message.translation && onTranslate) {
      onTranslate(message.id);
    }
    setShowTranslation((prev) => !prev);
  };

  return (
    <div className={`message-group ${message.role}`}>
      <div className="message-bubble">
        <p className="message-content">{message.content}</p>
        {showTranslation && message.translation && (
          <p className="translation-text">{message.translation}</p>
        )}
        {showTranslation && translateLoading && (
          <p className="translation-text translation-loading">Translating...</p>
        )}
      </div>
      {!isUser && (
        <div className="message-actions">
          <button
            className="action-button"
            onClick={() => message.audioUrl && onPlayAudio(message.audioUrl)}
            disabled={audioLoading || !message.audioUrl}
            title="Play audio pronunciation"
            aria-label="Play audio"
          >
            {audioLoading ? '...' : '\u{1F50A}'}
          </button>
          <button
            className="action-button"
            onClick={handleTranslateClick}
            disabled={translateLoading}
            title={showTranslation ? 'Hide translation' : 'Show English translation'}
            aria-label="Translate"
          >
            {translateLoading ? '...' : '\u{1F310}'}
          </button>
        </div>
      )}
      <span className="message-time">{formatTime(message.timestamp)}</span>
    </div>
  );
}

export type { Message };
