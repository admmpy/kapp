/**
 * IndexedDB storage for offline support
 */

import type { PronunciationSelfCheck } from '../types';

const DB_NAME = 'kapp-offline';
const DB_VERSION = 2;

interface ProgressRecord {
  lessonId: string;
  completed: boolean;
  score: number;
  timestamp: number;
  synced: boolean;
}

interface LessonCache {
  id: string;
  data: unknown;
  cachedAt: number;
}

let db: IDBDatabase | null = null;

export async function initDB(): Promise<IDBDatabase> {
  if (db) return db;

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);

    request.onsuccess = () => {
      db = request.result;
      resolve(db);
    };

    request.onupgradeneeded = (event) => {
      const database = (event.target as IDBOpenDBRequest).result;
      const oldVersion = event.oldVersion;

      if (oldVersion < 1) {
        // Progress store - tracks lesson completion
        const progressStore = database.createObjectStore('progress', { keyPath: 'lessonId' });
        progressStore.createIndex('synced', 'synced', { unique: false });
        progressStore.createIndex('timestamp', 'timestamp', { unique: false });

        // Lessons cache - stores lesson data for offline use
        const lessonsStore = database.createObjectStore('lessons', { keyPath: 'id' });
        lessonsStore.createIndex('cachedAt', 'cachedAt', { unique: false });

        // Sync queue - tracks changes to sync when online
        database.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
      }

      if (oldVersion < 2) {
        // Pronunciation self-check store
        const pronStore = database.createObjectStore('pronunciation_checks', {
          keyPath: 'id',
          autoIncrement: true,
        });
        pronStore.createIndex('exerciseId', 'exerciseId', { unique: false });
        pronStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
}

export async function saveProgress(lessonId: string, completed: boolean, score: number): Promise<void> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction(['progress', 'syncQueue'], 'readwrite');
    const progressStore = transaction.objectStore('progress');
    const syncStore = transaction.objectStore('syncQueue');

    const record: ProgressRecord = {
      lessonId,
      completed,
      score,
      timestamp: Date.now(),
      synced: navigator.onLine ? true : false
    };

    progressStore.put(record);

    // If offline, add to sync queue
    if (!navigator.onLine) {
      syncStore.add({
        type: 'progress',
        data: record,
        createdAt: Date.now()
      });
    }

    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function getProgress(lessonId: string): Promise<ProgressRecord | null> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('progress', 'readonly');
    const store = transaction.objectStore('progress');
    const request = store.get(lessonId);

    request.onsuccess = () => resolve(request.result || null);
    request.onerror = () => reject(request.error);
  });
}

export async function getAllProgress(): Promise<ProgressRecord[]> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('progress', 'readonly');
    const store = transaction.objectStore('progress');
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function cacheLesson(id: string, data: unknown): Promise<void> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('lessons', 'readwrite');
    const store = transaction.objectStore('lessons');

    const record: LessonCache = {
      id,
      data,
      cachedAt: Date.now()
    };

    store.put(record);

    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function getCachedLesson(id: string): Promise<unknown | null> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('lessons', 'readonly');
    const store = transaction.objectStore('lessons');
    const request = store.get(id);

    request.onsuccess = () => {
      const result = request.result as LessonCache | undefined;
      resolve(result?.data || null);
    };
    request.onerror = () => reject(request.error);
  });
}

export async function getUnsyncedItems(): Promise<unknown[]> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('syncQueue', 'readonly');
    const store = transaction.objectStore('syncQueue');
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function clearSyncQueue(): Promise<void> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('syncQueue', 'readwrite');
    const store = transaction.objectStore('syncQueue');
    store.clear();

    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function markProgressSynced(lessonId: string): Promise<void> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('progress', 'readwrite');
    const store = transaction.objectStore('progress');
    const request = store.get(lessonId);

    request.onsuccess = () => {
      const record = request.result as ProgressRecord;
      if (record) {
        record.synced = true;
        store.put(record);
      }
    };

    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}

export async function savePronunciationCheck(check: PronunciationSelfCheck): Promise<void> {
  const database = await initDB();

  return new Promise((resolve, reject) => {
    const transaction = database.transaction('pronunciation_checks', 'readwrite');
    const store = transaction.objectStore('pronunciation_checks');

    store.add(check);

    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
}
