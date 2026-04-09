"""
Feedback Collector - Rastreia interações do usuário com recomendações.

Coleta feedback implícito e explícito para melhorar o sistema de recomendação.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal


@dataclass
class FeedbackEvent:
    """Evento de feedback do usuário."""
    employee_id: int
    employee_name: str
    curso_id: str
    curso_titulo: str
    action: Literal["viewed", "clicked", "enrolled", "dismissed", "rated"]
    timestamp: str
    rating: float | None = None  # Para action="rated" (0-10)
    metadata: dict | None = None  # Dados adicionais


class FeedbackCollector:
    """
    Coleta e armazena feedback sobre recomendações.

    Actions rastreadas:
    - "viewed": Recomendação foi exibida para o usuário
    - "clicked": Usuário clicou para ver detalhes
    - "enrolled": Usuário se matriculou no curso
    - "dismissed": Usuário marcou como "não tenho interesse"
    - "rated": Usuário avaliou o curso após concluir
    """

    def __init__(self, storage_path: str | Path = "data/feedback"):
        """
        Inicializa o coletor de feedback.

        Args:
            storage_path: Diretório onde armazenar feedback
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.storage_path / "recommendation_feedback.jsonl"

    def record_interaction(
        self,
        employee_id: int,
        employee_name: str,
        curso_id: str,
        curso_titulo: str,
        action: Literal["viewed", "clicked", "enrolled", "dismissed", "rated"],
        rating: float | None = None,
        metadata: dict | None = None,
    ):
        """
        Registra uma interação do usuário.

        Args:
            employee_id: ID do colaborador
            employee_name: Nome do colaborador
            curso_id: ID do curso
            curso_titulo: Título do curso
            action: Tipo de ação
            rating: Avaliação (0-10), opcional
            metadata: Dados adicionais (ex: source="cold_start")
        """
        event = FeedbackEvent(
            employee_id=employee_id,
            employee_name=employee_name,
            curso_id=curso_id,
            curso_titulo=curso_titulo,
            action=action,
            timestamp=datetime.now().isoformat(),
            rating=rating,
            metadata=metadata or {},
        )

        # Append to JSONL file
        with open(self.feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def get_click_through_rate(self, curso_id: str) -> float:
        """
        Calcula CTR (Click-Through Rate) de um curso.

        CTR = clicks / views

        Args:
            curso_id: ID do curso

        Returns:
            Taxa entre 0-1
        """
        events = self._load_events()
        course_events = [e for e in events if e["curso_id"] == curso_id]

        views = sum(1 for e in course_events if e["action"] == "viewed")
        clicks = sum(1 for e in course_events if e["action"] == "clicked")

        return clicks / views if views > 0 else 0.0

    def get_enrollment_rate(self, curso_id: str) -> float:
        """
        Calcula taxa de matrícula de um curso.

        Enrollment Rate = enrollments / clicks

        Args:
            curso_id: ID do curso

        Returns:
            Taxa entre 0-1
        """
        events = self._load_events()
        course_events = [e for e in events if e["curso_id"] == curso_id]

        clicks = sum(1 for e in course_events if e["action"] == "clicked")
        enrollments = sum(1 for e in course_events if e["action"] == "enrolled")

        return enrollments / clicks if clicks > 0 else 0.0

    def get_dismissal_rate(self, curso_id: str) -> float:
        """
        Calcula taxa de rejeição (dismissed) de um curso.

        Args:
            curso_id: ID do curso

        Returns:
            Taxa entre 0-1
        """
        events = self._load_events()
        course_events = [e for e in events if e["curso_id"] == curso_id]

        views = sum(1 for e in course_events if e["action"] == "viewed")
        dismissals = sum(1 for e in course_events if e["action"] == "dismissed")

        return dismissals / views if views > 0 else 0.0

    def get_average_rating(self, curso_id: str) -> float:
        """
        Calcula nota média de um curso.

        Args:
            curso_id: ID do curso

        Returns:
            Nota média (0-10) ou 0 se sem avaliações
        """
        events = self._load_events()
        ratings = [
            e["rating"]
            for e in events
            if e["curso_id"] == curso_id
            and e["action"] == "rated"
            and e["rating"] is not None
        ]

        return sum(ratings) / len(ratings) if ratings else 0.0

    def get_employee_history(self, employee_id: int) -> list[dict]:
        """
        Retorna histórico de interações de um colaborador.

        Args:
            employee_id: ID do colaborador

        Returns:
            Lista de eventos ordenados por timestamp
        """
        events = self._load_events()
        employee_events = [e for e in events if e["employee_id"] == employee_id]

        # Ordena por timestamp (mais recente primeiro)
        employee_events.sort(
            key=lambda x: x["timestamp"],
            reverse=True
        )

        return employee_events

    def get_popular_courses(self, top_n: int = 10) -> list[dict]:
        """
        Retorna cursos mais populares (mais cliques).

        Args:
            top_n: Número de cursos a retornar

        Returns:
            Lista de {curso_id, titulo, clicks, enrollments}
        """
        events = self._load_events()

        course_stats = {}

        for event in events:
            curso_id = event["curso_id"]
            if curso_id not in course_stats:
                course_stats[curso_id] = {
                    "curso_id": curso_id,
                    "titulo": event["curso_titulo"],
                    "clicks": 0,
                    "enrollments": 0,
                    "views": 0,
                }

            if event["action"] == "viewed":
                course_stats[curso_id]["views"] += 1
            elif event["action"] == "clicked":
                course_stats[curso_id]["clicks"] += 1
            elif event["action"] == "enrolled":
                course_stats[curso_id]["enrollments"] += 1

        # Ordena por clicks
        popular = sorted(
            course_stats.values(),
            key=lambda x: x["clicks"],
            reverse=True
        )

        return popular[:top_n]

    def get_analytics_summary(self) -> dict:
        """
        Retorna resumo geral de analytics.

        Returns:
            Dict com métricas agregadas
        """
        events = self._load_events()

        total_events = len(events)
        total_views = sum(1 for e in events if e["action"] == "viewed")
        total_clicks = sum(1 for e in events if e["action"] == "clicked")
        total_enrollments = sum(1 for e in events if e["action"] == "enrolled")
        total_dismissals = sum(1 for e in events if e["action"] == "dismissed")

        overall_ctr = total_clicks / total_views if total_views > 0 else 0.0
        overall_enrollment_rate = (
            total_enrollments / total_clicks if total_clicks > 0 else 0.0
        )

        unique_employees = len(set(e["employee_id"] for e in events))
        unique_courses = len(set(e["curso_id"] for e in events))

        return {
            "total_interactions": total_events,
            "total_views": total_views,
            "total_clicks": total_clicks,
            "total_enrollments": total_enrollments,
            "total_dismissals": total_dismissals,
            "overall_ctr": round(overall_ctr, 3),
            "overall_enrollment_rate": round(overall_enrollment_rate, 3),
            "unique_employees": unique_employees,
            "unique_courses": unique_courses,
        }

    def _load_events(self) -> list[dict]:
        """Carrega todos os eventos do arquivo JSONL."""
        if not self.feedback_file.exists():
            return []

        events = []
        with open(self.feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

        return events
