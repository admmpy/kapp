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

    for (const item of unsyncedItems as Array<{ type: string; data: { lessonId: string; completed: boolean; score: number } }>) {
      try {
        if (item.type === 'progress') {
          // Sync progress to server
          await apiClient.submitProgress(item.data.lessonId, {
            completed: item.data.completed,
            score: item.data.score
          });
          await markProgressSynced(item.data.lessonId);
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
