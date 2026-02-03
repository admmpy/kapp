/**
 * API client for communicating with the Flask backend v2.0
 * Lesson-based architecture
 */
import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  Course,
  Unit,
  Lesson,
  LessonSummary,
  ExerciseResult,
  OverallProgress,
  RecentActivity,
  LearningStats,
  VocabularyItem,
  VocabularyCategory,
  CoursesResponse,
  CourseDetailResponse,
  UnitLessonsResponse,
  LessonDetailResponse,
  ProgressResponse,
  RecentActivityResponse,
  StatsResponse,
  VocabularyListResponse,
  VocabularyCategoriesResponse,
  VocabularyDueResponse,
  VocabularyReviewResponse,
  LLMHealth,
} from '../types';

import { API_BASE_URL } from '../config';

// Re-export for backward compatibility
export { API_BASE_URL };

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL ? `${API_BASE_URL}/api` : '/api',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 seconds
    });

    // Add interceptor to log requests
    this.client.interceptors.request.use((config) => {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
      return config;
    });
  }

  // ============================================
  // Health check
  // ============================================

  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ============================================
  // Course endpoints
  // ============================================

  async getCourses(): Promise<Course[]> {
    const response = await this.client.get<CoursesResponse>('/courses');
    const courses = response.data?.courses;
    if (!Array.isArray(courses)) {
      throw new Error('Invalid courses response');
    }
    return courses;
  }

  async getCourse(courseId: number): Promise<Course & { units: Unit[] }> {
    const response = await this.client.get<CourseDetailResponse>(`/courses/${courseId}`);
    return response.data.course;
  }

  async getUnit(unitId: number): Promise<Unit> {
    const response = await this.client.get<{ unit: Unit }>(`/units/${unitId}`);
    return response.data.unit;
  }

  async getUnitLessons(unitId: number): Promise<{ unit: { id: number; title: string }; lessons: LessonSummary[] }> {
    const response = await this.client.get<UnitLessonsResponse>(`/units/${unitId}/lessons`);
    return response.data;
  }

  // ============================================
  // Lesson endpoints
  // ============================================

  async getLesson(lessonId: number): Promise<Lesson> {
    const response = await this.client.get<LessonDetailResponse>(`/lessons/${lessonId}`);
    return response.data.lesson;
  }

  async startLesson(lessonId: number): Promise<{ success: boolean; progress: { is_started: boolean; started_at: string } }> {
    const response = await this.client.post(`/lessons/${lessonId}/start`);
    return response.data;
  }

  async completeLesson(lessonId: number, data: { score?: number; time_spent_seconds?: number }): Promise<{ success: boolean; progress: { is_completed: boolean; completed_at: string; score?: number } }> {
    const response = await this.client.post(`/lessons/${lessonId}/complete`, data);
    return response.data;
  }

  async getNextLesson(lessonId: number): Promise<{
    next_lesson: {
      id: number;
      title: string;
      description?: string;
      unit_id: number;
      estimated_minutes: number;
      exercise_count: number;
    } | null;
    is_last_in_unit: boolean;
    is_last_in_course: boolean;
  }> {
    const response = await this.client.get(`/lessons/${lessonId}/next`);
    return response.data;
  }

  async submitExercise(exerciseId: number, answer: string): Promise<ExerciseResult> {
    const response = await this.client.post<ExerciseResult>(`/exercises/${exerciseId}/submit`, { answer });
    return response.data;
  }

  // ============================================
  // Progress endpoints
  // ============================================

  async getProgress(): Promise<OverallProgress> {
    const response = await this.client.get<ProgressResponse>('/progress');
    const progress = response.data?.progress;
    if (!progress || typeof progress !== 'object') {
      throw new Error('Invalid progress response');
    }
    return progress;
  }

  async getRecentActivity(): Promise<RecentActivity[]> {
    const response = await this.client.get<RecentActivityResponse>('/progress/recent');
    return response.data.recent_activity;
  }

  async getStats(): Promise<LearningStats> {
    const response = await this.client.get<StatsResponse>('/progress/stats');
    return response.data.stats;
  }

  async submitProgress(lessonId: string, data: { completed: boolean; score: number }): Promise<{ success: boolean }> {
    const response = await this.client.post(`/progress/${lessonId}`, data);
    return response.data;
  }

  // ============================================
  // Vocabulary endpoints
  // ============================================

  async getVocabulary(params?: {
    category?: string;
    difficulty?: number;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ vocabulary: VocabularyItem[]; total: number; limit: number; offset: number }> {
    const response = await this.client.get<VocabularyListResponse>('/vocabulary', { params });
    return response.data;
  }

  async getVocabularyItem(itemId: number): Promise<VocabularyItem> {
    const response = await this.client.get<{ item: VocabularyItem }>(`/vocabulary/${itemId}`);
    return response.data.item;
  }

  async getVocabularyCategories(): Promise<VocabularyCategory[]> {
    const response = await this.client.get<VocabularyCategoriesResponse>('/vocabulary/categories');
    return response.data.categories;
  }

  async recordVocabularyPractice(itemId: number, correct: boolean): Promise<{ success: boolean; times_practiced: number; times_correct: number; accuracy_rate?: number }> {
    const response = await this.client.post(`/vocabulary/${itemId}/practice`, { correct });
    return response.data;
  }

  // ============================================
  // Spaced Repetition endpoints
  // ============================================

  async getVocabularyDue(limit?: number): Promise<{ vocabulary: VocabularyItem[]; total_due: number; new_items: number }> {
    const response = await this.client.get<VocabularyDueResponse>('/vocabulary/due', {
      params: { limit }
    });
    return response.data;
  }

  async recordVocabularyReview(itemId: number, quality: number): Promise<VocabularyReviewResponse> {
    const response = await this.client.post<VocabularyReviewResponse>(`/vocabulary/${itemId}/review`, { quality });
    return response.data;
  }

  // ============================================
  // Audio endpoint helper
  // ============================================

  getAudioUrl(filename: string): string {
    return `${API_BASE_URL}/api/audio/${filename}`;
  }

  // ============================================
  // LLM endpoints
  // ============================================

  async getLLMHealth(): Promise<LLMHealth> {
    const response = await this.client.get('/llm/health');
    return response.data;
  }

  async getLLMExplanation(vocabId: number, context?: { level?: number }): Promise<{ explanation: string; generated_at: string }> {
    const response = await this.client.post('/llm/explain', {
      vocab_id: vocabId,
      user_context: context
    }, {
      timeout: 90000  // 90 seconds for LLM requests
    });
    return response.data;
  }

  async getLLMExerciseExplanation(exerciseId: number, context?: { level?: number }): Promise<{ explanation: string; generated_at: string }> {
    const response = await this.client.post('/llm/explain-exercise', {
      exercise_id: exerciseId,
      user_context: context
    }, {
      timeout: 90000
    });
    return response.data;
  }

  // ============================================
  // LLM availability check (for mobile PWA)
  // ============================================

  async checkLLMAvailable(): Promise<boolean> {
    try {
      const health = await this.getLLMHealth();
      return health.available && health.status === 'ok';
    } catch {
      return false; // Expected on mobile
    }
  }

  // ============================================
  // Conversation endpoints
  // ============================================

  async sendConversationMessage(
    message: string,
    context?: { level?: number; conversation_history?: Array<{ user: string; assistant: string }> }
  ): Promise<{ response: string; timestamp: string }> {
    const response = await this.client.post('/llm/conversation', {
      message,
      context
    }, {
      timeout: 90000  // 90 seconds for LLM requests
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
