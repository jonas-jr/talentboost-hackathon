"""
Construtor de Perfil de Colaborador.

Consolida dados de avaliação, cadastrais e histórico de treinamentos
para criar um perfil completo para o sistema de recomendação.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from .competency_gap_detector import CompetencyGap


@dataclass
class TrainingHistory:
    """Histórico de treinamentos do colaborador."""
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    completion_rate: float
    average_score: float
    categories_completed: list[str]
    recent_courses: list[dict]
    completed_course_ids: list[str] = None

    def __post_init__(self):
        if self.completed_course_ids is None:
            self.completed_course_ids = []


@dataclass
class EmployeeProfile:
    """Perfil completo do colaborador para recomendação."""
    # Dados cadastrais
    colaborador_id: int
    nome: str
    cargo: str
    cargo_codigo: int
    departamento: str
    nivel: Literal["Junior", "Pleno", "Senior", "Especialista"]
    tempo_casa_meses: int
    gestor: bool

    # Dados de avaliação
    ciclo_avaliacao: str
    nota_media_geral: float
    gaps_identificados: list[CompetencyGap]
    pontos_fortes: list[str]

    # Histórico de treinamentos
    training_history: TrainingHistory

    # Metadados
    profile_created_at: str
    last_evaluation_date: str


class EmployeeProfileBuilder:
    """
    Constrói perfil completo do colaborador a partir de múltiplas fontes.

    Integra:
    - Dados cadastrais
    - Avaliação de desempenho
    - Histórico de treinamentos
    - Gaps identificados
    """

    def build_profile(
        self,
        employee_data: dict,
        evaluation_data: dict,
        training_data: dict,
        gaps: list[CompetencyGap],
    ) -> EmployeeProfile:
        """
        Constrói perfil completo.

        Args:
            employee_data: Dados cadastrais do colaborador
            evaluation_data: Dados da avaliação de desempenho
            training_data: Dados de treinamentos (cursos, matrículas, resultados)
            gaps: Lista de gaps identificados

        Returns:
            EmployeeProfile completo
        """
        # Processa dados cadastrais
        colaborador_id = employee_data.get("COLABORADOR_ID")
        nome = employee_data.get("NOME", "")
        cargo = employee_data.get("CARGO_NOME", "")
        cargo_codigo = employee_data.get("CARGO_CODIGO")
        departamento = employee_data.get("DEPARTAMENTO", "")
        tempo_casa = employee_data.get("TEMPO_DE_CASA_EM_MESES", 0)

        # Determina nível (inferido do cargo ou posição na avaliação)
        nivel = self._infer_nivel(evaluation_data.get("posicao", ""), cargo)

        # É gestor?
        gestor = evaluation_data.get("gestor", False)

        # Processa avaliação
        ciclo = evaluation_data.get("ciclo", "")
        nota_media = self._calculate_average_score(evaluation_data)
        pontos_fortes = self._identify_strengths(evaluation_data)

        # Extrai data da avaliação
        periodo_fim = evaluation_data.get("periodofim", "")

        # Processa histórico de treinamentos
        training_history = self._build_training_history(training_data, colaborador_id)

        # Cria perfil
        profile = EmployeeProfile(
            colaborador_id=colaborador_id,
            nome=nome,
            cargo=cargo,
            cargo_codigo=cargo_codigo,
            departamento=departamento,
            nivel=nivel,
            tempo_casa_meses=tempo_casa,
            gestor=gestor,
            ciclo_avaliacao=ciclo,
            nota_media_geral=nota_media,
            gaps_identificados=gaps,
            pontos_fortes=pontos_fortes,
            training_history=training_history,
            profile_created_at=datetime.now().isoformat(),
            last_evaluation_date=periodo_fim,
        )

        return profile

    def _infer_nivel(self, posicao_avaliacao: str, cargo: str) -> str:
        """Infere nível do colaborador."""
        posicao_lower = posicao_avaliacao.lower()
        cargo_lower = cargo.lower()

        # Prioriza posição da avaliação
        if "junior" in posicao_lower or "júnior" in posicao_lower:
            return "Junior"
        elif "senior" in posicao_lower or "sênior" in posicao_lower:
            return "Senior"
        elif "pleno" in posicao_lower:
            return "Pleno"
        elif "especialista" in posicao_lower or "expert" in posicao_lower:
            return "Especialista"

        # Fallback para cargo
        if "junior" in cargo_lower or "jr" in cargo_lower:
            return "Junior"
        elif "senior" in cargo_lower or "sr" in cargo_lower:
            return "Senior"
        elif "pleno" in cargo_lower:
            return "Pleno"
        elif "especialista" in cargo_lower:
            return "Especialista"

        return "Pleno"  # Default

    def _calculate_average_score(self, evaluation_data: dict) -> float:
        """Calcula nota média geral da avaliação."""
        valores = evaluation_data.get("valores", {})
        all_scores = []

        for competency, perspectives in valores.items():
            for role in ["auto", "par", "gestor"]:
                if role in perspectives and perspectives[role].get("nota"):
                    all_scores.append(perspectives[role]["nota"])

        if not all_scores:
            return 0.0

        return round(sum(all_scores) / len(all_scores), 2)

    def _identify_strengths(self, evaluation_data: dict) -> list[str]:
        """Identifica pontos fortes (competências com nota >= 8)."""
        valores = evaluation_data.get("valores", {})
        strengths = []

        competency_display_names = {
            "jogamosJuntosPelaCompanhia": "Colaboração",
            "inovamosComFocoNoCliente": "Inovação",
            "temosFomeDeAprender": "Aprendizado",
            "vamosDiretoAoPonto": "Comunicação",
            "genteEResultadosAndamJuntos": "Equilíbrio Pessoas/Resultados",
        }

        for competency_key, perspectives in valores.items():
            scores = []
            for role in ["gestor", "par", "auto"]:
                if role in perspectives and perspectives[role].get("nota"):
                    scores.append(perspectives[role]["nota"])

            if scores:
                avg = sum(scores) / len(scores)
                if avg >= 8:
                    display_name = competency_display_names.get(
                        competency_key, competency_key
                    )
                    strengths.append(display_name)

        return strengths

    def _build_training_history(
        self, training_data: dict, colaborador_id: int
    ) -> TrainingHistory:
        """Constrói histórico de treinamentos."""
        # Resolve o colaboradorId do sistema de treinamentos (pode diferir do cadastral)
        training_collab_id = None
        colaboradores = training_data.get("colaboradores", [])
        if colaboradores:
            training_collab_id = colaboradores[0].get("colaboradorId")

        # Filtra matrículas do colaborador
        lookup_id = str(training_collab_id or colaborador_id)
        matriculas = [
            m for m in training_data.get("matriculas", [])
            if str(m.get("colaboradorId")) == lookup_id
        ]

        if not matriculas:
            return TrainingHistory(
                total_courses=0,
                completed_courses=0,
                in_progress_courses=0,
                completion_rate=0.0,
                average_score=0.0,
                categories_completed=[],
                recent_courses=[],
            )

        # Conta status
        completed = [m for m in matriculas if m.get("status") == "Concluido"]
        in_progress = [m for m in matriculas if m.get("status") == "Em Andamento"]

        # Calcula taxa de conclusão
        completion_rate = len(completed) / len(matriculas) if matriculas else 0.0

        # Busca notas dos cursos concluídos
        resultados = training_data.get("resultados", [])
        matricula_ids = [m.get("matriculaId") for m in completed]

        notas = [
            r.get("nota", 0)
            for r in resultados
            if r.get("matriculaId") in matricula_ids and r.get("nota")
        ]

        avg_score = sum(notas) / len(notas) if notas else 0.0

        # Identifica categorias dos cursos concluídos
        cursos_map = {
            c.get("cursoID"): c for c in training_data.get("cursos", [])
        }

        categories = set()
        for m in completed:
            curso_id = m.get("cursoID")
            if curso_id in cursos_map:
                category = cursos_map[curso_id].get("categoria", "")
                if category:
                    categories.add(category)

        # Cursos recentes (últimos 3)
        recent = sorted(
            matriculas,
            key=lambda m: m.get("dataInicio", ""),
            reverse=True,
        )[:3]

        recent_courses = []
        for m in recent:
            curso_id = m.get("cursoID")
            curso = cursos_map.get(curso_id, {})
            recent_courses.append({
                "curso_id": curso_id,
                "titulo": curso.get("titulo", ""),
                "categoria": curso.get("categoria", ""),
                "status": m.get("status", ""),
                "progresso": m.get("progresso", 0),
            })

        completed_course_ids = [m.get("cursoID", "") for m in completed if m.get("cursoID")]

        return TrainingHistory(
            total_courses=len(matriculas),
            completed_courses=len(completed),
            in_progress_courses=len(in_progress),
            completion_rate=round(completion_rate, 2),
            average_score=round(avg_score, 2),
            categories_completed=list(categories),
            recent_courses=recent_courses,
            completed_course_ids=completed_course_ids,
        )
