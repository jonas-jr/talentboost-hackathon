"""
Collaborative Filtering - Recomenda baseado em colaboradores similares.

Encontra colaboradores com perfil similar e recomenda cursos que foram
bem-sucedidos para eles.
"""

from dataclasses import dataclass
from typing import Literal

from .profile_builder import EmployeeProfile


@dataclass
class SimilarEmployee:
    """Colaborador similar com score de similaridade."""
    colaborador_id: int
    nome: str
    cargo: str
    nivel: str
    similarity_score: float  # 0-1
    successful_courses: list[dict]  # Cursos que completou com sucesso


@dataclass
class CollaborativeRecommendation:
    """Recomendação baseada em filtro colaborativo."""
    curso_id: str
    titulo: str
    categoria: str
    modalidade: str
    carga_horaria: int
    relevance_score: float
    recommended_by_similar: int  # Quantos similares recomendam
    avg_score_by_similar: float  # Nota média de quem fez
    similarity_reason: str


class CollaborativeFilter:
    """
    Filtro Colaborativo para recomendações.

    Estratégia:
    1. Encontra colaboradores similares (mesmo cargo + nível + gaps parecidos)
    2. Identifica cursos que foram bem-sucedidos para eles
    3. Recomenda esses cursos para o colaborador atual
    """

    def __init__(self, all_employees: list[dict]):
        """
        Inicializa o filtro colaborativo.

        Args:
            all_employees: Lista de todos os colaboradores com histórico
        """
        self.all_employees = all_employees

    def find_similar_employees(
        self,
        profile: EmployeeProfile,
        top_n: int = 5,
    ) -> list[SimilarEmployee]:
        """
        Encontra colaboradores similares ao perfil fornecido.

        Similaridade baseada em:
        - Mesmo cargo (peso 0.4)
        - Mesmo nível ou adjacente (peso 0.3)
        - Mesmo departamento (peso 0.2)
        - Gaps similares (peso 0.1)

        Args:
            profile: Perfil do colaborador alvo
            top_n: Número de similares a retornar

        Returns:
            Lista de colaboradores similares ordenados por score
        """
        similar = []

        for emp in self.all_employees:
            # Não compara consigo mesmo
            if emp.get("colaborador_id") == profile.colaborador_id:
                continue

            similarity = self._calculate_similarity(profile, emp)

            if similarity > 0.5:  # Threshold mínimo de similaridade
                similar.append(
                    SimilarEmployee(
                        colaborador_id=emp.get("colaborador_id", 0),
                        nome=emp.get("nome", ""),
                        cargo=emp.get("cargo", ""),
                        nivel=emp.get("nivel", ""),
                        similarity_score=round(similarity, 2),
                        successful_courses=self._get_successful_courses(emp),
                    )
                )

        # Ordena por similaridade
        similar.sort(key=lambda x: x.similarity_score, reverse=True)

        return similar[:top_n]

    def recommend_from_similar(
        self,
        profile: EmployeeProfile,
        top_n: int = 5,
        min_endorsements: int = 2,
    ) -> list[CollaborativeRecommendation]:
        """
        Recomenda cursos baseado em colaboradores similares.

        Args:
            profile: Perfil do colaborador alvo
            top_n: Número de recomendações
            min_endorsements: Mínimo de similares que devem ter feito o curso

        Returns:
            Lista de recomendações colaborativas
        """
        # Encontra similares
        similar_employees = self.find_similar_employees(profile, top_n=10)

        if not similar_employees:
            return []  # Sem similares suficientes

        # Agrega cursos bem-sucedidos de todos os similares
        course_stats = {}  # {curso_id: {count, scores, similares}}

        for similar in similar_employees:
            for course in similar.successful_courses:
                curso_id = course.get("cursoID", "")
                if not curso_id:
                    continue

                if curso_id not in course_stats:
                    course_stats[curso_id] = {
                        "course": course,
                        "count": 0,
                        "scores": [],
                        "similar_names": [],
                    }

                course_stats[curso_id]["count"] += 1
                course_stats[curso_id]["scores"].append(course.get("nota", 0))
                course_stats[curso_id]["similar_names"].append(similar.nome)

        # Filtra cursos com mínimo de endorsements
        recommendations = []

        for curso_id, stats in course_stats.items():
            if stats["count"] < min_endorsements:
                continue

            course = stats["course"]
            avg_score = sum(stats["scores"]) / len(stats["scores"])

            # Score de relevância baseado em:
            # - Quantos similares fizeram (normalizado)
            # - Nota média obtida
            count_score = min(stats["count"] / len(similar_employees), 1.0)
            grade_score = avg_score / 10.0
            relevance = (count_score * 0.6) + (grade_score * 0.4)

            similarity_reason = (
                f"{stats['count']} colaboradores com perfil similar "
                f"completaram com nota média {avg_score:.1f}"
            )

            rec = CollaborativeRecommendation(
                curso_id=curso_id,
                titulo=course.get("titulo", ""),
                categoria=course.get("categoria", ""),
                modalidade=course.get("modalidade", ""),
                carga_horaria=course.get("cargaHoraria", 0),
                relevance_score=round(relevance, 2),
                recommended_by_similar=stats["count"],
                avg_score_by_similar=round(avg_score, 1),
                similarity_reason=similarity_reason,
            )

            recommendations.append(rec)

        # Ordena por relevância
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)

        return recommendations[:top_n]

    def _calculate_similarity(
        self, profile: EmployeeProfile, other_emp: dict
    ) -> float:
        """
        Calcula score de similaridade entre dois colaboradores.

        Returns:
            Score de 0-1 (1 = idênticos)
        """
        score = 0.0

        # 1. Cargo (peso 0.4)
        if profile.cargo.lower() == other_emp.get("cargo", "").lower():
            score += 0.4
        elif self._same_cargo_family(profile.cargo, other_emp.get("cargo", "")):
            score += 0.2  # Cargos relacionados (ex: Dev Backend vs Dev Frontend)

        # 2. Nível (peso 0.3)
        if profile.nivel == other_emp.get("nivel", ""):
            score += 0.3
        elif self._adjacent_nivel(profile.nivel, other_emp.get("nivel", "")):
            score += 0.15  # Níveis adjacentes (Junior vs Pleno, Pleno vs Senior)

        # 3. Departamento (peso 0.2)
        if profile.departamento.lower() == other_emp.get("departamento", "").lower():
            score += 0.2

        # 4. Gaps similares (peso 0.1)
        # Verifica se têm competências em comum que precisam melhorar
        if profile.gaps_identificados and other_emp.get("gaps", []):
            profile_gaps_set = {gap.competency_key for gap in profile.gaps_identificados}
            other_gaps_set = {gap.get("competency_key") for gap in other_emp.get("gaps", [])}
            overlap = len(profile_gaps_set & other_gaps_set)
            if overlap > 0:
                score += 0.1

        return min(score, 1.0)

    def _same_cargo_family(self, cargo1: str, cargo2: str) -> bool:
        """Verifica se dois cargos são da mesma família."""
        cargo1_lower = cargo1.lower()
        cargo2_lower = cargo2.lower()

        families = [
            ["desenvolvedor", "developer", "dev", "programador"],
            ["analista", "analyst"],
            ["gerente", "gestor", "manager"],
            ["designer", "design"],
        ]

        for family in families:
            if any(term in cargo1_lower for term in family) and any(
                term in cargo2_lower for term in family
            ):
                return True

        return False

    def _adjacent_nivel(self, nivel1: str, nivel2: str) -> bool:
        """Verifica se dois níveis são adjacentes."""
        niveis = ["Junior", "Pleno", "Senior", "Especialista"]

        try:
            idx1 = niveis.index(nivel1)
            idx2 = niveis.index(nivel2)
            return abs(idx1 - idx2) == 1
        except ValueError:
            return False

    def _get_successful_courses(self, employee: dict) -> list[dict]:
        """
        Retorna cursos bem-sucedidos de um colaborador.

        Considera bem-sucedido:
        - Status = "Concluído"
        - Nota >= 7.0
        """
        training_history = employee.get("training_history", {})
        recent_courses = training_history.get("recent_courses", [])

        successful = [
            course
            for course in recent_courses
            if course.get("status") == "Concluído" and course.get("nota", 0) >= 7.0
        ]

        return successful
