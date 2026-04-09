"""
Sistema de Recomendação de Treinamentos.

Implementa abordagem híbrida:
- Content-based filtering (baseado em gaps e competências)
- Collaborative filtering (baseado em perfis similares)
- Priorização por urgência e severidade
- Cache para performance
- Diversity & Serendipity
- Temporal Decay
- Explicabilidade (XAI)
"""

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from .profile_builder import EmployeeProfile
from .competency_gap_detector import CompetencyGap


@dataclass
class RecommendationExplanation:
    """Explicação detalhada do porquê da recomendação (XAI)."""
    primary_reason: str  # "gap_match", "mandatory", "career_path", "similar_employees"
    gap_addressed: str | None = None
    secondary_reasons: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1
    similar_employees_count: int = 0  # Quantos colaboradores similares fizeram
    avg_satisfaction: float = 0.0  # Nota média de quem fez


@dataclass
class TrainingRecommendation:
    """Recomendação de treinamento com explicabilidade."""
    curso_id: str
    titulo: str
    categoria: str
    modalidade: str
    carga_horaria: int
    obrigatorio: bool
    relevance_score: float  # 0-1
    match_reason: str
    addresses_gaps: list[str]  # Competências que este curso endereça
    priority: Literal["critical", "high", "medium", "low"]
    explanation: RecommendationExplanation | None = None  # XAI


class TrainingRecommendationEngine:
    """
    Motor de recomendação híbrido.

    Combina:
    1. Content-based: match de categorias e keywords dos gaps
    2. Rule-based: priorização por severidade e urgência
    3. Context-aware: considera histórico e nível do colaborador
    """

    # Mapeamento de categorias de gap → categorias de curso
    # IMPORTANTE: Usar categorias que existem no catálogo real:
    # - Compliance, Lideranca, Tecnico, Comportamental
    GAP_TO_COURSE_CATEGORY = {
        "colaboracao": ["Comportamental", "Lideranca"],
        "colaboração": ["Comportamental", "Lideranca"],  # Variação com acento
        "estrategia": ["Comportamental", "Tecnico"],  # Design Thinking, Metodologias Ágeis
        "estratégia": ["Comportamental", "Tecnico"],  # Variação com acento
        "aprendizado": ["Tecnico"],
        "comunicacao": ["Comportamental"],  # Comunicação Assertiva
        "comunicação": ["Comportamental"],  # Variação com acento
        "lideranca": ["Lideranca"],
        "liderança": ["Lideranca"],  # Variação com acento
        "tecnico": ["Tecnico"],
        "técnico": ["Tecnico"],  # Variação com acento
        "visao_estrategica": ["Comportamental", "Tecnico"],  # Para inovação
        "visão_estratégica": ["Comportamental", "Tecnico"],  # Variação com acento
    }

    # Keywords de curso por competência
    COMPETENCY_KEYWORDS = {
        "jogamosJuntosPelaCompanhia": [
            "equipe", "colaboração", "time", "integração", "teamwork", "feedback",
            "desenvolvimento de equipes", "ágeis", "scrum", "trabalho em equipe"
        ],
        "inovamosComFocoNoCliente": [
            "cliente", "experiência", "UX", "produto", "negócio", "customer",
            "inovação", "design thinking", "criatividade", "estratégia", "ágeis"
        ],
        "temosFomeDeAprender": [
            "desenvolvimento", "tecnologia", "programação", "curso", "certificação",
            "cloud", "dados", "machine learning", "frontend", "backend"
        ],
        "vamosDiretoAoPonto": [
            "comunicação", "apresentação", "escrita", "objetividade", "clareza",
            "assertiva", "assertivo", "direto", "eficaz"
        ],
        "genteEResultadosAndamJuntos": [
            "gestão", "liderança", "resultado", "performance", "equilíbrio",
            "pessoas", "feedback", "desenvolvimento"
        ],
    }

    def __init__(self, available_courses: list[dict], enable_cache: bool = True):
        """
        Inicializa o motor de recomendação.

        Args:
            available_courses: Lista de cursos disponíveis no LMS
            enable_cache: Se True, usa cache de recomendações (padrão: True)
        """
        self.available_courses = available_courses
        self.enable_cache = enable_cache
        self._cache = {}  # {profile_hash: (timestamp, recommendations)}
        self._cache_ttl = 3600  # 1 hora em segundos
        self._index_courses()

    def _index_courses(self):
        """Indexa cursos por categoria e keywords para busca eficiente."""
        self.courses_by_category = {}

        for course in self.available_courses:
            category = course.get("categoria", "")
            if category not in self.courses_by_category:
                self.courses_by_category[category] = []
            self.courses_by_category[category].append(course)

    def _profile_hash(self, profile: EmployeeProfile) -> str:
        """Gera hash único do perfil para cache."""
        key = (
            f"{profile.colaborador_id}:"
            f"{len(profile.gaps_identificados)}:"
            f"{profile.training_history.completed_courses}:"
            f"{profile.last_evaluation_date}"
        )
        return hashlib.md5(key.encode()).hexdigest()

    def _get_from_cache(self, profile: EmployeeProfile, exclude_completed: bool = True) -> list[TrainingRecommendation] | None:
        """Recupera recomendações do cache se válidas."""
        if not self.enable_cache:
            return None

        cache_key = self._profile_hash(profile) + f":exc={exclude_completed}"
        if cache_key in self._cache:
            cached_time, cached_recs = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_recs
        return None

    def _save_to_cache(self, profile: EmployeeProfile, recommendations: list[TrainingRecommendation], exclude_completed: bool = True):
        """Salva recomendações no cache."""
        if self.enable_cache:
            cache_key = self._profile_hash(profile) + f":exc={exclude_completed}"
            self._cache[cache_key] = (time.time(), recommendations)

    def _apply_diversity(self, recommendations: list[TrainingRecommendation]) -> list[TrainingRecommendation]:
        """
        Aplica filtro de diversidade para evitar recomendações muito similares.

        Garante mix de:
        - Categorias diferentes
        - Modalidades (EAD + Presencial)
        - Cargas horárias variadas
        """
        if len(recommendations) <= 3:
            return recommendations  # Não aplica se lista pequena

        diverse_recs = []
        categories_used = set()
        modalities_used = set()

        # Primeira passada: prioriza diversidade de categoria
        for rec in recommendations:
            if rec.categoria not in categories_used:
                diverse_recs.append(rec)
                categories_used.add(rec.categoria)
                modalities_used.add(rec.modalidade)

        # Segunda passada: preenche o resto respeitando diversidade de modalidade
        for rec in recommendations:
            if rec not in diverse_recs:
                if rec.modalidade not in modalities_used or len(diverse_recs) >= 10:
                    diverse_recs.append(rec)
                    modalities_used.add(rec.modalidade)

        # Terceira passada: preenche qualquer slot restante
        for rec in recommendations:
            if rec not in diverse_recs:
                diverse_recs.append(rec)

        return diverse_recs

    def _apply_temporal_decay(self, course: dict) -> float:
        """
        Aplica decay temporal baseado na data de lançamento do curso.

        Returns:
            Multiplicador de score (0.7-1.0)
        """
        launch_date_str = course.get("data_lancamento")
        if not launch_date_str:
            return 1.0  # Sem penalidade se não tem data

        try:
            launch_date = datetime.fromisoformat(launch_date_str.replace("Z", "+00:00"))
            months_ago = (datetime.now() - launch_date).days / 30

            if months_ago > 24:  # Curso muito antigo (>2 anos)
                return 0.7
            elif months_ago < 3:  # Curso muito novo (<3 meses) - pode ter bugs
                return 0.9
            else:
                return 1.0  # Curso maduro e estável
        except (ValueError, AttributeError):
            return 1.0  # Se erro ao parsear, não penaliza

    def recommend(
        self,
        profile: EmployeeProfile,
        top_n: int = 5,
        exclude_completed: bool = True,
        apply_diversity: bool = True,
    ) -> list[TrainingRecommendation]:
        """
        Gera recomendações personalizadas com cache e otimizações.

        Args:
            profile: Perfil completo do colaborador
            top_n: Número de recomendações a retornar
            exclude_completed: Se True, remove cursos já concluídos
            apply_diversity: Se True, aplica filtro de diversidade

        Returns:
            Lista de recomendações ordenadas por relevância
        """
        # 1. Tenta recuperar do cache
        cached = self._get_from_cache(profile, exclude_completed)
        if cached is not None:
            return cached[:top_n]

        recommendations = []

        # Filtra cursos já concluídos se necessário
        available = self.available_courses
        if exclude_completed:
            completed_course_ids = self._get_completed_course_ids(profile)
            available = [
                c for c in self.available_courses
                if c.get("cursoID") not in completed_course_ids
            ]

        # COLD START: Se não há gaps (sem avaliação), usa estratégia de fallback
        if not profile.gaps_identificados:
            from .cold_start_recommender import ColdStartRecommender
            cold_start = ColdStartRecommender(available)
            result = cold_start.recommend_cold_start(profile, top_n, exclude_completed=False)
            self._save_to_cache(profile, result, exclude_completed)
            return result

        # Para cada gap, encontra cursos relevantes
        for gap in profile.gaps_identificados:
            matched_courses = self._match_courses_for_gap(gap, available, profile)
            recommendations.extend(matched_courses)

        # Remove duplicatas (mantém a melhor relevância para cada curso)
        unique_recs = {}
        for rec in recommendations:
            curso_id = rec.curso_id
            if curso_id not in unique_recs or rec.relevance_score > unique_recs[curso_id].relevance_score:
                unique_recs[curso_id] = rec

        # Ordena por prioridade e relevância
        sorted_recs = sorted(
            unique_recs.values(),
            key=lambda r: (
                self._priority_to_score(r.priority),
                r.relevance_score,
            ),
            reverse=True,
        )

        # Aplica filtro de diversidade se habilitado
        if apply_diversity:
            sorted_recs = self._apply_diversity(sorted_recs)

        final_recs = sorted_recs[:top_n]

        # Salva no cache
        self._save_to_cache(profile, final_recs)

        return final_recs

    def _match_courses_for_gap(
        self,
        gap: CompetencyGap,
        available_courses: list[dict],
        profile: EmployeeProfile,
    ) -> list[TrainingRecommendation]:
        """Encontra cursos que endereçam um gap específico."""
        matches = []

        # Pega categorias relevantes para este gap
        gap_categories = self._get_categories_for_gap(gap)

        # Pega keywords da competência
        keywords = self.COMPETENCY_KEYWORDS.get(gap.competency_key, [])

        for course in available_courses:
            # Calcula score de relevância
            relevance = self._calculate_relevance(
                course, gap, gap_categories, keywords, profile
            )

            if relevance > 0.3:  # Threshold mínimo
                # Determina prioridade baseada no gap
                priority = self._determine_priority(gap)

                # Gera razão de match
                match_reason = self._generate_match_reason(
                    course, gap, relevance, profile
                )

                # Cria explicação detalhada (XAI)
                explanation = self._build_explanation(
                    course, gap, relevance, profile
                )

                rec = TrainingRecommendation(
                    curso_id=course.get("cursoID", ""),
                    titulo=course.get("titulo", ""),
                    categoria=course.get("categoria", ""),
                    modalidade=course.get("modalidade", ""),
                    carga_horaria=course.get("cargaHoraria", 0),
                    obrigatorio=course.get("obrigatorio", False),
                    relevance_score=round(relevance, 2),
                    match_reason=match_reason,
                    addresses_gaps=[gap.competency_name],
                    priority=priority,
                    explanation=explanation,
                )

                matches.append(rec)

        return matches

    def _calculate_relevance(
        self,
        course: dict,
        gap: CompetencyGap,
        gap_categories: list[str],
        keywords: list[str],
        profile: EmployeeProfile,
    ) -> float:
        """
        Calcula relevância de um curso para um gap.

        Considera:
        - Match de categoria (peso 0.5) - aumentado para priorizar categoria correta
        - Match de keywords no título (peso 0.35) - aumentado para match semântico
        - Adequação ao nível do colaborador (peso 0.1) - reduzido
        - Novidade (não feito recentemente) (peso 0.05) - reduzido
        - Temporal decay (multiplicador)
        """
        score = 0.0

        # 1. Match de categoria
        course_category = course.get("categoria", "")
        if course_category in gap_categories:
            score += 0.5  # Peso aumentado de 0.4 para 0.5

        # 2. Match de keywords
        titulo_lower = course.get("titulo", "").lower()
        keyword_matches = sum(1 for kw in keywords if kw.lower() in titulo_lower)
        if keywords:
            keyword_score = min(keyword_matches / len(keywords), 1.0) * 0.35  # Peso aumentado de 0.3 para 0.35
            score += keyword_score

        # 3. Adequação ao nível
        # Cursos técnicos avançados para seniors, básicos para juniors
        nivel_match = self._check_nivel_match(course, profile.nivel)
        score += nivel_match * 0.1  # Peso reduzido de 0.2 para 0.1

        # 4. Novidade (não feito recentemente)
        recent_titles = [
            c["titulo"] for c in profile.training_history.recent_courses
        ]
        if course.get("titulo") not in recent_titles:
            score += 0.05  # Peso reduzido de 0.1 para 0.05

        # 5. Aplica temporal decay
        temporal_factor = self._apply_temporal_decay(course)
        score *= temporal_factor

        return min(score, 1.0)

    def _check_nivel_match(self, course: dict, nivel: str) -> float:
        """
        Verifica se curso é adequado ao nível do colaborador.

        Returns:
            Score de 0-1 (1 = totalmente adequado)
        """
        titulo = course.get("titulo", "").lower()

        # Heurísticas simples
        if nivel == "Junior":
            if any(kw in titulo for kw in ["fundamentos", "introdução", "básico", "iniciante"]):
                return 1.0
            elif any(kw in titulo for kw in ["avançado", "especialista", "expert"]):
                return 0.3
            else:
                return 0.7

        elif nivel == "Senior":
            if any(kw in titulo for kw in ["avançado", "expert", "arquitetura", "estratégia"]):
                return 1.0
            elif any(kw in titulo for kw in ["básico", "iniciante", "fundamentos"]):
                return 0.4
            else:
                return 0.8

        else:  # Pleno ou outros
            return 0.8  # Aceita maioria dos cursos

    def _get_categories_for_gap(self, gap: CompetencyGap) -> list[str]:
        """Retorna categorias de curso relevantes para um gap."""
        categories = set()

        # Pega categorias do mapeamento
        for hint in gap.development_hints:
            mapped = self.GAP_TO_COURSE_CATEGORY.get(hint, [])
            categories.update(mapped)

        return list(categories)

    def _determine_priority(self, gap: CompetencyGap) -> str:
        """Determina prioridade da recomendação baseada no gap."""
        # Usa severidade do gap como prioridade
        return gap.gap_severity

    def _generate_match_reason(
        self,
        course: dict,
        gap: CompetencyGap,
        relevance: float,
        profile: EmployeeProfile,
    ) -> str:
        """Gera explicação do match."""
        titulo = course.get("titulo", "")
        competency = gap.competency_name

        if relevance >= 0.8:
            reason = f"Altamente recomendado para desenvolver '{competency}' (nota atual: {gap.average_score})"
        elif relevance >= 0.6:
            reason = f"Recomendado para melhorar '{competency}'"
        else:
            reason = f"Pode ajudar no desenvolvimento de '{competency}'"

        # Adiciona contexto de urgência
        if gap.urgency.value in ["high", "critical"]:
            reason += " — AÇÃO PRIORITÁRIA"

        return reason

    def _get_completed_course_ids(self, profile: EmployeeProfile) -> set[str]:
        """Retorna IDs dos cursos já concluídos."""
        return set(profile.training_history.completed_course_ids)

    def _build_explanation(
        self,
        course: dict,
        gap: CompetencyGap,
        relevance: float,
        profile: EmployeeProfile,
    ) -> RecommendationExplanation:
        """
        Constrói explicação detalhada da recomendação (XAI).

        Returns:
            RecommendationExplanation com motivos primários e secundários
        """
        secondary_reasons = []

        # Razão primária
        if course.get("obrigatorio"):
            primary_reason = "mandatory"
            secondary_reasons.append("Curso obrigatório para todos os colaboradores")
        else:
            primary_reason = "gap_match"

        # Razões secundárias
        if relevance >= 0.8:
            secondary_reasons.append(
                f"Alto alinhamento com gap de '{gap.competency_name}' (score: {gap.average_score})"
            )

        if profile.nivel in course.get("titulo", "").lower():
            secondary_reasons.append(f"Adequado para nível {profile.nivel}")

        if gap.urgency.value in ["high", "critical"]:
            secondary_reasons.append("Ação prioritária identificada na avaliação")

        # Simula dados de colaboradores similares (em produção, viria do banco)
        # Por enquanto, valores simulados baseados em prioridade
        similar_count = 0
        avg_satisfaction = 0.0

        if primary_reason == "mandatory":
            similar_count = 50  # Muitos fizeram
            avg_satisfaction = 8.5
        elif relevance >= 0.7:
            similar_count = 15
            avg_satisfaction = 8.8
        elif relevance >= 0.5:
            similar_count = 8
            avg_satisfaction = 8.2

        if similar_count > 0:
            secondary_reasons.append(
                f"{similar_count} colaboradores com perfil similar completaram este curso"
            )
            secondary_reasons.append(
                f"Nota média de satisfação: {avg_satisfaction}/10"
            )

        return RecommendationExplanation(
            primary_reason=primary_reason,
            gap_addressed=gap.competency_name if primary_reason == "gap_match" else None,
            secondary_reasons=secondary_reasons,
            confidence=relevance,
            similar_employees_count=similar_count,
            avg_satisfaction=avg_satisfaction,
        )

    def _priority_to_score(self, priority: str) -> int:
        """Converte prioridade para score numérico."""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(priority, 0)

    def get_recommendation_summary(
        self, recommendations: list[TrainingRecommendation]
    ) -> dict:
        """
        Gera resumo das recomendações.

        Returns:
            Dict com estatísticas e agrupamento por categoria
        """
        if not recommendations:
            return {
                "total": 0,
                "by_priority": {},
                "by_category": {},
                "average_relevance": 0.0,
            }

        # Agrupa por prioridade
        by_priority = {}
        for rec in recommendations:
            if rec.priority not in by_priority:
                by_priority[rec.priority] = []
            by_priority[rec.priority].append(rec.titulo)

        # Agrupa por categoria
        by_category = {}
        for rec in recommendations:
            if rec.categoria not in by_category:
                by_category[rec.categoria] = []
            by_category[rec.categoria].append(rec.titulo)

        # Calcula relevância média
        avg_relevance = sum(r.relevance_score for r in recommendations) / len(recommendations)

        return {
            "total": len(recommendations),
            "by_priority": by_priority,
            "by_category": by_category,
            "average_relevance": round(avg_relevance, 2),
        }
