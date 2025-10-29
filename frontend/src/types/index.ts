/**
 * TypeScript type definitions for the Korean Learning App
 */

export interface Card {
  id: number;
  deck_id: number;
  front_korean: string;
  front_romanization?: string;
  back_english: string;
  example_sentence?: string;
  level: number;
  interval: number;
  repetitions: number;
  ease_factor: number;
  next_review_date?: string;
  audio_url?: string;
  is_new: boolean;
  is_due: boolean;
}

export interface Review {
  id: number;
  card_id: number;
  review_date: string;
  quality_rating: number;
  time_spent?: number;
  was_successful: boolean;
}

export interface Deck {
  id: number;
  name: string;
  description?: string;
  level: number;
  total_cards?: number;
  due_cards?: number;
}

export interface Stats {
  total_cards: number;
  cards_due_today: number;
  new_cards: number;
  cards_reviewed_today: number;
  total_reviews: number;
  accuracy_rate: number;
  streak_days: number;
  decks: Deck[];
}

export interface ReviewSubmission {
  card_id: number;
  quality_rating: number;
  time_spent?: number;
}

export interface ReviewResponse {
  success: boolean;
  card_id: number;
  next_review_date: string;
  interval: number;
  repetitions: number;
  ease_factor: number;
}

export interface DueCardsResponse {
  cards: Card[];
  total_due: number;
  limit: number;
}
