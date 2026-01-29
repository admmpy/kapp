/**
 * ConversationMessage - Individual message bubble with optional audio
 */
import './ConversationMessage.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  audioUrl?: string;
}

interface Props {
  message: Message;
  onPlayAudio: (audioUrl: string) => void;
}

export default function ConversationMessage({ message, onPlayAudio }: Props) {
  const isUser = message.role === 'user';

  const formatTime = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className={`message-group ${message.role}`}>
      <div className="message-bubble">
        <p className="message-content">{message.content}</p>
        {!isUser && message.audioUrl && (
          <button
            className="audio-button"
            onClick={() => onPlayAudio(message.audioUrl!)}
            title="Play audio pronunciation"
            aria-label="Play audio"
          >
            🔊
          </button>
        )}
      </div>
      <span className="message-time">{formatTime(message.timestamp)}</span>
    </div>
  );
}
