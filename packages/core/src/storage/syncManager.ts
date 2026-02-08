/**
 * Sync Manager - Handles offline/online synchronization
 */

import { getUnsyncedItems, clearSyncQueue, markProgressSynced } from './indexedDB';
import { apiClient } from '../api/client';

let syncInProgress = false;

export async function syncOfflineChanges(): Promise<{ synced: number; failed: number }> {
  if (syncInProgress) {
    return { synced: 0, failed: 0 };
  }

  if (!navigator.onLine) {
    return { synced: 0, failed: 0 };
  }

  syncInProgress = true;
  let synced = 0;
  let failed = 0;

  try {
    const unsyncedItems = await getUnsyncedItems();

    for (const item of unsyncedItems as Array<{ type: string; data: Record<string, unknown> }>) {
      try {
        if (item.type === 'progress') {
          const data = item.data as { lessonId: string; completed: boolean; score: number };
          await apiClient.submitProgress(data.lessonId, {
            completed: data.completed,
            score: data.score
          });
          await markProgressSynced(data.lessonId);
          synced++;
        } else if (item.type === 'grammar_mastery') {
          const data = item.data as { exerciseId: number; answer: string };
          await apiClient.submitExercise(data.exerciseId, data.answer);
          synced++;
        }
      } catch (error) {
        console.error('Failed to sync item:', error);
        failed++;
      }
    }

    // Clear successfully synced items
    if (synced > 0 && failed === 0) {
      await clearSyncQueue();
    }
  } finally {
    syncInProgress = false;
  }

  return { synced, failed };
}

export function setupOnlineListener(): () => void {
  const handleOnline = () => {
    console.log('Back online - syncing changes...');
    syncOfflineChanges().then(({ synced, failed }) => {
      if (synced > 0) {
        console.log(`Synced ${synced} items`);
      }
      if (failed > 0) {
        console.warn(`Failed to sync ${failed} items`);
      }
    });
  };

  window.addEventListener('online', handleOnline);

  // Return cleanup function
  return () => {
    window.removeEventListener('online', handleOnline);
  };
}

export function isOnline(): boolean {
  return navigator.onLine;
}
