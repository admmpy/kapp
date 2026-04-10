/**
 * ElderConversationView — 할아버지 Mode conversation simulator (F-07)
 * Elderly Korean man persona, formal 합쇼체 register
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '@kapp/core';
import ConversationMessage from './ConversationMessage';
import type { Message } from './ConversationMessage';
import './ConversationView.css';
import './ElderConversationView.css';

const SITUATION_CARDS = [
  { title: 'Bus Stop', scene: "You're sitting next to a grandfather at a bus stop. He smiles at you warmly." },
  { title: 'Park Bench', scene: "An elderly man sits beside you on a park bench, watching pigeons." },
  { title: 'Tea House', scene: "You've been invited to sit with an elder at a traditional tea house." },
  { title: 'Market', scene: "An elderly gentleman is selling vegetables and greets you with a smile." },
  { title: 'Temple', scene: "You meet a grandfather at a temple. He seems pleased to see a foreigner." },
];

interface Props {
  onBack: () => void;
}

export default function ElderConversationView({ onBack }: Props) {
  const [situationIdx] = useState(() => Math.floor(Math.random() * SITUATION_CARDS.length));
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [opening, setOpening] = useState<string | null>(null);
  const [starterIndex, setStarterIndex] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [translateLoadingId, setTranslateLoadingId] = useState<string | null>(null);
  const [started, setStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<Array<{ user: string; assistant: string }>>([]);

  // Fetch the opening line on mount
  useEffect(() => {
    apiClient.getElderConversationStart()
      .then(({ opening: op, starter_index: idx }) => {
        setOpening(op);
        setStarterIndex(idx);
      })
      .catch(() => {
        setOpening('어서 오세요! 한국어를 공부하고 계십니까?');
      });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function startConversation() {
    if (!opening) return;
    const openerMsg: Message = {
      id: `assistant-0`,
      role: 'assistant',
      content: opening,
      timestamp: new Date().toISOString(),
    };
    setMessages([openerMsg]);
    setStarted(true);
    // Generate audio for opener in background
    apiClient.generateAudio(opening).then(({ filename }) => {
      const audioUrl = apiClient.getAudioUrl(filename);
      setMessages((prev) => prev.map((m) => m.id === 'assistant-0' ? { ...m, audioUrl } : m));
    }).catch(() => {});
  }

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await apiClient.sendElderConversationMessage(userMessage, {
        conversation_history: historyRef.current,
        starter_index: starterIndex,
      });

      const assistantId = `assistant-${Date.now()}`;
      const assistantMsg: Message = {
        id: assistantId,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Update history ref
      historyRef.current = [
        ...historyRef.current,
        { user: userMessage, assistant: response.response },
      ].slice(-5);

      // Generate audio in background
      apiClient.generateAudio(response.response).then(({ filename }) => {
        const audioUrl = apiClient.getAudioUrl(filename);
        setMessages((prev) => prev.map((m) => m.id === assistantId ? { ...m, audioUrl } : m));
      }).catch(() => {});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [inputValue, loading, starterIndex]);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handlePlayAudio = async (audioUrl: string) => {
    if (!audioUrl) return;
    try {
      await new Audio(audioUrl).play();
    } catch {}
  };

  const handleTranslate = async (messageId: string) => {
    const msg = messages.find((m) => m.id === messageId);
    if (!msg || msg.translation) return;
    setTranslateLoadingId(messageId);
    try {
      const { translation } = await apiClient.translateText(msg.content);
      setMessages((prev) => prev.map((m) => m.id === messageId ? { ...m, translation } : m));
    } catch {}
    setTranslateLoadingId(null);
  };

  const situation = SITUATION_CARDS[situationIdx];

  return (
    <div className="conversation-view elder-conversation-view">
      <header className="conversation-header">
        <button className="back-button" onClick={onBack}>← Back</button>
        <h1>할아버지 Mode</h1>
        <p className="subtitle">Elder Conversation Simulator</p>
      </header>

      <div className="conversation-container">
        {!started ? (
          <div className="elder-intro">
            <div className="elder-scene-card">
              <div className="elder-icon">👴</div>
              <h2>{situation.title}</h2>
              <p className="elder-scene">{situation.scene}</p>
            </div>

            <div className="elder-tips">
              <h3>Tips for this conversation</h3>
              <ul>
                <li>Use formal endings: -ㅂ니다/습니다 or -세요</li>
                <li>Address him as 할아버지 or 어르신</li>
                <li>Speak slowly and simply</li>
                <li>It's okay to say 잘 모르겠어요 (I'm not sure)</li>
              </ul>
            </div>

            {opening && (
              <div className="elder-opening-preview">
                <p className="elder-opening-label">He opens with:</p>
                <p className="elder-opening-text">"{opening}"</p>
              </div>
            )}

            <button
              className="elder-start-btn"
              onClick={startConversation}
              disabled={!opening}
            >
              {opening ? 'Begin Conversation' : 'Loading...'}
            </button>
          </div>
        ) : (
          <>
            <div className="messages-container">
              {messages.map((message) => (
                <ConversationMessage
                  key={message.id}
                  message={message}
                  onPlayAudio={handlePlayAudio}
                  onTranslate={handleTranslate}
                  audioLoading={false}
                  translateLoading={translateLoadingId === message.id}
                />
              ))}

              {loading && (
                <div className="message-group assistant">
                  <div className="thinking-indicator">
                    <span></span><span></span><span></span>
                  </div>
                  <p className="thinking-text">할아버지 is thinking...</p>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {error && (
              <div className="error-message"><p>⚠️ {error}</p></div>
            )}

            <div className="input-section">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="한국어로 말씀해 주세요... (speak Korean)"
                disabled={loading}
                className="conversation-input"
                autoFocus
              />
              <button
                onClick={handleSendMessage}
                disabled={loading || !inputValue.trim()}
                className="send-button"
              >
                {loading ? '...' : 'Send'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
