"""
FastAPI backend para TalentBoost.

Expõe endpoints REST para o frontend consumir.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
from typing import Optional
import os

# Import dos componentes core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from talent_boost_core.sentiment_analyzer import SentimentAnalyzer
from talent_boost_core.competency_gap_detector import CompetencyGapDetector
from talent_boost_core.profile_builder import EmployeeProfileBuilder
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine
from talent_boost_core.feedback_collector import FeedbackCollector
from talent_boost_core.course_assistant import (
    CourseAssistant,
    CourseContext,
    StudentContext,
)
import logging
import structlog
from datetime import datetime

# Helper para LLM importado de forma lazy para evitar carregar prompts do projeto principal


app = FastAPI(
    title="TalentBoost API",
    description="API para análise de avaliações e recomendação de treinamentos",
    version="1.0.0",
)

def _get_allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    configured = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    defaults = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    production_candidates = [
        os.getenv("FRONTEND_URL"),
        os.getenv("VITE_API_CLIENT_URL"),
        os.getenv("VERCEL_PROJECT_PRODUCTION_URL"),
    ]
    for candidate in production_candidates:
        if candidate:
            normalized = candidate.strip()
            if normalized and not normalized.startswith("http"):
                normalized = f"https://{normalized}"
            defaults.append(normalized)

    origins: list[str] = []
    for origin in defaults + configured:
        if origin and origin not in origins:
            origins.append(origin)

    return origins


allowed_origins = _get_allowed_origins()
allow_origin_regex = os.getenv("CORS_ALLOWED_ORIGIN_REGEX", r"https://.*\.vercel\.app")

# CORS para desenvolvimento e produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logs estruturados
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

# Diretório de dados
DATA_DIR = Path(__file__).parent.parent

# Inicializa componentes
sentiment_analyzer = SentimentAnalyzer()
gap_detector = CompetencyGapDetector(sentiment_analyzer)
profile_builder = EmployeeProfileBuilder()


# Carrega todos os cursos na inicialização
def load_all_courses():
    all_courses = []
    treinamentos_dir = DATA_DIR / "treinamentos"
    for file in treinamentos_dir.glob("treinamentos_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            courses = data.get("cursos", [])
            for course in courses:
                if not any(c.get("cursoID") == course.get("cursoID") for c in all_courses):
                    all_courses.append(course)
    return all_courses


ALL_COURSES = load_all_courses()
recommendation_engine = TrainingRecommendationEngine(ALL_COURSES)
feedback_collector = FeedbackCollector(storage_path=DATA_DIR / "data" / "feedback")


# Course Assistant inicializado de forma lazy no startup do FastAPI
course_assistant: CourseAssistant = None  # type: ignore[assignment]


@app.on_event("startup")
async def _init_course_assistant():
    global course_assistant
    from api.llm_helper import create_llm_for_course_assistant

    _llm_provider = create_llm_for_course_assistant()
    course_assistant = CourseAssistant(llm_provider=_llm_provider)

    if _llm_provider:
        logger.info("course_assistant_initialized", mode="llm_powered")
    else:
        logger.info("course_assistant_initialized", mode="simulated")


def get_llm_status() -> str:
    if course_assistant is None:
        return "starting"
    return "llm_powered" if course_assistant.llm_provider else "simulated"


# Models
class EmployeeListItem(BaseModel):
    name: str
    cargo: str
    departamento: str
    nivel: Optional[str] = None


class RecommendationRequest(BaseModel):
    employee_name: str
    top_n: int = 5
    exclude_completed: bool = True


class FeedbackRequest(BaseModel):
    employee_id: int
    employee_name: str
    curso_id: str
    curso_titulo: str
    action: str  # "viewed", "clicked", "enrolled", "dismissed", "rated"
    rating: Optional[float] = None
    metadata: Optional[dict] = None


class CourseAssistantStartRequest(BaseModel):
    session_id: str
    curso_id: str
    employee_id: int
    employee_name: str
    progresso_curso: float = 0.0
    modulo_atual: Optional[str] = None


class CourseAssistantQuestionRequest(BaseModel):
    session_id: str
    curso_id: str
    employee_id: int
    employee_name: str
    question: str
    progresso_curso: float = 0.0
    modulo_atual: Optional[str] = None


# Helpers
def normalize_name(name: str) -> str:
    """Normaliza nome para match com arquivo."""
    import unicodedata
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    return name.lower().replace(" ", "_")


def load_employee_data(employee_name: str):
    """Carrega todos os dados de um colaborador."""
    normalized = normalize_name(employee_name)

    # Avaliação
    avaliacao_path = DATA_DIR / "avaliacoes" / f"avaliacao_{normalized}.json"
    if not avaliacao_path.exists():
        raise HTTPException(status_code=404, detail=f"Avaliação não encontrada para {employee_name}")

    with open(avaliacao_path, "r", encoding="utf-8") as f:
        avaliacao = json.load(f)

    # Cadastro
    cadastro_path = DATA_DIR / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"
    if not cadastro_path.exists():
        raise HTTPException(status_code=404, detail=f"Dados cadastrais não encontrados para {employee_name}")

    with open(cadastro_path, "r", encoding="utf-8") as f:
        cadastro = json.load(f)

    # Treinamentos (opcional)
    treinamento_path = DATA_DIR / "treinamentos" / f"treinamentos_{normalized}.json"
    if treinamento_path.exists():
        with open(treinamento_path, "r", encoding="utf-8") as f:
            treinamentos = json.load(f)
    else:
        treinamentos = {"colaboradores": [], "cursos": [], "matriculas": [], "resultados": []}

    return avaliacao, cadastro, treinamentos


# Endpoints
@app.get("/")
def read_root():
    """Health check."""
    return {
        "status": "ok",
        "service": "TalentBoost API",
        "version": "1.0.0",
        "llm_mode": get_llm_status(),
    }


@app.get("/api/health")
def read_health():
    """Health check detalhado para deploy."""
    return {
        "status": "ok",
        "service": "TalentBoost API",
        "version": "1.0.0",
        "llm_mode": get_llm_status(),
        "allowed_origins": allowed_origins,
        "allow_origin_regex": allow_origin_regex,
        "courses_indexed": len(ALL_COURSES),
    }


@app.get("/api/employees", response_model=list[EmployeeListItem])
def list_employees():
    """Lista todos os colaboradores disponíveis."""
    employees = []
    cadastro_dir = DATA_DIR / "dados_cadastrais"

    for file in cadastro_dir.glob("dadoscadastrais_*.json"):
        if file.name == "dadoscadastrais.json":
            continue

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            employees.append(EmployeeListItem(
                name=data.get("NOME", ""),
                cargo=data.get("CARGO_NOME", ""),
                departamento=data.get("DEPARTAMENTO", ""),
                nivel=None,  # Será inferido da avaliação
            ))

    return sorted(employees, key=lambda e: e.name)


@app.get("/api/employees/{employee_name}/profile")
def get_employee_profile(employee_name: str):
    """Retorna dados cadastrais de um colaborador."""
    _, cadastro, _ = load_employee_data(employee_name)
    return cadastro


@app.get("/api/employees/{employee_name}/evaluation")
def get_employee_evaluation(employee_name: str):
    """Retorna avaliação de desempenho completa."""
    avaliacao, _, _ = load_employee_data(employee_name)
    return avaliacao


@app.get("/api/employees/{employee_name}/gaps")
def analyze_gaps(employee_name: str):
    """Analisa gaps de competências."""
    avaliacao, _, _ = load_employee_data(employee_name)

    # Detecta gaps
    gaps = gap_detector.detect_gaps(avaliacao)

    # Serializa
    gaps_json = [
        {
            "competency_name": g.competency_name,
            "competency_key": g.competency_key,
            "average_score": g.average_score,
            "gap_severity": g.gap_severity,
            "urgency": g.urgency.value,
            "context": g.context,
            "evaluator_consensus": g.evaluator_consensus,
            "development_hints": g.development_hints,
            "key_observations": g.key_observations,
        }
        for g in gaps
    ]

    return {
        "employee_name": employee_name,
        "total_gaps": len(gaps),
        "gaps": gaps_json,
    }


@app.post("/api/employees/{employee_name}/recommendations")
def get_recommendations(employee_name: str, request: RecommendationRequest):
    """Gera recomendações personalizadas de treinamentos."""
    start_time = datetime.now()

    logger.info(
        "recommendation_requested",
        employee_name=employee_name,
        top_n=request.top_n,
        timestamp=start_time.isoformat(),
    )

    avaliacao, cadastro, treinamentos = load_employee_data(employee_name)

    # Detecta gaps
    gaps = gap_detector.detect_gaps(avaliacao)

    # Constrói perfil
    profile = profile_builder.build_profile(
        employee_data=cadastro,
        evaluation_data=avaliacao,
        training_data=treinamentos,
        gaps=gaps,
    )

    # Gera recomendações
    recommendations = recommendation_engine.recommend(
        profile=profile,
        top_n=request.top_n,
        exclude_completed=request.exclude_completed,
    )

    # Serializa com explicabilidade
    recs_json = [
        {
            "curso_id": r.curso_id,
            "titulo": r.titulo,
            "categoria": r.categoria,
            "modalidade": r.modalidade,
            "carga_horaria": r.carga_horaria,
            "obrigatorio": r.obrigatorio,
            "relevance_score": r.relevance_score,
            "match_reason": r.match_reason,
            "addresses_gaps": r.addresses_gaps,
            "priority": r.priority,
            "explanation": {
                "primary_reason": r.explanation.primary_reason,
                "gap_addressed": r.explanation.gap_addressed,
                "secondary_reasons": r.explanation.secondary_reasons,
                "confidence": r.explanation.confidence,
                "similar_employees_count": r.explanation.similar_employees_count,
                "avg_satisfaction": r.explanation.avg_satisfaction,
            } if r.explanation else None,
        }
        for r in recommendations
    ]

    # Resumo
    summary = recommendation_engine.get_recommendation_summary(recommendations)

    # Log de performance
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    logger.info(
        "recommendation_generated",
        employee_name=employee_name,
        recommendations_count=len(recommendations),
        cold_start_used=len(profile.gaps_identificados) == 0,
        avg_relevance=summary.get("average_relevance", 0),
        duration_ms=round(duration_ms, 2),
    )

    return {
        "employee_name": employee_name,
        "profile_summary": {
            "cargo": profile.cargo,
            "nivel": profile.nivel,
            "nota_media_geral": profile.nota_media_geral,
            "pontos_fortes": profile.pontos_fortes,
            "total_gaps": len(profile.gaps_identificados),
        },
        "recommendations": recs_json,
        "summary": summary,
        "metadata": {
            "cold_start_used": len(profile.gaps_identificados) == 0,
            "generation_time_ms": round(duration_ms, 2),
        },
    }


@app.get("/api/employees/{employee_name}/sentiment-analysis")
def get_sentiment_analysis(employee_name: str):
    """Retorna análise de sentimentos das observações."""
    avaliacao, _, _ = load_employee_data(employee_name)

    # Analisa sentimentos
    sentiment_results = sentiment_analyzer.analyze_all_observations(avaliacao)

    # Serializa
    results_json = {}
    for competency_key, analyses in sentiment_results.items():
        results_json[competency_key] = [
            {
                "evaluator_role": role,
                "tone": analysis.tone.value,
                "urgency": analysis.urgency.value,
                "confidence": analysis.confidence,
                "key_phrases": analysis.key_phrases,
                "development_hints": analysis.development_hints,
            }
            for role, analysis in analyses
        ]

    return {
        "employee_name": employee_name,
        "sentiment_analysis": results_json,
    }


@app.get("/api/courses")
def list_courses(category: Optional[str] = None):
    """Lista todos os cursos disponíveis."""
    courses = ALL_COURSES

    if category:
        courses = [c for c in courses if c.get("categoria") == category]

    return {
        "total": len(courses),
        "category_filter": category,
        "courses": courses,
    }


@app.get("/api/stats/overview")
def get_overview_stats():
    """Estatísticas gerais do sistema."""
    # Conta arquivos
    total_employees = len(list((DATA_DIR / "dados_cadastrais").glob("dadoscadastrais_*.json")))
    total_courses = len(ALL_COURSES)

    # Categorias de cursos
    categories = {}
    for course in ALL_COURSES:
        cat = course.get("categoria", "Outros")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_employees": total_employees,
        "total_courses": total_courses,
        "categories": categories,
    }


# ========== NOVOS ENDPOINTS: FEEDBACK & ANALYTICS ==========

@app.post("/api/feedback/track")
def track_feedback(feedback: FeedbackRequest):
    """Registra feedback do usuário sobre recomendações."""
    logger.info(
        "feedback_tracked",
        employee_id=feedback.employee_id,
        curso_id=feedback.curso_id,
        action=feedback.action,
        timestamp=datetime.now().isoformat(),
    )

    feedback_collector.record_interaction(
        employee_id=feedback.employee_id,
        employee_name=feedback.employee_name,
        curso_id=feedback.curso_id,
        curso_titulo=feedback.curso_titulo,
        action=feedback.action,
        rating=feedback.rating,
        metadata=feedback.metadata,
    )

    return {"status": "success", "message": "Feedback registrado"}


@app.get("/api/feedback/employee/{employee_id}")
def get_employee_feedback_history(employee_id: int):
    """Retorna histórico de interações de um colaborador."""
    history = feedback_collector.get_employee_history(employee_id)

    return {
        "employee_id": employee_id,
        "total_interactions": len(history),
        "history": history,
    }


@app.get("/api/analytics/summary")
def get_analytics_summary():
    """Resumo geral de analytics do sistema de recomendação."""
    logger.info("analytics_summary_requested", timestamp=datetime.now().isoformat())

    summary = feedback_collector.get_analytics_summary()

    return summary


@app.get("/api/analytics/course/{curso_id}")
def get_course_analytics(curso_id: str):
    """Analytics detalhado de um curso específico."""
    ctr = feedback_collector.get_click_through_rate(curso_id)
    enrollment_rate = feedback_collector.get_enrollment_rate(curso_id)
    dismissal_rate = feedback_collector.get_dismissal_rate(curso_id)
    avg_rating = feedback_collector.get_average_rating(curso_id)

    return {
        "curso_id": curso_id,
        "click_through_rate": round(ctr, 3),
        "enrollment_rate": round(enrollment_rate, 3),
        "dismissal_rate": round(dismissal_rate, 3),
        "average_rating": round(avg_rating, 2),
    }


@app.get("/api/analytics/popular-courses")
def get_popular_courses(top_n: int = 10):
    """Retorna cursos mais populares (mais cliques)."""
    popular = feedback_collector.get_popular_courses(top_n=top_n)

    return {
        "top_n": top_n,
        "popular_courses": popular,
    }


@app.get("/api/analytics/recommendations-performance")
def get_recommendations_performance():
    """Métricas de performance do sistema de recomendação."""
    summary = feedback_collector.get_analytics_summary()

    # Cache stats
    cache_hits = getattr(recommendation_engine, "_cache", {})
    cache_size = len(cache_hits)

    return {
        "recommendation_stats": summary,
        "cache_stats": {
            "cache_size": cache_size,
            "cache_enabled": recommendation_engine.enable_cache,
            "cache_ttl_seconds": recommendation_engine._cache_ttl,
        },
        "system_info": {
            "total_courses_indexed": len(ALL_COURSES),
            "recommendation_strategies": [
                "content_based",
                "cold_start_fallback",
                "diversity_filter",
                "temporal_decay",
            ],
        },
    }


# ========== COURSE ASSISTANT (Tutor Virtual com LLM) ==========

@app.post("/api/course-assistant/start")
def start_course_assistant_session(request: CourseAssistantStartRequest):
    """
    Inicia uma sessão de assistência com o tutor virtual do curso.

    O Course Assistant é um tutor baseado em LLM que auxilia o aluno
    durante o curso, respondendo dúvidas e oferecendo suporte contextual.
    """
    logger.info(
        "course_assistant_session_started",
        session_id=request.session_id,
        curso_id=request.curso_id,
        employee_id=request.employee_id,
        timestamp=datetime.now().isoformat(),
    )

    # Busca informações do curso (modo geral se curso_id == "general")
    if request.curso_id == "general":
        course_info = {
            "cursoID": "general",
            "titulo": "Assistente TalentBoost",
            "categoria": "Geral",
            "modalidade": "EAD",
            "cargaHoraria": 0,
            "descricao": "Assistente geral para dúvidas sobre treinamentos, recomendações e desenvolvimento profissional.",
        }
    else:
        course_info = next(
            (c for c in ALL_COURSES if c.get("cursoID") == request.curso_id), None
        )
        if not course_info:
            raise HTTPException(status_code=404, detail=f"Curso {request.curso_id} não encontrado")

    # Busca informações do colaborador
    try:
        normalized = normalize_name(request.employee_name)
        cadastro_path = DATA_DIR / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"

        with open(cadastro_path, "r", encoding="utf-8") as f:
            cadastro = json.load(f)

        cargo = cadastro.get("CARGO_NOME", "Colaborador")
        nivel = "Pleno"
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Falha ao carregar dados cadastrais: {e}")
        cargo = "Colaborador"
        nivel = "Pleno"

    # Cria contextos
    course_context = CourseContext(
        curso_id=request.curso_id,
        titulo=course_info.get("titulo", ""),
        categoria=course_info.get("categoria", ""),
        modalidade=course_info.get("modalidade", ""),
        carga_horaria=course_info.get("cargaHoraria", 0),
        descricao=course_info.get("descricao"),
        nivel="Intermediário",  # Placeholder
        objetivos=[
            "Desenvolver competências práticas",
            "Aplicar conhecimentos no dia a dia",
            "Preparar-se para desafios profissionais",
        ],
        topicos=["Fundamentos", "Prática", "Aplicação Avançada"],
    )

    student_context = StudentContext(
        employee_id=request.employee_id,
        nome=request.employee_name,
        cargo=cargo,
        nivel=nivel,
        progresso_curso=request.progresso_curso,
        modulo_atual=request.modulo_atual,
    )

    # Inicia sessão
    welcome_msg = course_assistant.start_session(
        request.session_id, course_context, student_context
    )

    return {
        "session_id": request.session_id,
        "curso_id": request.curso_id,
        "message": {
            "role": welcome_msg.role,
            "content": welcome_msg.content,
            "timestamp": welcome_msg.timestamp,
        },
        "status": "session_started",
    }


@app.post("/api/course-assistant/ask")
def ask_course_assistant(request: CourseAssistantQuestionRequest):
    """
    Faz uma pergunta ao tutor virtual do curso.

    O assistente responde com base no contexto do curso e do aluno,
    adaptando a explicação ao nível profissional e progresso no curso.
    """
    logger.info(
        "course_assistant_question",
        session_id=request.session_id,
        curso_id=request.curso_id,
        employee_id=request.employee_id,
        question_length=len(request.question),
        timestamp=datetime.now().isoformat(),
    )

    # Busca informações do curso (modo geral se curso_id == "general")
    if request.curso_id == "general":
        course_info = {
            "cursoID": "general",
            "titulo": "Assistente TalentBoost",
            "categoria": "Geral",
            "modalidade": "EAD",
            "cargaHoraria": 0,
        }
    else:
        course_info = next(
            (c for c in ALL_COURSES if c.get("cursoID") == request.curso_id), None
        )
        if not course_info:
            raise HTTPException(status_code=404, detail=f"Curso {request.curso_id} não encontrado")

    # Busca informações do colaborador
    try:
        normalized = normalize_name(request.employee_name)
        cadastro_path = DATA_DIR / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"

        with open(cadastro_path, "r", encoding="utf-8") as f:
            cadastro = json.load(f)

        cargo = cadastro.get("CARGO_NOME", "Colaborador")
        nivel = "Pleno"
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Falha ao carregar dados cadastrais: {e}")
        cargo = "Colaborador"
        nivel = "Pleno"

    # Cria contextos
    course_context = CourseContext(
        curso_id=request.curso_id,
        titulo=course_info.get("titulo", ""),
        categoria=course_info.get("categoria", ""),
        modalidade=course_info.get("modalidade", ""),
        carga_horaria=course_info.get("cargaHoraria", 0),
        nivel="Intermediário",
        objetivos=[
            "Desenvolver competências práticas",
            "Aplicar conhecimentos no dia a dia",
        ],
        topicos=["Fundamentos", "Prática", "Aplicação"],
    )

    student_context = StudentContext(
        employee_id=request.employee_id,
        nome=request.employee_name,
        cargo=cargo,
        nivel=nivel,
        progresso_curso=request.progresso_curso,
        modulo_atual=request.modulo_atual,
    )

    # Processa pergunta
    response_msg = course_assistant.ask(
        request.session_id, request.question, course_context, student_context
    )

    return {
        "session_id": request.session_id,
        "question": request.question,
        "response": {
            "role": response_msg.role,
            "content": response_msg.content,
            "timestamp": response_msg.timestamp,
            "metadata": response_msg.metadata,
        },
    }


@app.get("/api/course-assistant/history/{session_id}")
def get_course_assistant_history(session_id: str):
    """Retorna histórico de conversa com o assistente."""
    history = course_assistant.get_conversation_history(session_id)

    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "metadata": msg.metadata,
            }
            for msg in history
            if msg.role != "system"  # Não expõe system prompt
        ],
    }


@app.post("/api/course-assistant/suggestions")
def get_course_assistant_suggestions(request: CourseAssistantStartRequest):
    """Sugere próximos passos baseado no progresso do aluno."""
    # Busca informações do curso (modo geral se curso_id == "general")
    if request.curso_id == "general":
        return {
            "suggestions": [
                "Quais cursos são recomendados para mim?",
                "Como funciona o sistema de recomendação?",
                "Quais competências devo desenvolver?",
                "Como acompanho meu progresso?",
            ]
        }

    course_info = next(
        (c for c in ALL_COURSES if c.get("cursoID") == request.curso_id), None
    )

    if not course_info:
        raise HTTPException(status_code=404, detail=f"Curso {request.curso_id} não encontrado")

    # Busca informações do colaborador
    try:
        normalized = normalize_name(request.employee_name)
        cadastro_path = DATA_DIR / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"

        with open(cadastro_path, "r", encoding="utf-8") as f:
            cadastro = json.load(f)

        cargo = cadastro.get("CARGO_NOME", "Colaborador")
        nivel = "Pleno"
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Falha ao carregar dados cadastrais: {e}")
        cargo = "Colaborador"
        nivel = "Pleno"

    course_context = CourseContext(
        curso_id=request.curso_id,
        titulo=course_info.get("titulo", ""),
        categoria=course_info.get("categoria", ""),
        modalidade=course_info.get("modalidade", ""),
        carga_horaria=course_info.get("cargaHoraria", 0),
        nivel="Intermediário",
    )

    student_context = StudentContext(
        employee_id=request.employee_id,
        nome=request.employee_name,
        cargo=cargo,
        nivel=nivel,
        progresso_curso=request.progresso_curso,
        modulo_atual=request.modulo_atual,
    )

    suggestions = course_assistant.suggest_next_steps(course_context, student_context)

    return {
        "curso_id": request.curso_id,
        "employee_id": request.employee_id,
        "progresso": request.progresso_curso,
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
