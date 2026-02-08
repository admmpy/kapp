/**
 * Application configuration
 * Platform-agnostic - works in both web (Vite) and other environments
 */

// Use type assertion to access Vite's import.meta.env
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const env = (import.meta as any).env || {};

export const API_BASE_URL: string = env.VITE_API_URL || '';

// Feature flags
export const PRONUNCIATION_SELF_CHECK_ENABLED: boolean = env.VITE_PRONUNCIATION_SELF_CHECK_ENABLED === 'true';
export const SPEAKING_FIRST_ENABLED: boolean = env.VITE_SPEAKING_FIRST_ENABLED !== 'false';
export const GRAMMAR_MASTERY_ENABLED: boolean = env.VITE_GRAMMAR_MASTERY_ENABLED === 'true';
export const WEAKNESS_REVIEW_ENABLED: boolean = env.VITE_WEAKNESS_REVIEW_ENABLED === 'true';
export const SENTENCE_SRS_ENABLED: boolean = env.VITE_SENTENCE_SRS_ENABLED === 'true';
export const IMMERSION_MODE_ENABLED: boolean = env.VITE_IMMERSION_MODE_ENABLED === 'true';
