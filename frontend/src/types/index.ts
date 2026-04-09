export interface Employee {
  name: string;
  cargo: string;
  departamento: string;
  nivel?: string;
}

export interface CompetencyGap {
  competency_name: string;
  competency_key: string;
  average_score: number;
  gap_severity: 'critical' | 'high' | 'medium' | 'low';
  urgency: 'critical' | 'high' | 'medium' | 'low';
  context: string;
  evaluator_consensus: number;
  development_hints: string[];
  key_observations: string[];
}

export interface TrainingRecommendation {
  curso_id: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  carga_horaria: number;
  obrigatorio: boolean;
  relevance_score: number;
  match_reason: string;
  addresses_gaps: string[];
  priority: 'critical' | 'high' | 'medium' | 'low';
}

export interface ProfileSummary {
  cargo: string;
  nivel: string;
  nota_media_geral: number;
  pontos_fortes: string[];
  total_gaps: number;
}

export interface RecommendationResponse {
  employee_name: string;
  profile_summary: ProfileSummary;
  recommendations: TrainingRecommendation[];
  summary: {
    total: number;
    by_priority: Record<string, string[]>;
    by_category: Record<string, string[]>;
    average_relevance: number;
  };
}

export interface SentimentAnalysis {
  evaluator_role: string;
  tone: string;
  urgency: string;
  confidence: number;
  key_phrases: string[];
  development_hints: string[];
}

export interface OverviewStats {
  total_employees: number;
  total_courses: number;
  categories: Record<string, number>;
}
