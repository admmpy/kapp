/**
 * TypeScript type definitions for the Korean Learning App v2.0
 * Lesson-based architecture
 */

// ============================================
// Course & Lesson Types
// ============================================

export interface Course {
  id: number;
  title: string;
  description?: string;
  language: string;
  level: string;
  unit_count: number;
  total_lessons: number;
  image_url?: string;
}

export interface Unit {
  id: number;
  title: string;
  description?: string;
  course_id?: number;
  lesson_count: number;
  display_order: number;
  is_locked: boolean;
}

export interface Lesson {
  id: number;
  title: string;
  description?: string;
  grammar_explanation?: string;
  grammar_tip?: string;
  estimated_minutes: number;
  unit_id: number;
  exercise_count: number;
  exercises?: Exercise[];
  progress?: LessonProgress;
  grammar_patterns?: GrammarPattern[];
}

export interface LessonSummary {
  id: number;
  title: string;
  description?: string;
  estimated_minutes: number;
  exercise_count: number;
  display_order: number;
  is_locked: boolean;
  is_started: boolean;
  is_completed: boolean;
  score?: number;
}

// ============================================
// Exercise Types
// ============================================

export type ExerciseType = 'vocabulary' | 'grammar' | 'reading' | 'listening' | 'writing' | 'review' | 'sentence_arrange';

export interface SentenceTile {
  korean: string;
  romanization: string;
  id: number;
  audio_url?: string;
}

export interface Exercise {
  id: number;
  exercise_type: ExerciseType;
  question: string;
  instruction?: string;
  display_order: number;
  korean_text?: string;
  romanization?: string;
  english_text?: string;
  content_text?: string;
  audio_url?: string;
  options?: string[] | SentenceTile[];
  correct_answer?: string;
  explanation?: string;
}

export interface ExerciseSubmission {
  answer: string;
  quality?: number;
  peeked?: boolean;
}

export interface ExerciseResult {
  correct: boolean;
  correct_answer: string;
  explanation?: string;
  pattern_mastery?: {
    pattern_title: string;
    mastery_score: number;
    attempts: number;
  };
}

// ============================================
// Progress Types
// ============================================

export interface LessonProgress {
  is_started: boolean;
  is_completed: boolean;
  completed_exercises: number;
  total_exercises: number;
  score?: number;
}

export interface OverallProgress {
  total_lessons: number;
  completed_lessons: number;
  completion_percentage: number;
  total_time_spent_minutes: number;
  average_score?: number;
  current_streak: number;
  courses: CourseProgress[];
}

export interface CourseProgress {
  id: number;
  title: string;
  completed_lessons: number;
  total_lessons: number;
  percentage: number;
}

export interface RecentActivity {
  lesson_id: number;
  lesson_title: string;
  unit_title?: string;
  completed_at?: string;
  score?: number;
  time_spent_minutes: number;
}

export interface LearningStats {
  lessons_completed_today: number;
  lessons_completed_this_week: number;
  total_exercises_completed: number;
  best_score?: number;
  improvement_trend?: number;
  current_streak: number;
}

// ============================================
// Vocabulary Types
// ============================================

export interface VocabularyItem {
  id: number;
  korean: string;
  romanization?: string;
  english: string;
  part_of_speech?: string;
  example_sentence_korean?: string;
  example_sentence_english?: string;
  category?: string;
  difficulty_level: number;
  audio_url?: string;
  times_practiced?: number;
  times_correct?: number;
  accuracy_rate?: number;
  // Spaced repetition fields
  next_review_date?: string;
  review_interval?: number;
  repetitions?: number;
  ease_factor?: number;
}

export interface VocabularyCategory {
  name: string;
  count: number;
}

// ============================================
// LLM Types (kept from v1)
// ============================================

export interface Card {
  id: number;
  front_korean: string;
  front_romanization?: string;
  back_english: string;
}

export interface ExplanationRequest {
  vocab_id?: number;
  card_id?: number;
  user_context?: {
    level?: number;
    previous_ratings?: number[];
    time_spent?: number;
  };
}

export interface LLMExplanation {
  explanation: string;
  vocab_id?: number;
  card_id?: number;
  generated_at: string;
}

export interface ExerciseExplanationRequest {
  exercise_id: number;
  user_context?: {
    level?: number;
  };
}

export interface LLMExerciseExplanation {
  explanation: string;
  exercise_id: number;
  generated_at: string;
}

export interface LLMConversationExchange {
  user: string;
  assistant: string;
}

export interface LLMHealth {
  status: string;
  available: boolean;
  models?: string[];
  configured_model?: string;
  model_loaded?: boolean;
  error?: string;
}

// ============================================
// API Response Types
// ============================================

export interface CoursesResponse {
  courses: Course[];
}

export interface CourseDetailResponse {
  course: Course & { units: Unit[] };
}

export interface UnitLessonsResponse {
  unit: { id: number; title: string };
  lessons: LessonSummary[];
}

export interface LessonDetailResponse {
  lesson: Lesson;
}

export interface ProgressResponse {
  progress: OverallProgress;
}

export interface RecentActivityResponse {
  recent_activity: RecentActivity[];
}

export interface StatsResponse {
  stats: LearningStats;
}

export interface VocabularyListResponse {
  vocabulary: VocabularyItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface VocabularyCategoriesResponse {
  categories: VocabularyCategory[];
}

export interface VocabularyDueResponse {
  vocabulary: VocabularyItem[];
  total_due: number;
  new_items: number;
}

export interface VocabularyReviewRequest {
  quality: number; // 0-5 rating
}

export interface VocabularyReviewResponse {
  success: boolean;
  next_review_date: string | null;
  review_interval: number;
  repetitions: number;
  ease_factor: number;
}

// ============================================
// Grammar Pattern & Mastery Types
// ============================================

export interface GrammarPattern {
  id: number;
  title: string;
  pattern: string;
  meaning?: string;
  example_korean?: string;
  example_english?: string;
  mastery?: GrammarMastery;
}

export interface GrammarMastery {
  mastery_score: number;
  attempts: number;
  correct: number;
}

// ============================================
// Pronunciation Self-Check Types
// ============================================

export interface PronunciationSelfCheck {
  exerciseId: number;
  rating: 'good' | 'okay' | 'again';
  timestamp: number;
}

// ============================================
// Weakness Review Types
// ============================================

export interface WeakGrammarItem {
  pattern_id: number;
  pattern_title: string;
  mastery_score: number;
  attempts: number;
  correct: number;
  exercise_ids: number[];
}

export interface WeakVocabularyItem {
  id: number;
  korean: string;
  english: string;
  romanization?: string;
  accuracy_rate: number;
  times_practiced: number;
}

export interface WeaknessData {
  weak_grammar: WeakGrammarItem[];
  weak_vocabulary: WeakVocabularyItem[];
}

// ============================================
// Exercise SRS Types (Sentence-Based SRS)
// ============================================

export interface ExerciseSRSData {
  exercise_id: number;
  next_review_date?: string;
  review_interval: number;
  repetitions: number;
  ease_factor: number;
}

export interface DueExercise extends Exercise {
  srs?: ExerciseSRSData;
  lesson_title?: string;
}

export interface ExerciseDueResponse {
  exercises: DueExercise[];
  total_due: number;
  new_items: number;
}

export interface ExerciseReviewResponse {
  success: boolean;
  next_review_date: string | null;
  review_interval: number;
  repetitions: number;
  ease_factor: number;
}

// ============================================
// User Settings Types
// ============================================

export type ImmersionLevel = 1 | 2 | 3;

export interface UserSettings {
  immersion_level: ImmersionLevel;
}

// Dashboard statistics
export interface DashboardStats {
  vocabulary_mastery_percent: number;
  grammar_patterns_completed: number;
  listening_hours: number;
  reading_passages_completed: number;
  topik1_readiness_percent: number;
  vocabulary_due_count: number;
  lessons_completed_this_week: number;
  current_streak: number;
}
