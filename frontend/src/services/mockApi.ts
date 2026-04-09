import type {
  Employee,
  CompetencyGap,
  RecommendationResponse,
  SentimentAnalysis,
  OverviewStats,
  TrainingRecommendation,
} from '@/types';

export interface EmployeeEnrollment {
  curso_id: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  status: 'completed' | 'in_progress' | 'enrolled';
  progress: number;
  nota?: number;
  data_matricula: string;
  data_conclusao?: string | null;
}

export interface EmployeeTrainingSummary {
  total_courses: number;
  completed_courses: number;
  in_progress_courses: number;
  enrolled_courses: number;
  completion_rate: number;
  average_score: number;
  categories_completed: string[];
  completed_course_ids: string[];
  in_progress_course_ids: string[];
}

interface StoredEnrollments {
  [employeeKey: string]: EmployeeEnrollment[];
}

interface StoredAssistantSessions {
  [sessionId: string]: AssistantSession;
}

interface FeedbackEvent {
  employee_id: number;
  employee_name: string;
  curso_id: string;
  curso_titulo: string;
  action: 'viewed' | 'clicked' | 'enrolled' | 'dismissed' | 'rated';
  timestamp: string;
  rating?: number;
  metadata?: Record<string, unknown>;
}

interface AssistantMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

interface AssistantSession {
  curso_id: string;
  employee_id: number;
  employee_name: string;
  messages: AssistantMessage[];
}

interface StaticCourse {
  cursoID: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  cargaHoraria: number;
  obrigatorio: boolean;
  notaMinima: number;
}

interface StaticEmployeeRecord {
  profile: Record<string, any>;
  evaluation: Record<string, any>;
  gaps: {
    employee_name: string;
    total_gaps: number;
    gaps: CompetencyGap[];
  };
  recommendations: RecommendationResponse;
  sentiment_analysis: {
    employee_name: string;
    sentiment_analysis: Record<string, SentimentAnalysis[]>;
  };
  training: {
    employee_name: string;
    enrollments: EmployeeEnrollment[];
    summary: EmployeeTrainingSummary;
  };
}

interface StaticDataset {
  generated_at: string;
  employees: Employee[];
  employees_by_name: Record<string, StaticEmployeeRecord>;
  courses: {
    total: number;
    category_filter: string | null;
    courses: StaticCourse[];
  };
  overview_stats: OverviewStats;
  analytics_seed_events: FeedbackEvent[];
}

const STATIC_DATA_URL = '/mock-data/talentboost-static.json';
const FEEDBACK_STORAGE_KEY = 'talentboost.feedback.v1';
const ENROLLMENTS_STORAGE_KEY = 'talentboost.enrollments.v1';
const ASSISTANT_STORAGE_KEY = 'talentboost.assistant.v1';

let staticDatasetPromise: Promise<StaticDataset> | null = null;

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function normalizeName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, '_');
}

function compareCourseIds(a: string, b: string): number {
  const aNum = Number(a.replace(/\D/g, ''));
  const bNum = Number(b.replace(/\D/g, ''));
  return aNum - bNum;
}

function getStorage<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback;

  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function setStorage<T>(key: string, value: T) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

async function loadStaticDataset(): Promise<StaticDataset> {
  if (!staticDatasetPromise) {
    staticDatasetPromise = fetch(STATIC_DATA_URL).then(async (response) => {
      if (!response.ok) {
        throw new Error(`Falha ao carregar ${STATIC_DATA_URL}: ${response.status}`);
      }
      return (await response.json()) as StaticDataset;
    });
  }

  return staticDatasetPromise;
}

async function getEmployeeRecord(employeeName: string): Promise<StaticEmployeeRecord> {
  const dataset = await loadStaticDataset();
  const employeeRecord = dataset.employees_by_name[normalizeName(employeeName)];

  if (!employeeRecord) {
    throw new Error(`Colaborador não encontrado: ${employeeName}`);
  }

  return employeeRecord;
}

async function getCourseById(cursoId: string): Promise<StaticCourse | undefined> {
  const dataset = await loadStaticDataset();
  return dataset.courses.courses.find((course) => course.cursoID === cursoId);
}

function buildRecommendationSummary(recommendations: TrainingRecommendation[]) {
  if (recommendations.length === 0) {
    return {
      total: 0,
      by_priority: {},
      by_category: {},
      average_relevance: 0,
    };
  }

  const byPriority: Record<string, string[]> = {};
  const byCategory: Record<string, string[]> = {};

  recommendations.forEach((recommendation) => {
    byPriority[recommendation.priority] = byPriority[recommendation.priority] || [];
    byPriority[recommendation.priority].push(recommendation.titulo);

    byCategory[recommendation.categoria] = byCategory[recommendation.categoria] || [];
    byCategory[recommendation.categoria].push(recommendation.titulo);
  });

  const averageRelevance =
    recommendations.reduce((sum, recommendation) => sum + recommendation.relevance_score, 0) /
    recommendations.length;

  return {
    total: recommendations.length,
    by_priority: byPriority,
    by_category: byCategory,
    average_relevance: Number(averageRelevance.toFixed(2)),
  };
}

function getStoredEnrollments(employeeName: string): EmployeeEnrollment[] {
  const allStoredEnrollments = getStorage<StoredEnrollments>(ENROLLMENTS_STORAGE_KEY, {});
  return allStoredEnrollments[normalizeName(employeeName)] || [];
}

function saveStoredEnrollments(employeeName: string, enrollments: EmployeeEnrollment[]) {
  const allStoredEnrollments = getStorage<StoredEnrollments>(ENROLLMENTS_STORAGE_KEY, {});
  allStoredEnrollments[normalizeName(employeeName)] = enrollments;
  setStorage(ENROLLMENTS_STORAGE_KEY, allStoredEnrollments);
}

function mergeEnrollments(
  seededEnrollments: EmployeeEnrollment[],
  storedEnrollments: EmployeeEnrollment[]
): EmployeeEnrollment[] {
  const enrollmentsMap = new Map<string, EmployeeEnrollment>();

  seededEnrollments.forEach((enrollment) => {
    enrollmentsMap.set(enrollment.curso_id, clone(enrollment));
  });

  storedEnrollments.forEach((enrollment) => {
    enrollmentsMap.set(enrollment.curso_id, clone(enrollment));
  });

  return Array.from(enrollmentsMap.values()).sort((left, right) => {
    if (left.data_matricula === right.data_matricula) {
      return compareCourseIds(left.curso_id, right.curso_id);
    }
    return right.data_matricula.localeCompare(left.data_matricula);
  });
}

function summarizeEnrollments(enrollments: EmployeeEnrollment[]): EmployeeTrainingSummary {
  const completed = enrollments.filter((item) => item.status === 'completed');
  const inProgress = enrollments.filter((item) => item.status === 'in_progress');
  const enrolled = enrollments.filter((item) => item.status === 'enrolled');
  const rated = completed.filter((item) => typeof item.nota === 'number');

  return {
    total_courses: enrollments.length,
    completed_courses: completed.length,
    in_progress_courses: inProgress.length,
    enrolled_courses: enrolled.length,
    completion_rate: enrollments.length ? completed.length / enrollments.length : 0,
    average_score: rated.length
      ? Number(
          (
            rated.reduce((sum, item) => sum + (item.nota || 0), 0) / rated.length
          ).toFixed(2)
        )
      : 0,
    categories_completed: Array.from(new Set(completed.map((item) => item.categoria))).sort(),
    completed_course_ids: completed.map((item) => item.curso_id),
    in_progress_course_ids: inProgress.map((item) => item.curso_id),
  };
}

function getAllFeedbackEvents(seedEvents: FeedbackEvent[]): FeedbackEvent[] {
  const storedEvents = getStorage<FeedbackEvent[]>(FEEDBACK_STORAGE_KEY, []);
  return [...seedEvents, ...storedEvents].sort((left, right) =>
    left.timestamp.localeCompare(right.timestamp)
  );
}

function storeFeedbackEvent(event: FeedbackEvent) {
  const currentEvents = getStorage<FeedbackEvent[]>(FEEDBACK_STORAGE_KEY, []);
  currentEvents.push(event);
  setStorage(FEEDBACK_STORAGE_KEY, currentEvents);
}

function summarizeAnalytics(events: FeedbackEvent[]) {
  const totalViews = events.filter((event) => event.action === 'viewed').length;
  const totalClicks = events.filter((event) => event.action === 'clicked').length;
  const totalEnrollments = events.filter((event) => event.action === 'enrolled').length;
  const totalDismissals = events.filter((event) => event.action === 'dismissed').length;

  return {
    total_interactions: events.length,
    total_views: totalViews,
    total_clicks: totalClicks,
    total_enrollments: totalEnrollments,
    total_dismissals: totalDismissals,
    overall_ctr: totalViews > 0 ? Number((totalClicks / totalViews).toFixed(3)) : 0,
    overall_enrollment_rate: totalClicks > 0 ? Number((totalEnrollments / totalClicks).toFixed(3)) : 0,
    unique_employees: new Set(events.map((event) => event.employee_id)).size,
    unique_courses: new Set(events.map((event) => event.curso_id)).size,
  };
}

function buildPopularCourses(events: FeedbackEvent[], topN: number) {
  const courseStats = new Map<
    string,
    { curso_id: string; titulo: string; clicks: number; enrollments: number; views: number }
  >();

  events.forEach((event) => {
    if (!courseStats.has(event.curso_id)) {
      courseStats.set(event.curso_id, {
        curso_id: event.curso_id,
        titulo: event.curso_titulo,
        clicks: 0,
        enrollments: 0,
        views: 0,
      });
    }

    const stats = courseStats.get(event.curso_id)!;
    if (event.action === 'viewed') stats.views += 1;
    if (event.action === 'clicked') stats.clicks += 1;
    if (event.action === 'enrolled') stats.enrollments += 1;
  });

  return Array.from(courseStats.values())
    .sort((left, right) => {
      if (right.clicks !== left.clicks) return right.clicks - left.clicks;
      if (right.enrollments !== left.enrollments) return right.enrollments - left.enrollments;
      return left.titulo.localeCompare(right.titulo);
    })
    .slice(0, topN);
}

function buildCourseAnalytics(events: FeedbackEvent[], cursoId: string) {
  const filteredEvents = events.filter((event) => event.curso_id === cursoId);
  const views = filteredEvents.filter((event) => event.action === 'viewed').length;
  const clicks = filteredEvents.filter((event) => event.action === 'clicked').length;
  const enrollments = filteredEvents.filter((event) => event.action === 'enrolled').length;
  const dismissals = filteredEvents.filter((event) => event.action === 'dismissed').length;
  const ratings = filteredEvents
    .filter((event) => event.action === 'rated' && typeof event.rating === 'number')
    .map((event) => event.rating as number);

  return {
    curso_id: cursoId,
    click_through_rate: views > 0 ? Number((clicks / views).toFixed(3)) : 0,
    enrollment_rate: clicks > 0 ? Number((enrollments / clicks).toFixed(3)) : 0,
    dismissal_rate: views > 0 ? Number((dismissals / views).toFixed(3)) : 0,
    average_rating: ratings.length
      ? Number((ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length).toFixed(2))
      : 0,
  };
}

function readAssistantSessions(): StoredAssistantSessions {
  return getStorage<StoredAssistantSessions>(ASSISTANT_STORAGE_KEY, {});
}

function writeAssistantSessions(sessions: StoredAssistantSessions) {
  setStorage(ASSISTANT_STORAGE_KEY, sessions);
}

function getCategoryGuidance(category: string) {
  const normalizedCategory = category.toLowerCase();

  if (normalizedCategory.includes('compliance')) {
    return {
      focus: 'normas, responsabilidade e tomada de decisão segura',
      examples: ['revisar políticas internas', 'avaliar riscos', 'documentar evidências'],
    };
  }

  if (normalizedCategory.includes('lider')) {
    return {
      focus: 'liderança, influência e desenvolvimento do time',
      examples: ['dar feedback claro', 'delegar com contexto', 'acompanhar evolução do time'],
    };
  }

  if (normalizedCategory.includes('comport')) {
    return {
      focus: 'comunicação, colaboração e repertório de relacionamento',
      examples: ['conduzir conversas difíceis', 'alinhar expectativas', 'facilitar decisões'],
    };
  }

  return {
    focus: 'fundamentos técnicos e aplicação prática no trabalho',
    examples: ['resolver problemas recorrentes', 'automatizar etapas do dia a dia', 'aplicar boas práticas em projetos'],
  };
}

function buildWelcomeMessage(params: {
  employeeName: string;
  employeeCargo: string;
  courseTitle: string;
  progress: number;
}) {
  return [
    `Olá, ${params.employeeName}!`,
    `Sou seu assistente virtual para o curso **${params.courseTitle}**.`,
    `Vou adaptar as explicações ao seu contexto como **${params.employeeCargo}**.`,
    `Você está com **${params.progress.toFixed(0)}%** de progresso. Pode me perguntar sobre conteúdo, aplicação prática, revisão ou exercícios.`,
  ].join('\n\n');
}

function buildTutorResponse(params: {
  question: string;
  employeeName: string;
  employeeCargo: string;
  course: StaticCourse;
  progress: number;
  topGaps: string[];
}) {
  const question = params.question.toLowerCase();
  const guidance = getCategoryGuidance(params.course.categoria);
  const highlightedGaps =
    params.topGaps.length > 0
      ? `Isso conversa especialmente com seus gaps em **${params.topGaps.join(', ')}**.`
      : `Isso ajuda a ampliar seu repertório profissional de forma estruturada.`;

  if (
    question.includes('o que vou aprender') ||
    question.includes('conteudo') ||
    question.includes('conteúdo') ||
    question.includes('curso')
  ) {
    return [
      `Neste curso, o foco principal é **${guidance.focus}**.`,
      `Você deve sair mais preparado para:`,
      `- aplicar conceitos em situações reais do trabalho`,
      `- reconhecer padrões e tomar decisões com mais segurança`,
      `- transformar teoria em prática com mais autonomia`,
      highlightedGaps,
    ].join('\n');
  }

  if (
    question.includes('aplicar') ||
    question.includes('trabalho') ||
    question.includes('dia a dia') ||
    question.includes('pratica')
  ) {
    return [
      `Pensando no seu contexto como **${params.employeeCargo}**, você pode aplicar este conteúdo em frentes como:`,
      ...guidance.examples.map((example) => `- ${example}`),
      `Uma boa estratégia é escolher **um caso real da sua rotina** e testar o conceito ainda esta semana.`,
    ].join('\n');
  }

  if (
    question.includes('exerc') ||
    question.includes('prático') ||
    question.includes('pratico') ||
    question.includes('atividade')
  ) {
    return [
      `Uma forma prática de estudar este tema é:`,
      `1. resuma o conceito em uma frase curta;`,
      `2. escolha um cenário do seu trabalho onde ele se aplica;`,
      `3. execute um teste pequeno e registre o resultado;`,
      `4. compare o que funcionou com o que o curso recomenda.`,
      `Se quiser, posso transformar isso em um plano de estudo de 15 minutos.`,
    ].join('\n');
  }

  if (
    question.includes('resumo') ||
    question.includes('revis') ||
    question.includes('revisão') ||
    question.includes('nao entendi') ||
    question.includes('não entendi')
  ) {
    return [
      `Vamos simplificar.`,
      `- O objetivo do curso é fortalecer **${guidance.focus}**.`,
      `- O ponto mais importante é entender **quando usar** o conceito, não só decorá-lo.`,
      `- Como você já está em **${params.progress.toFixed(0)}%** do curso, vale revisar o último módulo e anotar 2 aprendizados aplicáveis no seu trabalho.`,
    ].join('\n');
  }

  return [
    `Posso te ajudar com isso.`,
    `Neste curso de **${params.course.categoria}**, o mais valioso é conectar o conteúdo com situações concretas do seu dia a dia.`,
    highlightedGaps,
    `Se quiser, posso responder de três formas: **explicação simples**, **exemplo prático** ou **plano de estudo curto**.`,
  ].join('\n\n');
}

export const mockTalentBoostApi = {
  async listEmployees(): Promise<Employee[]> {
    const dataset = await loadStaticDataset();
    return clone(dataset.employees).sort((left, right) => left.name.localeCompare(right.name));
  },

  async getEmployeeProfile(employeeName: string) {
    const record = await getEmployeeRecord(employeeName);
    return clone(record.profile);
  },

  async getEmployeeEvaluation(employeeName: string) {
    const record = await getEmployeeRecord(employeeName);
    return clone(record.evaluation);
  },

  async analyzeGaps(
    employeeName: string
  ): Promise<{ employee_name: string; total_gaps: number; gaps: CompetencyGap[] }> {
    const record = await getEmployeeRecord(employeeName);
    return clone(record.gaps);
  },

  async getRecommendations(
    employeeName: string,
    topN = 5,
    _excludeCompleted = true
  ): Promise<RecommendationResponse> {
    const record = await getEmployeeRecord(employeeName);
    const response = clone(record.recommendations);
    const slicedRecommendations = response.recommendations.slice(0, topN);
    response.recommendations = slicedRecommendations;
    response.summary = buildRecommendationSummary(slicedRecommendations);
    return response;
  },

  async getSentimentAnalysis(
    employeeName: string
  ): Promise<{ employee_name: string; sentiment_analysis: Record<string, SentimentAnalysis[]> }> {
    const record = await getEmployeeRecord(employeeName);
    return clone(record.sentiment_analysis);
  },

  async listCourses(category?: string) {
    const dataset = await loadStaticDataset();
    const filteredCourses = category
      ? dataset.courses.courses.filter((course) => course.categoria === category)
      : dataset.courses.courses;

    return {
      total: filteredCourses.length,
      category_filter: category || null,
      courses: clone(filteredCourses).sort((left, right) => compareCourseIds(left.cursoID, right.cursoID)),
    };
  },

  async getOverviewStats(): Promise<OverviewStats> {
    const dataset = await loadStaticDataset();
    return clone(dataset.overview_stats);
  },

  async getEmployeeEnrollments(employeeName: string) {
    const record = await getEmployeeRecord(employeeName);
    const mergedEnrollments = mergeEnrollments(
      record.training.enrollments,
      getStoredEnrollments(employeeName)
    );

    return {
      employee_name: employeeName,
      enrollments: mergedEnrollments,
      summary: summarizeEnrollments(mergedEnrollments),
    };
  },

  async enrollInCourse(params: {
    employee_id: number;
    employee_name: string;
    curso_id: string;
    curso_titulo?: string;
  }) {
    const current = await this.getEmployeeEnrollments(params.employee_name);
    const existingEnrollment = current.enrollments.find(
      (enrollment) => enrollment.curso_id === params.curso_id
    );

    if (existingEnrollment) {
      return { status: 'success', enrollment: existingEnrollment, already_enrolled: true };
    }

    const course = await getCourseById(params.curso_id);
    if (!course) {
      throw new Error(`Curso não encontrado: ${params.curso_id}`);
    }

    const enrollment: EmployeeEnrollment = {
      curso_id: course.cursoID,
      titulo: course.titulo,
      categoria: course.categoria,
      modalidade: course.modalidade,
      status: 'in_progress',
      progress: 0,
      data_matricula: new Date().toISOString().slice(0, 10),
    };

    const merged = mergeEnrollments(current.enrollments, [enrollment]);
    saveStoredEnrollments(params.employee_name, merged);

    storeFeedbackEvent({
      employee_id: params.employee_id,
      employee_name: params.employee_name,
      curso_id: course.cursoID,
      curso_titulo: params.curso_titulo || course.titulo,
      action: 'enrolled',
      timestamp: new Date().toISOString(),
      metadata: { source: 'local_demo_enrollment' },
    });

    return { status: 'success', enrollment, already_enrolled: false };
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
    storeFeedbackEvent({
      ...feedback,
      timestamp: new Date().toISOString(),
    });

    return { status: 'success', message: 'Feedback registrado' };
  },

  async getEmployeeFeedbackHistory(employeeId: number) {
    const dataset = await loadStaticDataset();
    const events = getAllFeedbackEvents(dataset.analytics_seed_events).filter(
      (event) => event.employee_id === employeeId
    );

    return {
      employee_id: employeeId,
      total_interactions: events.length,
      history: clone(events).sort((left, right) => right.timestamp.localeCompare(left.timestamp)),
    };
  },

  async getAnalyticsSummary() {
    const dataset = await loadStaticDataset();
    return summarizeAnalytics(getAllFeedbackEvents(dataset.analytics_seed_events));
  },

  async getCourseAnalytics(cursoId: string) {
    const dataset = await loadStaticDataset();
    return buildCourseAnalytics(getAllFeedbackEvents(dataset.analytics_seed_events), cursoId);
  },

  async getPopularCourses(topN = 10) {
    const dataset = await loadStaticDataset();
    return {
      top_n: topN,
      popular_courses: buildPopularCourses(getAllFeedbackEvents(dataset.analytics_seed_events), topN),
    };
  },

  async getRecommendationsPerformance() {
    const dataset = await loadStaticDataset();
    const summary = summarizeAnalytics(getAllFeedbackEvents(dataset.analytics_seed_events));

    return {
      recommendation_stats: summary,
      cache_stats: {
        cache_size: 0,
        cache_enabled: false,
        cache_ttl_seconds: 0,
      },
      system_info: {
        total_courses_indexed: dataset.courses.total,
        recommendation_strategies: ['static_seed', 'frontend_fallback', 'local_feedback_tracking'],
      },
    };
  },

  async startCourseAssistant(params: {
    session_id: string;
    curso_id: string;
    employee_id: number;
    employee_name: string;
    progresso_curso: number;
    modulo_atual?: string;
  }) {
    const course = await getCourseById(params.curso_id);
    const employeeRecord = await getEmployeeRecord(params.employee_name).catch(() => null);
    const employeeCargo =
      employeeRecord?.profile?.CARGO_NOME || employeeRecord?.recommendations?.profile_summary?.cargo || 'Colaborador';
    const welcomeMessage: AssistantMessage = {
      role: 'assistant',
      content: buildWelcomeMessage({
        employeeName: params.employee_name,
        employeeCargo,
        courseTitle: course?.titulo || 'Tutoria Geral',
        progress: params.progresso_curso,
      }),
      timestamp: new Date().toISOString(),
    };

    const sessions = readAssistantSessions();
    sessions[params.session_id] = {
      curso_id: params.curso_id,
      employee_id: params.employee_id,
      employee_name: params.employee_name,
      messages: [welcomeMessage],
    };
    writeAssistantSessions(sessions);

    return {
      session_id: params.session_id,
      curso_id: params.curso_id,
      message: clone(welcomeMessage),
      status: 'session_started',
    };
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
    const sessions = readAssistantSessions();

    if (!sessions[params.session_id]) {
      await this.startCourseAssistant({
        session_id: params.session_id,
        curso_id: params.curso_id,
        employee_id: params.employee_id,
        employee_name: params.employee_name,
        progresso_curso: params.progresso_curso,
        modulo_atual: params.modulo_atual,
      });
    }

    const course = await getCourseById(params.curso_id);
    const employeeRecord = await getEmployeeRecord(params.employee_name).catch(() => null);
    const topGaps = employeeRecord?.gaps.gaps.slice(0, 2).map((gap) => gap.competency_name) || [];
    const employeeCargo =
      employeeRecord?.profile?.CARGO_NOME || employeeRecord?.recommendations?.profile_summary?.cargo || 'Colaborador';

    const userMessage: AssistantMessage = {
      role: 'user',
      content: params.question,
      timestamp: new Date().toISOString(),
    };

    const assistantMessage: AssistantMessage = {
      role: 'assistant',
      content: buildTutorResponse({
        question: params.question,
        employeeName: params.employee_name,
        employeeCargo,
        course:
          course ||
          ({
            cursoID: params.curso_id,
            titulo: 'Tutoria Geral',
            categoria: 'Desenvolvimento Profissional',
            modalidade: 'Online',
            cargaHoraria: 4,
            obrigatorio: false,
            notaMinima: 7,
          } as StaticCourse),
        progress: params.progresso_curso,
        topGaps,
      }),
      timestamp: new Date().toISOString(),
      metadata: {
        modulo_atual: params.modulo_atual || 'Módulo atual',
      },
    };

    const session = sessions[params.session_id];
    session.messages.push(userMessage, assistantMessage);
    writeAssistantSessions(sessions);

    return {
      session_id: params.session_id,
      question: params.question,
      response: clone(assistantMessage),
    };
  },

  async getCourseAssistantHistory(sessionId: string) {
    const sessions = readAssistantSessions();
    const messages = sessions[sessionId]?.messages || [];

    return {
      session_id: sessionId,
      message_count: messages.length,
      messages: clone(messages),
    };
  },

  async getCourseAssistantSuggestions(params: {
    session_id: string;
    curso_id: string;
    employee_id: number;
    employee_name: string;
    progresso_curso: number;
    modulo_atual?: string;
  }) {
    const employeeRecord = await getEmployeeRecord(params.employee_name).catch(() => null);
    const level = employeeRecord?.recommendations.profile_summary.nivel || 'Pleno';
    const suggestions: string[] = [];

    if (params.progresso_curso < 25) {
      suggestions.push(
        `Comece pelo módulo "${params.modulo_atual || 'Introdução'}" e avance em blocos curtos de estudo.`
      );
    } else if (params.progresso_curso < 50) {
      suggestions.push('Revise os conceitos principais antes de seguir para o próximo tópico.');
    } else if (params.progresso_curso < 75) {
      suggestions.push('Hora de praticar: tente aplicar o conteúdo em um caso real do seu trabalho.');
    } else {
      suggestions.push('Você está perto do fim: revise os pontos-chave e prepare-se para a avaliação final.');
    }

    if (level === 'Junior') {
      suggestions.push('Anote exemplos simples do dia a dia para consolidar cada conceito aprendido.');
    } else if (level === 'Senior') {
      suggestions.push('Busque aplicações avançadas e compartilhe um exemplo com o time.');
    } else {
      suggestions.push('Conecte o conteúdo do curso com uma melhoria concreta no seu fluxo de trabalho.');
    }

    return {
      curso_id: params.curso_id,
      employee_id: params.employee_id,
      progresso: params.progresso_curso,
      suggestions,
    };
  },
};
