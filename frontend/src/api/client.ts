/**
 * API client for communicating with the Flask backend
 */
import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  Card,
  Stats,
  ReviewSubmission,
  ReviewResponse,
  DueCardsResponse,
  Review,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 seconds
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Card endpoints
  async getDueCards(params?: {
    level?: number;
    deck_id?: number;
    limit?: number;
  }): Promise<DueCardsResponse> {
    const response = await this.client.get('/cards/due', { params });
    return response.data;
  }

  async getCard(cardId: number): Promise<Card> {
    const response = await this.client.get(`/cards/${cardId}`);
    return response.data;
  }

  async getAllCards(params?: {
    page?: number;
    per_page?: number;
    deck_id?: number;
    level?: number;
  }): Promise<{
    cards: Card[];
    page: number;
    per_page: number;
    total_count: number;
    total_pages: number;
  }> {
    const response = await this.client.get('/cards', { params });
    return response.data;
  }

  // Review endpoints
  async submitReview(review: ReviewSubmission): Promise<ReviewResponse> {
    const response = await this.client.post('/reviews', review);
    return response.data;
  }

  async getCardReviews(cardId: number): Promise<{
    card_id: number;
    reviews: Review[];
    total_reviews: number;
  }> {
    const response = await this.client.get(`/reviews/card/${cardId}`);
    return response.data;
  }

  // Stats endpoints
  async getStats(): Promise<Stats> {
    const response = await this.client.get('/stats');
    return response.data;
  }

  async getRecentReviews(): Promise<{
    reviews: (Review & { card_korean?: string; card_english?: string })[];
    count: number;
  }> {
    const response = await this.client.get('/stats/recent-reviews');
    return response.data;
  }

  // Audio endpoint helper
  getAudioUrl(filename: string): string {
    return `${API_BASE_URL}/api/audio/${filename}`;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
