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
    return response.data.courses;
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

  async submitExercise(exerciseId: number, answer: string): Promise<ExerciseResult> {
    const response = await this.client.post<ExerciseResult>(`/exercises/${exerciseId}/submit`, { answer });
    return response.data;
  }

  // ============================================
  // Progress endpoints
  // ============================================

  async getProgress(): Promise<OverallProgress> {
    const response = await this.client.get<ProgressResponse>('/progress');
    return response.data.progress;
  }

  async getRecentActivity(): Promise<RecentActivity[]> {
    const response = await this.client.get<RecentActivityResponse>('/progress/recent');
    return response.data.recent_activity;
  }

  async getStats(): Promise<LearningStats> {
    const response = await this.client.get<StatsResponse>('/progress/stats');
    return response.data.stats;
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

  async getLLMExplanation(lessonId: number, context?: { level?: number }): Promise<{ explanation: string; generated_at: string }> {
    const response = await this.client.post('/llm/explain', {
      lesson_id: lessonId,
      user_context: context
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
    context?: { level?: number; conversation_history?: Array<{ role: string; content: string }> }
  ): Promise<{ response: string; timestamp: string }> {
    const response = await this.client.post('/llm/conversation', {
      message,
      user_context: context
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
