#!/usr/bin/env python3
"""
Gera uma base estática consolidada para o frontend Vite funcionar sem backend.

O script reaproveita a lógica do backend Python para produzir saídas já
serializadas em JSON que podem ser consumidas no deploy estático da Vercel.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


FRONTEND_DIR = Path(__file__).resolve().parents[1]
TEST_HTN_DIR = FRONTEND_DIR.parent
API_DIR = TEST_HTN_DIR / "api"
OUTPUT_DIR = FRONTEND_DIR / "public" / "mock-data"
OUTPUT_FILE = OUTPUT_DIR / "talentboost-static.json"

sys.path.insert(0, str(API_DIR))
sys.path.insert(0, str(TEST_HTN_DIR))

import main as backend  # noqa: E402


def to_jsonable(value: Any) -> Any:
    """Converte modelos/dataclasses/Enums para estruturas serializáveis."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "value"):
        return value.value
    return value


def normalize_name(name: str) -> str:
    return backend.normalize_name(name)


def map_training_status(raw_status: str | None) -> str:
    mapping = {
        "Concluido": "completed",
        "Em Andamento": "in_progress",
        "Pendente": "enrolled",
    }
    return mapping.get(raw_status or "", "enrolled")


def build_training_snapshot(training_data: dict[str, Any], employee_name: str) -> dict[str, Any]:
    results_by_enrollment = {
        item.get("matriculaId"): item for item in training_data.get("resultados", [])
    }

    enrollments: list[dict[str, Any]] = []
    completed_course_ids: list[str] = []
    in_progress_course_ids: list[str] = []
    categories_completed: set[str] = set()
    scores: list[float] = []
    courses_by_id = {
        course.get("cursoID"): course for course in training_data.get("cursos", [])
    }

    for enrollment in training_data.get("matriculas", []):
        status = map_training_status(enrollment.get("status"))
        result = results_by_enrollment.get(enrollment.get("matriculaId"), {})
        course_id = enrollment.get("cursoID")
        course = courses_by_id.get(course_id, {})

        record = {
            "curso_id": course_id,
            "titulo": course.get("titulo", ""),
            "categoria": course.get("categoria", ""),
            "modalidade": course.get("modalidade", ""),
            "status": status,
            "progress": enrollment.get("progresso", 0),
            "nota": result.get("nota"),
            "data_matricula": enrollment.get("dataInicio"),
            "data_conclusao": enrollment.get("dataFim") if status == "completed" else None,
        }
        enrollments.append(record)

        if status == "completed":
            completed_course_ids.append(course_id)
            if course.get("categoria"):
                categories_completed.add(course["categoria"])
            if result.get("nota") is not None:
                scores.append(float(result["nota"]))
        elif status == "in_progress":
            in_progress_course_ids.append(course_id)

    completed_count = len(completed_course_ids)
    in_progress_count = len(in_progress_course_ids)
    enrolled_count = sum(1 for item in enrollments if item["status"] == "enrolled")
    total_count = len(enrollments)

    return {
        "employee_name": employee_name,
        "enrollments": enrollments,
        "summary": {
            "total_courses": total_count,
            "completed_courses": completed_count,
            "in_progress_courses": in_progress_count,
            "enrolled_courses": enrolled_count,
            "completion_rate": round(completed_count / total_count, 3) if total_count else 0.0,
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "categories_completed": sorted(categories_completed),
            "completed_course_ids": completed_course_ids,
            "in_progress_course_ids": in_progress_course_ids,
        },
    }


def build_seed_feedback(
    employees_by_name: dict[str, dict[str, Any]],
    courses_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    now = datetime.now(UTC)
    events: list[dict[str, Any]] = []

    def append_event(
        *,
        employee_id: int,
        employee_name: str,
        course_id: str,
        action: str,
        timestamp: datetime,
        rating: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        course = courses_by_id.get(course_id, {})
        events.append(
            {
                "employee_id": employee_id,
                "employee_name": employee_name,
                "curso_id": course_id,
                "curso_titulo": course.get("titulo", course_id),
                "action": action,
                "timestamp": timestamp.isoformat(),
                "rating": rating,
                "metadata": metadata or {},
            }
        )

    for offset, bundle in enumerate(employees_by_name.values()):
        employee_profile = bundle["profile"]
        employee_id = int(employee_profile.get("COLABORADOR_ID"))
        employee_name = employee_profile.get("NOME", "")
        training = bundle["training"]
        recommendations = bundle["recommendations"]["recommendations"]

        base_time = now - timedelta(days=60 - offset)

        for rec_index, recommendation in enumerate(recommendations[:5]):
            view_time = base_time + timedelta(hours=rec_index * 2)
            append_event(
                employee_id=employee_id,
                employee_name=employee_name,
                course_id=recommendation["curso_id"],
                action="viewed",
                timestamp=view_time,
                metadata={"source": "recommendation_seed", "priority": recommendation["priority"]},
            )
            if rec_index < 3 or recommendation["priority"] in {"critical", "high"}:
                append_event(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    course_id=recommendation["curso_id"],
                    action="clicked",
                    timestamp=view_time + timedelta(minutes=15),
                    metadata={"source": "recommendation_seed"},
                )

        for enrollment in training["enrollments"]:
            course_id = enrollment["curso_id"]
            enrolled_at = enrollment["data_matricula"] or now.date().isoformat()
            started_time = datetime.fromisoformat(enrolled_at).replace(tzinfo=UTC)

            append_event(
                employee_id=employee_id,
                employee_name=employee_name,
                course_id=course_id,
                action="viewed",
                timestamp=started_time,
                metadata={"source": "training_history_seed"},
            )
            append_event(
                employee_id=employee_id,
                employee_name=employee_name,
                course_id=course_id,
                action="clicked",
                timestamp=started_time + timedelta(minutes=30),
                metadata={"source": "training_history_seed"},
            )
            append_event(
                employee_id=employee_id,
                employee_name=employee_name,
                course_id=course_id,
                action="enrolled",
                timestamp=started_time + timedelta(hours=1),
                metadata={"status": enrollment["status"]},
            )

            if enrollment["status"] == "completed" and enrollment.get("nota") is not None:
                finished_at = enrollment["data_conclusao"] or enrolled_at
                append_event(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    course_id=course_id,
                    action="rated",
                    timestamp=datetime.fromisoformat(finished_at).replace(tzinfo=UTC),
                    rating=float(enrollment["nota"]),
                    metadata={"source": "completion_seed"},
                )

    return sorted(events, key=lambda item: item["timestamp"])


def build_recommendation_summary(recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    if not recommendations:
        return {
            "total": 0,
            "by_priority": {},
            "by_category": {},
            "average_relevance": 0.0,
        }

    by_priority: dict[str, list[str]] = {}
    by_category: dict[str, list[str]] = {}

    for recommendation in recommendations:
        by_priority.setdefault(recommendation["priority"], []).append(
            recommendation["titulo"]
        )
        by_category.setdefault(recommendation["categoria"], []).append(
            recommendation["titulo"]
        )

    average_relevance = sum(
        recommendation["relevance_score"] for recommendation in recommendations
    ) / len(recommendations)

    return {
        "total": len(recommendations),
        "by_priority": by_priority,
        "by_category": by_category,
        "average_relevance": round(average_relevance, 2),
    }


def serialize_recommendation(recommendation: Any) -> dict[str, Any]:
    explanation = getattr(recommendation, "explanation", None)

    return {
        "curso_id": recommendation.curso_id,
        "titulo": recommendation.titulo,
        "categoria": recommendation.categoria,
        "modalidade": recommendation.modalidade,
        "carga_horaria": recommendation.carga_horaria,
        "obrigatorio": recommendation.obrigatorio,
        "relevance_score": recommendation.relevance_score,
        "match_reason": recommendation.match_reason,
        "addresses_gaps": getattr(recommendation, "addresses_gaps", []),
        "priority": recommendation.priority,
        "explanation": (
            {
                "primary_reason": explanation.primary_reason,
                "gap_addressed": explanation.gap_addressed,
                "secondary_reasons": explanation.secondary_reasons,
                "confidence": explanation.confidence,
                "similar_employees_count": explanation.similar_employees_count,
                "avg_satisfaction": explanation.avg_satisfaction,
            }
            if explanation
            else None
        ),
    }


def build_recommendations_payload(
    employee_name: str,
    cadastro: dict[str, Any],
    avaliacao: dict[str, Any],
    training_data: dict[str, Any],
    gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    profile = backend.profile_builder.build_profile(
        employee_data=cadastro,
        evaluation_data=avaliacao,
        training_data=training_data,
        gaps=backend.gap_detector.detect_gaps(avaliacao),
    )

    recommendations = backend.recommendation_engine.recommend(
        profile=profile,
        top_n=10,
        exclude_completed=True,
    )
    recommendations_json = [
        serialize_recommendation(recommendation)
        for recommendation in recommendations
    ]

    return {
        "employee_name": employee_name,
        "profile_summary": {
            "cargo": profile.cargo,
            "nivel": profile.nivel,
            "nota_media_geral": profile.nota_media_geral,
            "pontos_fortes": profile.pontos_fortes,
            "total_gaps": len(gaps),
        },
        "recommendations": recommendations_json,
        "summary": build_recommendation_summary(recommendations_json),
        "metadata": {
            "cold_start_used": len(gaps) == 0,
            "generation_time_ms": 0,
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    employees = [to_jsonable(employee) for employee in backend.list_employees()]
    courses_response = deepcopy(backend.list_courses())
    overview_stats = deepcopy(backend.get_overview_stats())
    courses_by_id = {course["cursoID"]: course for course in courses_response["courses"]}

    employees_by_name: dict[str, dict[str, Any]] = {}

    for employee in employees:
        name = employee["name"]
        profile = deepcopy(backend.get_employee_profile(name))
        evaluation = deepcopy(backend.get_employee_evaluation(name))
        gaps = deepcopy(backend.analyze_gaps(name))
        sentiment = deepcopy(backend.get_sentiment_analysis(name))
        _, cadastro, training_data = backend.load_employee_data(name)
        recommendations = deepcopy(
            build_recommendations_payload(
                employee_name=name,
                cadastro=cadastro,
                avaliacao=evaluation,
                training_data=training_data,
                gaps=gaps["gaps"],
            )
        )
        training = build_training_snapshot(training_data, name)

        employees_by_name[normalize_name(name)] = {
            "profile": profile,
            "evaluation": evaluation,
            "gaps": gaps,
            "recommendations": recommendations,
            "sentiment_analysis": sentiment,
            "training": training,
        }

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "employees": employees,
        "employees_by_name": employees_by_name,
        "courses": courses_response,
        "overview_stats": overview_stats,
        "analytics_seed_events": build_seed_feedback(employees_by_name, courses_by_id),
    }

    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Static mock data written to {OUTPUT_FILE}")
    print(f"Employees: {len(employees)} | Courses: {courses_response['total']}")


if __name__ == "__main__":
    main()
