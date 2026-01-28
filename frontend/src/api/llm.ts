/**
 * LLM API client for AI-powered explanations
 */
import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { LLMExplanation, LLMHealth, ExplanationRequest } from '../types';
import { API_BASE_URL } from '../config';

class LLMClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/llm`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds for LLM responses
    });
  }

  async healthCheck(): Promise<LLMHealth> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async explainCard(request: ExplanationRequest): Promise<LLMExplanation> {
    const response = await this.client.post('/explain', request);
    return response.data;
  }
}

export const llmClient = new LLMClient();
export default llmClient;

