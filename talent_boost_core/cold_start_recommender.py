"""
Cold Start Recommender - Sistema de fallback para novos colaboradores.

Recomenda cursos quando não há avaliação de desempenho disponível,
baseando-se apenas em dados cadastrais.
"""

from dataclasses import dataclass
from typing import Literal

from .profile_builder import EmployeeProfile


@dataclass
class ColdStartRecommendation:
    """Recomendação baseada em perfil cadastral."""
    curso_id: str
    titulo: str
    categoria: str
    modalidade: str
    carga_horaria: int
    obrigatorio: bool
    relevance_score: float
    match_reason: str
    recommendation_type: Literal["obrigatorio", "cargo", "nivel", "departamento"]
    priority: Literal["critical", "high", "medium", "low"]


class ColdStartRecommender:
    """
    Recomendador para cold start (sem avaliação de desempenho).

    Estratégias de fallback (em ordem):
    1. Cursos obrigatórios não concluídos
    2. Cursos por cargo (matching de keywords)
    3. Cursos por nível (Junior → fundamentos, Senior → avançado)
    4. Cursos por departamento
    """

    # Mapeamento cargo → keywords de cursos relevantes
    CARGO_KEYWORDS = {
        "desenvolvedor": ["programação", "código", "git", "desenvolvimento"],
        "backend": ["api", "banco de dados", "python", "java", "node"],
        "frontend": ["react", "javascript", "css", "html", "ui"],
        "qa": ["teste", "qualidade", "automação", "selenium"],
        "designer": ["ux", "ui", "design", "figma", "prototipagem"],
        "analista": ["análise", "dados", "sql", "excel", "relatório"],
        "gestor": ["liderança", "gestão", "equipe", "estratégia"],
        "gerente": ["gestão", "liderança", "projetos", "resultados"],
    }

    # Mapeamento departamento → categorias de cursos
    DEPARTAMENTO_CATEGORIES = {
        "tecnologia": ["Tecnico", "Desenvolvimento Profissional"],
        "rh": ["Soft Skills", "Lideranca", "Gestao"],
        "vendas": ["Comunicacao", "Negocios", "Soft Skills"],
        "marketing": ["Comunicacao", "Negocios"],
        "financeiro": ["Gestao", "Compliance"],
        "qualidade": ["Tecnico", "Compliance"],
    }

    def __init__(self, available_courses: list[dict]):
        """
        Inicializa o recomendador de cold start.

        Args:
            available_courses: Lista de cursos disponíveis
        """
        self.available_courses = available_courses

    def recommend_cold_start(
        self,
        profile: EmployeeProfile,
        top_n: int = 5,
        exclude_completed: bool = True,
    ) -> list[ColdStartRecommendation]:
        """
        Gera recomendações para cold start (sem avaliação).

        Args:
            profile: Perfil do colaborador (sem gaps)
            top_n: Número de recomendações
            exclude_completed: Excluir cursos já feitos

        Returns:
            Lista de recomendações baseadas em perfil
        """
        recommendations = []

        # Filtra cursos completados
        available = self.available_courses
        if exclude_completed:
            completed_titles = [c["titulo"] for c in profile.training_history.recent_courses]
            available = [
                c for c in self.available_courses
                if c.get("titulo") not in completed_titles
            ]

        # 1. Cursos obrigatórios (máxima prioridade)
        mandatory_recs = self._recommend_mandatory(available, profile)
        recommendations.extend(mandatory_recs)

        # 2. Cursos por cargo
        if len(recommendations) < top_n:
            cargo_recs = self._recommend_by_cargo(available, profile)
            recommendations.extend(cargo_recs)

        # 3. Cursos por nível
        if len(recommendations) < top_n:
            nivel_recs = self._recommend_by_nivel(available, profile)
            recommendations.extend(nivel_recs)

        # 4. Cursos por departamento
        if len(recommendations) < top_n:
            dept_recs = self._recommend_by_departamento(available, profile)
            recommendations.extend(dept_recs)

        # Remove duplicatas mantendo a primeira (maior prioridade)
        unique_recs = {}
        for rec in recommendations:
            if rec.curso_id not in unique_recs:
                unique_recs[rec.curso_id] = rec

        # Ordena por prioridade e relevância
        sorted_recs = sorted(
            unique_recs.values(),
            key=lambda r: (
                self._priority_to_score(r.priority),
                self._type_to_score(r.recommendation_type),
                r.relevance_score,
            ),
            reverse=True,
        )

        return sorted_recs[:top_n]

    def _recommend_mandatory(
        self, available: list[dict], profile: EmployeeProfile
    ) -> list[ColdStartRecommendation]:
        """Recomenda cursos obrigatórios."""
        recs = []

        for course in available:
            if course.get("obrigatorio", False):
                rec = ColdStartRecommendation(
                    curso_id=course.get("cursoID", ""),
                    titulo=course.get("titulo", ""),
                    categoria=course.get("categoria", ""),
                    modalidade=course.get("modalidade", ""),
                    carga_horaria=course.get("cargaHoraria", 0),
                    obrigatorio=True,
                    relevance_score=1.0,
                    match_reason="Curso obrigatório para todos os colaboradores",
                    recommendation_type="obrigatorio",
                    priority="critical",
                )
                recs.append(rec)

        return recs

    def _recommend_by_cargo(
        self, available: list[dict], profile: EmployeeProfile
    ) -> list[ColdStartRecommendation]:
        """Recomenda cursos baseados no cargo."""
        recs = []
        cargo_lower = profile.cargo.lower()

        # Encontra keywords relevantes para o cargo
        relevant_keywords = []
        for cargo_key, keywords in self.CARGO_KEYWORDS.items():
            if cargo_key in cargo_lower:
                relevant_keywords.extend(keywords)

        if not relevant_keywords:
            return recs

        for course in available:
            titulo_lower = course.get("titulo", "").lower()

            # Calcula match de keywords
            matches = sum(1 for kw in relevant_keywords if kw in titulo_lower)
            if matches > 0:
                relevance = min(matches / len(relevant_keywords), 1.0)

                # Ajusta relevância por nível
                relevance *= self._adjust_for_nivel(course, profile.nivel)

                if relevance > 0.3:
                    rec = ColdStartRecommendation(
                        curso_id=course.get("cursoID", ""),
                        titulo=course.get("titulo", ""),
                        categoria=course.get("categoria", ""),
                        modalidade=course.get("modalidade", ""),
                        carga_horaria=course.get("cargaHoraria", 0),
                        obrigatorio=course.get("obrigatorio", False),
                        relevance_score=round(relevance, 2),
                        match_reason=f"Recomendado para {profile.cargo} ({profile.nivel})",
                        recommendation_type="cargo",
                        priority="high",
                    )
                    recs.append(rec)

        return recs

    def _recommend_by_nivel(
        self, available: list[dict], profile: EmployeeProfile
    ) -> list[ColdStartRecommendation]:
        """Recomenda cursos baseados no nível."""
        recs = []
        nivel = profile.nivel

        for course in available:
            titulo_lower = course.get("titulo", "").lower()

            # Junior → fundamentos, básico
            if nivel == "Junior":
                if any(kw in titulo_lower for kw in ["fundamentos", "básico", "iniciante", "introdução"]):
                    relevance = 0.8
                elif "avançado" in titulo_lower or "expert" in titulo_lower:
                    continue  # Pula cursos avançados
                else:
                    relevance = 0.5

            # Senior → avançado, arquitetura
            elif nivel == "Senior":
                if any(kw in titulo_lower for kw in ["avançado", "expert", "arquitetura", "estratégia"]):
                    relevance = 0.8
                elif "básico" in titulo_lower or "iniciante" in titulo_lower:
                    continue  # Pula cursos básicos
                else:
                    relevance = 0.6

            # Pleno → qualquer
            else:
                relevance = 0.6

            rec = ColdStartRecommendation(
                curso_id=course.get("cursoID", ""),
                titulo=course.get("titulo", ""),
                categoria=course.get("categoria", ""),
                modalidade=course.get("modalidade", ""),
                carga_horaria=course.get("cargaHoraria", 0),
                obrigatorio=course.get("obrigatorio", False),
                relevance_score=relevance,
                match_reason=f"Adequado para nível {nivel}",
                recommendation_type="nivel",
                priority="medium",
            )
            recs.append(rec)

        return recs

    def _recommend_by_departamento(
        self, available: list[dict], profile: EmployeeProfile
    ) -> list[ColdStartRecommendation]:
        """Recomenda cursos baseados no departamento."""
        recs = []
        dept_lower = profile.departamento.lower()

        # Encontra categorias relevantes
        relevant_categories = []
        for dept_key, categories in self.DEPARTAMENTO_CATEGORIES.items():
            if dept_key in dept_lower:
                relevant_categories.extend(categories)

        if not relevant_categories:
            return recs

        for course in available:
            if course.get("categoria") in relevant_categories:
                rec = ColdStartRecommendation(
                    curso_id=course.get("cursoID", ""),
                    titulo=course.get("titulo", ""),
                    categoria=course.get("categoria", ""),
                    modalidade=course.get("modalidade", ""),
                    carga_horaria=course.get("cargaHoraria", 0),
                    obrigatorio=course.get("obrigatorio", False),
                    relevance_score=0.6,
                    match_reason=f"Recomendado para {profile.departamento}",
                    recommendation_type="departamento",
                    priority="medium",
                )
                recs.append(rec)

        return recs

    def _adjust_for_nivel(self, course: dict, nivel: str) -> float:
        """Ajusta relevância baseado no nível."""
        titulo = course.get("titulo", "").lower()

        if nivel == "Junior":
            if any(kw in titulo for kw in ["fundamentos", "básico"]):
                return 1.0
            elif "avançado" in titulo:
                return 0.3
            return 0.7

        elif nivel == "Senior":
            if "avançado" in titulo or "expert" in titulo:
                return 1.0
            elif "básico" in titulo:
                return 0.4
            return 0.8

        return 0.8

    def _priority_to_score(self, priority: str) -> int:
        """Converte prioridade para score."""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(priority, 0)

    def _type_to_score(self, rec_type: str) -> int:
        """Converte tipo de recomendação para score."""
        scores = {"obrigatorio": 4, "cargo": 3, "nivel": 2, "departamento": 1}
        return scores.get(rec_type, 0)
