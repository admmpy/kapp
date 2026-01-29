/**
 * Application configuration
 * Platform-agnostic - works in both web (Vite) and other environments
 */

// Use type assertion to access Vite's import.meta.env
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const env = (import.meta as any).env || {};

export const API_BASE_URL: string = env.VITE_API_URL || '';
