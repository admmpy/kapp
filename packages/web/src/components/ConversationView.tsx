/**
 * ConversationView - Interactive conversation with AI tutor
 */
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '@kapp/core';
import ConversationMessage from './ConversationMessage';
import type { Message } from './ConversationMessage';
import './ConversationView.css';

interface Props {
  onBack: () => void;
}

export default function ConversationView({ onBack }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [userLevel, setUserLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [audioLoadingId] = useState<string | null>(null);
  const [translateLoadingId, setTranslateLoadingId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch user level on mount (estimate from completion percentage)
  useEffect(() => {
    const fetchUserLevel = async () => {
      try {
        const progress = await apiClient.getProgress();
        if (progress.courses && progress.courses.length > 0) {
          const percentage = progress.courses[0]?.percentage || 0;
          setUserLevel(Math.floor(percentage / 20));
        }
      } catch (err) {
        console.error('Failed to fetch user level:', err);
      }
    };

    fetchUserLevel();
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const generateAudioForMessage = async (text: string): Promise<string> => {
    try {
      const { filename } = await apiClient.generateAudio(text);
      return apiClient.getAudioUrl(filename);
    } catch (err) {
      console.error('Failed to generate audio:', err);
      return '';
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    const userMessageObj: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessageObj]);
    setLoading(true);

    try {
      // Prepare conversation history (last 5 exchanges for context)
      const recentMessages = messages.slice(-10);
      const conversationHistory: Array<{ user: string; assistant: string }> = [];
      let current: { user?: string; assistant?: string } = {};

      recentMessages.forEach((msg) => {
        if (msg.role === 'user') {
          if (current.user || current.assistant) {
            if (current.user && current.assistant) {
              conversationHistory.push({ user: current.user, assistant: current.assistant });
            }
            current = {};
          }
          current.user = msg.content;
        } else if (msg.role === 'assistant') {
          current.assistant = msg.content;
          if (current.user && current.assistant) {
            conversationHistory.push({ user: current.user, assistant: current.assistant });
            current = {};
          }
        }
      });

      const response = await apiClient.sendConversationMessage(userMessage, {
        level: userLevel,
        conversation_history: conversationHistory,
      });

      const assistantId = `assistant-${Date.now()}`;

      // Add assistant response (audio will be generated on-demand or eagerly)
      const assistantMessage: Message = {
        id: assistantId,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Eagerly generate audio in background
      generateAudioForMessage(response.response).then((audioUrl) => {
        if (audioUrl) {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, audioUrl } : m))
          );
        }
      });
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handlePlayAudio = async (audioUrl: string) => {
    if (!audioUrl) return;
    try {
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (err) {
      console.error('Audio playback failed:', err);
    }
  };

  const handleTranslate = async (messageId: string) => {
    const msg = messages.find((m) => m.id === messageId);
    if (!msg || msg.translation) return;

    setTranslateLoadingId(messageId);
    try {
      const { translation } = await apiClient.translateText(msg.content);
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, translation } : m))
      );
    } catch (err) {
      console.error('Failed to translate:', err);
    } finally {
      setTranslateLoadingId(null);
    }
  };

  return (
    <div className="conversation-view">
      <header className="conversation-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h1>Practice Conversation</h1>
        <p className="subtitle">Chat with your AI Korean tutor</p>
      </header>

      <div className="conversation-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>안녕하세요! (Welcome!)</h2>
              <p>
                Let's practice Korean together. Feel free to ask about anything you'd like to
                learn!
              </p>
              <div className="suggestions">
                <p>Try starting with:</p>
                <ul>
                  <li>"I want to learn about food"</li>
                  <li>"Tell me about Korean culture"</li>
                  <li>"Let's talk about hobbies"</li>
                </ul>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ConversationMessage
              key={message.id}
              message={message}
              onPlayAudio={handlePlayAudio}
              onTranslate={handleTranslate}
              audioLoading={audioLoadingId === message.id}
              translateLoading={translateLoadingId === message.id}
            />
          ))}

          {loading && (
            <div className="message-group assistant">
              <div className="thinking-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <p className="thinking-text">AI is thinking...</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
          </div>
        )}

        <div className="input-section">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message in English or Korean..."
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
      </div>
    </div>
  );
}
