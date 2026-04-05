/**
 * HangulComposer - Dubeolsik (2-set) Korean input composition engine
 * Converts individual jamo keystrokes into composed syllable blocks.
 *
 * Unicode formula: 0xAC00 + (choIdx * 21 + jungIdx) * 28 + jongIdx
 */

// Choseong (initial consonants), indices 0-18
const CHOSEONG = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];

// Jungseong (vowels/medials), indices 0-20
const JUNGSEONG = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'];

// Jongseong (final consonants), index 0 = none
const JONGSEONG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];

// Compound vowels: "baseJungIdx:addedJamo" → compound jung index
const COMPOUND_VOWELS: Record<string, number> = {
  '8:ㅏ': 9,   // ㅗ + ㅏ = ㅘ
  '8:ㅐ': 10,  // ㅗ + ㅐ = ㅙ
  '8:ㅣ': 11,  // ㅗ + ㅣ = ㅚ
  '13:ㅓ': 14, // ㅜ + ㅓ = ㅝ
  '13:ㅔ': 15, // ㅜ + ㅔ = ㅞ
  '13:ㅣ': 16, // ㅜ + ㅣ = ㅟ
  '18:ㅣ': 19, // ㅡ + ㅣ = ㅢ
};

// Decompose compound vowels: jung index → [base jamo, added jamo]
const VOWEL_DECOMPOSE: Record<number, [string, string]> = {
  9: ['ㅗ', 'ㅏ'],
  10: ['ㅗ', 'ㅐ'],
  11: ['ㅗ', 'ㅣ'],
  14: ['ㅜ', 'ㅓ'],
  15: ['ㅜ', 'ㅔ'],
  16: ['ㅜ', 'ㅣ'],
  19: ['ㅡ', 'ㅣ'],
};

// Compound finals: "baseJongIdx:addedJamo" → compound jong index
const COMPOUND_FINALS: Record<string, number> = {
  '1:ㅅ': 3,   // ㄱ + ㅅ = ㄳ
  '4:ㅈ': 5,   // ㄴ + ㅈ = ㄵ
  '4:ㅎ': 6,   // ㄴ + ㅎ = ㄶ
  '8:ㄱ': 9,   // ㄹ + ㄱ = ㄺ
  '8:ㅁ': 10,  // ㄹ + ㅁ = ㄻ
  '8:ㅂ': 11,  // ㄹ + ㅂ = ㄼ
  '8:ㅅ': 12,  // ㄹ + ㅅ = ㄽ
  '8:ㅌ': 13,  // ㄹ + ㅌ = ㄾ
  '8:ㅍ': 14,  // ㄹ + ㅍ = ㄿ
  '8:ㅎ': 15,  // ㄹ + ㅎ = ㅀ
  '17:ㅅ': 18, // ㅂ + ㅅ = ㅄ
};

// Decompose compound finals: jong index → [first jamo, second jamo]
const FINAL_DECOMPOSE: Record<number, [string, string]> = {
  3: ['ㄱ', 'ㅅ'],
  5: ['ㄴ', 'ㅈ'],
  6: ['ㄴ', 'ㅎ'],
  9: ['ㄹ', 'ㄱ'],
  10: ['ㄹ', 'ㅁ'],
  11: ['ㄹ', 'ㅂ'],
  12: ['ㄹ', 'ㅅ'],
  13: ['ㄹ', 'ㅌ'],
  14: ['ㄹ', 'ㅍ'],
  15: ['ㄹ', 'ㅎ'],
  18: ['ㅂ', 'ㅅ'],
};

const CHOSEONG_MAP: Record<string, number> = Object.fromEntries(CHOSEONG.map((c, i) => [c, i]));
const JUNGSEONG_MAP: Record<string, number> = Object.fromEntries(JUNGSEONG.map((v, i) => [v, i]));

// Consonants that can appear as jongseong (final) → jong index
const JONGSEONG_SIMPLE_MAP: Record<string, number> = {
  'ㄱ': 1, 'ㄲ': 2, 'ㄴ': 4, 'ㄷ': 7, 'ㄹ': 8,
  'ㅁ': 16, 'ㅂ': 17, 'ㅅ': 19, 'ㅆ': 20,
  'ㅇ': 21, 'ㅈ': 22, 'ㅊ': 23, 'ㅋ': 24, 'ㅌ': 25, 'ㅍ': 26, 'ㅎ': 27,
};

type State = 'none' | 'cho' | 'jung' | 'jong';

function makeSyllable(cho: number, jung: number, jong: number): string {
  return String.fromCharCode(0xAC00 + (cho * 21 + jung) * 28 + jong);
}

export class HangulComposer {
  private committed = '';
  private state: State = 'none';
  private choIdx = -1;
  private jungIdx = -1;
  private jongIdx = 0;

  private getComposing(): string {
    switch (this.state) {
      case 'none': return '';
      case 'cho': return CHOSEONG[this.choIdx];
      case 'jung': return makeSyllable(this.choIdx, this.jungIdx, 0);
      case 'jong': return makeSyllable(this.choIdx, this.jungIdx, this.jongIdx);
    }
  }

  getText(): string {
    return this.committed + this.getComposing();
  }

  inputJamo(jamo: string): string {
    const isVowel = jamo in JUNGSEONG_MAP;
    const isConsonant = jamo in CHOSEONG_MAP;

    if (isVowel) {
      const vIdx = JUNGSEONG_MAP[jamo];
      switch (this.state) {
        case 'none':
          // Vowel alone → silent ㅇ as choseong
          this.choIdx = CHOSEONG_MAP['ㅇ'];
          this.jungIdx = vIdx;
          this.state = 'jung';
          break;
        case 'cho':
          this.jungIdx = vIdx;
          this.state = 'jung';
          break;
        case 'jung': {
          const key = `${this.jungIdx}:${jamo}`;
          if (key in COMPOUND_VOWELS) {
            this.jungIdx = COMPOUND_VOWELS[key];
          } else {
            this.committed += makeSyllable(this.choIdx, this.jungIdx, 0);
            this.choIdx = CHOSEONG_MAP['ㅇ'];
            this.jungIdx = vIdx;
          }
          break;
        }
        case 'jong': {
          if (this.jongIdx in FINAL_DECOMPOSE) {
            // Compound final splits: first stays, second becomes next choseong
            const [firstJamo, secondJamo] = FINAL_DECOMPOSE[this.jongIdx];
            const firstJong = JONGSEONG.indexOf(firstJamo);
            this.committed += makeSyllable(this.choIdx, this.jungIdx, firstJong);
            this.choIdx = CHOSEONG_MAP[secondJamo];
          } else {
            // Simple final moves to next choseong
            const jongJamo = JONGSEONG[this.jongIdx];
            this.committed += makeSyllable(this.choIdx, this.jungIdx, 0);
            this.choIdx = CHOSEONG_MAP[jongJamo];
          }
          this.jungIdx = vIdx;
          this.jongIdx = 0;
          this.state = 'jung';
          break;
        }
      }
    } else if (isConsonant) {
      switch (this.state) {
        case 'none':
          this.choIdx = CHOSEONG_MAP[jamo];
          this.state = 'cho';
          break;
        case 'cho':
          // Two consonants: commit first, start new
          this.committed += CHOSEONG[this.choIdx];
          this.choIdx = CHOSEONG_MAP[jamo];
          break;
        case 'jung':
          if (jamo in JONGSEONG_SIMPLE_MAP) {
            this.jongIdx = JONGSEONG_SIMPLE_MAP[jamo];
            this.state = 'jong';
          } else {
            // Cannot be jongseong (ㄸ, ㅃ, ㅉ) → commit, start new cho
            this.committed += makeSyllable(this.choIdx, this.jungIdx, 0);
            this.choIdx = CHOSEONG_MAP[jamo];
            this.state = 'cho';
          }
          break;
        case 'jong': {
          const key = `${this.jongIdx}:${jamo}`;
          if (key in COMPOUND_FINALS) {
            this.jongIdx = COMPOUND_FINALS[key];
          } else {
            this.committed += makeSyllable(this.choIdx, this.jungIdx, this.jongIdx);
            this.choIdx = CHOSEONG_MAP[jamo];
            this.jongIdx = 0;
            this.state = 'cho';
          }
          break;
        }
      }
    } else {
      // Non-jamo (space, punctuation) → commit composing + character
      this.committed += this.getComposing() + jamo;
      this.state = 'none';
      this.choIdx = -1;
      this.jungIdx = -1;
      this.jongIdx = 0;
    }

    return this.getText();
  }

  backspace(): string {
    switch (this.state) {
      case 'none':
        if (this.committed.length > 0) {
          this.committed = this.committed.slice(0, -1);
        }
        break;
      case 'cho':
        this.state = 'none';
        this.choIdx = -1;
        break;
      case 'jung':
        if (this.jungIdx in VOWEL_DECOMPOSE) {
          // Compound vowel → revert to first component
          const [firstVowel] = VOWEL_DECOMPOSE[this.jungIdx];
          this.jungIdx = JUNGSEONG_MAP[firstVowel];
        } else {
          this.state = 'cho';
          this.jungIdx = -1;
        }
        break;
      case 'jong':
        if (this.jongIdx in FINAL_DECOMPOSE) {
          // Compound final → revert to first component
          const [firstJamo] = FINAL_DECOMPOSE[this.jongIdx];
          this.jongIdx = JONGSEONG.indexOf(firstJamo);
        } else {
          this.state = 'jung';
          this.jongIdx = 0;
        }
        break;
    }
    return this.getText();
  }

  reset() {
    this.committed = '';
    this.state = 'none';
    this.choIdx = -1;
    this.jungIdx = -1;
    this.jongIdx = 0;
  }

  /** Initialize composer with pre-existing text (treated as committed) */
  setText(text: string) {
    this.committed = text;
    this.state = 'none';
    this.choIdx = -1;
    this.jungIdx = -1;
    this.jongIdx = 0;
  }
}
