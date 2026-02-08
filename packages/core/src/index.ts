/**
 * @kapp/core - Shared code for Kapp Korean Learning App
 * Re-exports all types, API clients, and utilities
 */

// Types
export * from './types';

// Config
export {
  API_BASE_URL,
  PRONUNCIATION_SELF_CHECK_ENABLED,
  SPEAKING_FIRST_ENABLED,
  GRAMMAR_MASTERY_ENABLED,
} from './config';

// API clients
export { apiClient, default as APIClient } from './api/client';

// Storage (for PWA offline support)
export * from './storage/indexedDB';
export * from './storage/syncManager';
