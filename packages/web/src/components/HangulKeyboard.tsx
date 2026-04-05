/**
 * HangulKeyboard — virtual dubeolsik (2-set) Korean keyboard
 * Handles jamo composition via HangulComposer.
 */
import { useRef, useState, useEffect, useCallback } from 'react';
import { HangulComposer } from '../utils/hangulComposer';
import './HangulKeyboard.css';

interface Props {
  text: string;
  onTextChange: (newText: string) => void;
  visible: boolean;
}

// Standard dubeolsik layout rows [normal, shifted]
const ROWS: [string[], string[]][] = [
  [
    ['ㅂ', 'ㅈ', 'ㄷ', 'ㄱ', 'ㅅ', 'ㅛ', 'ㅕ', 'ㅑ', 'ㅐ', 'ㅔ'],
    ['ㅃ', 'ㅉ', 'ㄸ', 'ㄲ', 'ㅆ', 'ㅛ', 'ㅕ', 'ㅑ', 'ㅒ', 'ㅖ'],
  ],
  [
    ['ㅁ', 'ㄴ', 'ㅇ', 'ㄹ', 'ㅎ', 'ㅗ', 'ㅓ', 'ㅏ', 'ㅣ'],
    ['ㅁ', 'ㄴ', 'ㅇ', 'ㄹ', 'ㅎ', 'ㅗ', 'ㅓ', 'ㅏ', 'ㅣ'],
  ],
  [
    ['ㅋ', 'ㅌ', 'ㅊ', 'ㅍ', 'ㅠ', 'ㅜ', 'ㅡ'],
    ['ㅋ', 'ㅌ', 'ㅊ', 'ㅍ', 'ㅠ', 'ㅜ', 'ㅡ'],
  ],
];

export default function HangulKeyboard({ text, onTextChange, visible }: Props) {
  const composerRef = useRef(new HangulComposer());
  const [shifted, setShifted] = useState(false);
  const [pressedKey, setPressedKey] = useState<string | null>(null);

  // When keyboard becomes visible, sync composer with current text
  useEffect(() => {
    if (visible) {
      composerRef.current.setText(text);
    }
  }, [visible]); // intentionally not including `text` — only sync on open

  const handleKey = useCallback((jamo: string) => {
    setPressedKey(jamo);
    setTimeout(() => setPressedKey(null), 150);
    const result = composerRef.current.inputJamo(jamo);
    onTextChange(result);
    // Auto-release shift after a consonant input (dubeolsik convention)
    if (shifted && !['ㅛ', 'ㅕ', 'ㅑ', 'ㅐ', 'ㅔ', 'ㅗ', 'ㅓ', 'ㅏ', 'ㅣ', 'ㅠ', 'ㅜ', 'ㅡ', 'ㅒ', 'ㅖ'].includes(jamo)) {
      setShifted(false);
    }
  }, [shifted, onTextChange]);

  const handleSpace = useCallback(() => {
    const result = composerRef.current.inputJamo(' ');
    onTextChange(result);
  }, [onTextChange]);

  const handleBackspace = useCallback(() => {
    setPressedKey('⌫');
    setTimeout(() => setPressedKey(null), 150);
    const result = composerRef.current.backspace();
    onTextChange(result);
  }, [onTextChange]);

  if (!visible) return null;

  return (
    <div className="hangul-keyboard" onMouseDown={(e) => e.preventDefault()}>
      <div className="hangul-keyboard-rows">
        {/* Rows 0 and 1 */}
        {ROWS.map((rowPair, rowIdx) => {
          const keys = shifted ? rowPair[1] : rowPair[0];
          return (
            <div key={rowIdx} className="hangul-row">
              {rowIdx === 2 && (
                <button
                  className={`hangul-key shift-key${shifted ? ' active' : ''}`}
                  onMouseDown={(e) => { e.preventDefault(); setShifted(s => !s); }}
                  onTouchStart={(e) => { e.preventDefault(); setShifted(s => !s); }}
                  aria-label="Shift"
                >
                  ⇧
                </button>
              )}
              {keys.map((jamo) => (
                <button
                  key={jamo}
                  className={`hangul-key${pressedKey === jamo ? ' pressed' : ''}`}
                  onMouseDown={(e) => { e.preventDefault(); handleKey(jamo); }}
                  onTouchStart={(e) => { e.preventDefault(); handleKey(jamo); }}
                >
                  {jamo}
                </button>
              ))}
              {rowIdx === 2 && (
                <button
                  className={`hangul-key backspace-key${pressedKey === '⌫' ? ' pressed' : ''}`}
                  onMouseDown={(e) => { e.preventDefault(); handleBackspace(); }}
                  onTouchStart={(e) => { e.preventDefault(); handleBackspace(); }}
                  aria-label="Backspace"
                >
                  ⌫
                </button>
              )}
            </div>
          );
        })}

        {/* Space row */}
        <div className="hangul-row">
          <button
            className="hangul-key space-key"
            onMouseDown={(e) => { e.preventDefault(); handleSpace(); }}
            onTouchStart={(e) => { e.preventDefault(); handleSpace(); }}
            aria-label="Space"
          >
            SPACE
          </button>
        </div>
      </div>
    </div>
  );
}
