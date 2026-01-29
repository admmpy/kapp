/**
 * ConversationView - Interactive conversation with AI tutor
 */
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '@kapp/core';
import ConversationMessage from './ConversationMessage';
import './ConversationView.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  audioUrl?: string;
}

interface Props {
  onBack: () => void;
}

export default function ConversationView({ onBack }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [userLevel, setUserLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch user level on mount (estimate from completion percentage)
  useEffect(() => {
    const fetchUserLevel = async () => {
      try {
        const progress = await apiClient.getProgress();
        if (progress.courses && progress.courses.length > 0) {
          // Estimate level from completion percentage (0-100% → 0-5 level)
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

  const generateAudioUrl = async (text: string): Promise<string> => {
    try {
      // Try to generate audio using the backend TTS endpoint
      // The endpoint should be at /api/audio/text-to-speech or similar
      // For now, we'll use a placeholder that will be implemented
      const filename = encodeURIComponent(text.substring(0, 50)) + `.mp3`;
      return apiClient.getAudioUrl(filename);
    } catch (err) {
      console.error('Failed to generate audio URL:', err);
      return '';
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    // Add user message to conversation
    const userMessageObj: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessageObj]);
    setLoading(true);

    try {
      // Prepare conversation history (last 5 exchanges for context)
      const conversationHistory = messages
        .slice(-10) // Last 10 messages (5 exchanges)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));

      const response = await apiClient.sendConversationMessage(userMessage, {
        level: userLevel,
        conversation_history: conversationHistory
      });

      // Generate audio URL for AI response
      const audioUrl = await generateAudioUrl(response.response);

      // Add assistant response to conversation
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        audioUrl
      };

      setMessages(prev => [...prev, assistantMessage]);
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

  const handlePlayAudio = (audioUrl: string) => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play().catch(err => console.error('Audio playback failed:', err));
    }
  };

  return (
    <div className="conversation-view">
      <header className="conversation-header">
        <button className="back-button" onClick={onBack}>← Back</button>
        <h1>Practice Conversation</h1>
        <p className="subtitle">Chat with your AI Korean tutor</p>
      </header>

      <div className="conversation-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>안녕하세요! (Welcome!)</h2>
              <p>Let's practice Korean together. Feel free to ask about anything you'd like to learn!</p>
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
