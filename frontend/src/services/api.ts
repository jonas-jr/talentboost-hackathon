import axios from 'axios';
import type {
  Employee,
  CompetencyGap,
  RecommendationResponse,
  SentimentAnalysis,
  OverviewStats,
} from '@/types';
import { mockTalentBoostApi } from './mockApi';

const baseURL = import.meta.env.VITE_API_URL || '/api';
const preferLocalData = import.meta.env.PROD && !import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL,
  timeout: 30000,
});

async function withFallback<T>(
  remoteCall: () => Promise<T>,
  localCall: () => Promise<T>,
  isValid?: (value: T) => boolean
): Promise<T> {
  if (preferLocalData) {
    return localCall();
  }

  try {
    const response = await remoteCall();
    if (isValid && !isValid(response)) {
      throw new Error('Resposta remota inválida');
    }
    return response;
  } catch (error) {
    console.warn('Fallback para dados locais do TalentBoost:', error);
    return localCall();
  }
}

const isObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

export const talentBoostApi = {
  async listEmployees(): Promise<Employee[]> {
    return withFallback(
      async () => {
        const { data } = await api.get<Employee[]>('/employees');
        return data;
      },
      () => mockTalentBoostApi.listEmployees(),
      (value) => Array.isArray(value)
    );
  },

  async getEmployeeProfile(employeeName: string) {
    return withFallback(
      async () => {
        const { data } = await api.get(`/employees/${encodeURIComponent(employeeName)}/profile`);
        return data;
      },
      () => mockTalentBoostApi.getEmployeeProfile(employeeName),
      isObject
    );
  },

  async getEmployeeEvaluation(employeeName: string) {
    return withFallback(
      async () => {
        const { data } = await api.get(`/employees/${encodeURIComponent(employeeName)}/evaluation`);
        return data;
      },
      () => mockTalentBoostApi.getEmployeeEvaluation(employeeName),
      isObject
    );
  },

  async analyzeGaps(
    employeeName: string
  ): Promise<{ employee_name: string; total_gaps: number; gaps: CompetencyGap[] }> {
    return withFallback(
      async () => {
        const { data } = await api.get(`/employees/${encodeURIComponent(employeeName)}/gaps`);
        return data;
      },
      () => mockTalentBoostApi.analyzeGaps(employeeName),
      (value) => isObject(value) && Array.isArray(value.gaps)
    );
  },

  async getRecommendations(
    employeeName: string,
    topN: number = 5,
    excludeCompleted: boolean = true
  ): Promise<RecommendationResponse> {
    return withFallback(
      async () => {
        const { data } = await api.post(`/employees/${encodeURIComponent(employeeName)}/recommendations`, {
          employee_name: employeeName,
          top_n: topN,
          exclude_completed: excludeCompleted,
        });
        return data;
      },
      () => mockTalentBoostApi.getRecommendations(employeeName, topN, excludeCompleted),
      (value) => isObject(value) && Array.isArray(value.recommendations)
    );
  },

  async getSentimentAnalysis(
    employeeName: string
  ): Promise<{ employee_name: string; sentiment_analysis: Record<string, SentimentAnalysis[]> }> {
    return withFallback(
      async () => {
        const { data } = await api.get(`/employees/${encodeURIComponent(employeeName)}/sentiment-analysis`);
        return data;
      },
      () => mockTalentBoostApi.getSentimentAnalysis(employeeName),
      (value) => isObject(value) && isObject(value.sentiment_analysis)
    );
  },

  async listCourses(category?: string) {
    return withFallback(
      async () => {
        const { data } = await api.get('/courses', { params: { category } });
        return data;
      },
      () => mockTalentBoostApi.listCourses(category),
      (value) => isObject(value) && Array.isArray(value.courses)
    );
  },

  async getOverviewStats(): Promise<OverviewStats> {
    return withFallback(
      async () => {
        const { data } = await api.get<OverviewStats>('/stats/overview');
        return data;
      },
      () => mockTalentBoostApi.getOverviewStats(),
      (value) => isObject(value) && typeof value.total_courses === 'number'
    );
  },

  async getEmployeeEnrollments(employeeName: string) {
    return mockTalentBoostApi.getEmployeeEnrollments(employeeName);
  },

  async enrollInCourse(params: {
    employee_id: number;
    employee_name: string;
    curso_id: string;
    curso_titulo?: string;
  }) {
    return mockTalentBoostApi.enrollInCourse(params);
  },

  async trackFeedback(feedback: {
    employee_id: number;
    employee_name: string;
    curso_id: string;
    curso_titulo: string;
    action: 'viewed' | 'clicked' | 'enrolled' | 'dismissed' | 'rated';
    rating?: number;
    metadata?: Record<string, unknown>;
  }) {
    return withFallback(
      async () => {
        const { data } = await api.post('/feedback/track', feedback);
        return data;
      },
      () => mockTalentBoostApi.trackFeedback(feedback),
      isObject
    );
  },

  async getEmployeeFeedbackHistory(employeeId: number) {
    return withFallback(
      async () => {
        const { data } = await api.get(`/feedback/employee/${employeeId}`);
        return data;
      },
      () => mockTalentBoostApi.getEmployeeFeedbackHistory(employeeId),
      isObject
    );
  },

  async getAnalyticsSummary() {
    return withFallback(
      async () => {
        const { data } = await api.get('/analytics/summary');
        return data;
      },
      () => mockTalentBoostApi.getAnalyticsSummary(),
      (value) => isObject(value) && typeof value.total_interactions === 'number'
    );
  },

  async getCourseAnalytics(cursoId: string) {
    return withFallback(
      async () => {
        const { data } = await api.get(`/analytics/course/${cursoId}`);
        return data;
      },
      () => mockTalentBoostApi.getCourseAnalytics(cursoId),
      (value) => isObject(value) && typeof value.click_through_rate === 'number'
    );
  },

  async getPopularCourses(topN: number = 10) {
    return withFallback(
      async () => {
        const { data } = await api.get('/analytics/popular-courses', { params: { top_n: topN } });
        return data;
      },
      () => mockTalentBoostApi.getPopularCourses(topN),
      (value) => isObject(value) && Array.isArray(value.popular_courses)
    );
  },

  async getRecommendationsPerformance() {
    return withFallback(
      async () => {
        const { data } = await api.get('/analytics/recommendations-performance');
        return data;
      },
      () => mockTalentBoostApi.getRecommendationsPerformance(),
      isObject
    );
  },

  async startCourseAssistant(params: {
    session_id: string;
    curso_id: string;
    employee_id: number;
    employee_name: string;
    progresso_curso: number;
    modulo_atual?: string;
  }) {
    return withFallback(
      async () => {
        const { data } = await api.post('/course-assistant/start', params);
        return data;
      },
      () => mockTalentBoostApi.startCourseAssistant(params),
      (value) => isObject(value) && isObject(value.message)
    );
  },

  async askCourseAssistant(params: {
    session_id: string;
    curso_id: string;
    employee_id: number;
    employee_name: string;
    question: string;
    progresso_curso: number;
    modulo_atual?: string;
  }) {
    return withFallback(
      async () => {
        const { data } = await api.post('/course-assistant/ask', params);
        return data;
      },
      () => mockTalentBoostApi.askCourseAssistant(params),
      (value) => isObject(value) && isObject(value.response)
    );
  },

  async getCourseAssistantHistory(sessionId: string) {
    return withFallback(
      async () => {
        const { data } = await api.get(`/course-assistant/history/${sessionId}`);
        return data;
      },
      () => mockTalentBoostApi.getCourseAssistantHistory(sessionId),
      (value) => isObject(value) && Array.isArray(value.messages)
    );
  },

  async getCourseAssistantSuggestions(params: {
    session_id: string;
    curso_id: string;
    employee_id: number;
    employee_name: string;
    progresso_curso: number;
    modulo_atual?: string;
  }) {
    return withFallback(
      async () => {
        const { data } = await api.post('/course-assistant/suggestions', params);
        return data;
      },
      () => mockTalentBoostApi.getCourseAssistantSuggestions(params),
      (value) => isObject(value) && Array.isArray(value.suggestions)
    );
  },
};
