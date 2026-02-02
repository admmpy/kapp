/**
 * @kapp/core - Shared code for Kapp Korean Learning App
 * Re-exports all types, API clients, and utilities
 */

// Types
export * from './types';

// Config
export { API_BASE_URL } from './config';

// API clients
export { apiClient, default as APIClient } from './api/client';
export { llmClient, default as LLMClient } from './api/llm';

// Storage (for PWA offline support)
export * from './storage/indexedDB';
export * from './storage/syncManager';
