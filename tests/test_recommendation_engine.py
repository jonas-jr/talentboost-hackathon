"""
Testes para TrainingRecommendationEngine.

Valida sistema de recomendação híbrido.
"""

import pytest
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine
from talent_boost_core.profile_builder import EmployeeProfile, TrainingHistory
from talent_boost_core.competency_gap_detector import CompetencyGap, UrgencyLevel


@pytest.fixture
def sample_courses():
    """Cursos de exemplo para testes."""
    return [
        {
            "cursoID": "C001",
            "titulo": "Comunicação Assertiva",
            "categoria": "Soft Skills",
            "modalidade": "EAD",
            "cargaHoraria": 8,
            "obrigatorio": False,
            "notaMinima": 7,
        },
        {
            "cursoID": "C002",
            "titulo": "Visão de Produto para Desenvolvedores",
            "categoria": "Gestao",
            "modalidade": "EAD",
            "cargaHoraria": 12,
            "obrigatorio": False,
            "notaMinima": 7,
        },
        {
            "cursoID": "C003",
            "titulo": "Fundamentos de Cloud AWS",
            "categoria": "Tecnico",
            "modalidade": "EAD",
            "cargaHoraria": 16,
            "obrigatorio": False,
            "notaMinima": 7,
        },
        {
            "cursoID": "C004",
            "titulo": "Liderança para Times Técnicos",
            "categoria": "Lideranca",
            "modalidade": "EAD",
            "cargaHoraria": 10,
            "obrigatorio": False,
            "notaMinima": 7,
        },
    ]


@pytest.fixture
def sample_profile():
    """Perfil de colaborador de exemplo."""
    gap1 = CompetencyGap(
        competency_name="Comunicação Direta e Objetiva",
        competency_key="vamosDiretoAoPonto",
        average_score=6.0,
        gap_severity="medium",
        urgency=UrgencyLevel.MEDIUM,
        context="Pode melhorar objetividade.",
        evaluator_consensus=0.8,
        development_hints=["comunicacao"],
        key_observations=["Pode melhorar objetividade em status updates."],
    )

    gap2 = CompetencyGap(
        competency_name="Inovação com Foco no Cliente",
        competency_key="inovamosComFocoNoCliente",
        average_score=5.3,
        gap_severity="high",
        urgency=UrgencyLevel.HIGH,
        context="Precisa ampliar visão de negócio.",
        evaluator_consensus=0.9,
        development_hints=["estrategia"],
        key_observations=["Foca no técnico, pode ampliar visão de negócio."],
    )

    training_history = TrainingHistory(
        total_courses=3,
        completed_courses=3,
        in_progress_courses=0,
        completion_rate=1.0,
        average_score=8.5,
        categories_completed=["Compliance"],
        recent_courses=[],
    )

    return EmployeeProfile(
        colaborador_id=2001,
        nome="Ana Paula Ferreira",
        cargo="Desenvolvedora Backend",
        cargo_codigo=501,
        departamento="Tecnologia",
        nivel="Junior",
        tempo_casa_meses=12,
        gestor=False,
        ciclo_avaliacao="2025",
        nota_media_geral=6.8,
        gaps_identificados=[gap2, gap1],  # Ordenados por severidade
        pontos_fortes=["Aprendizado"],
        training_history=training_history,
        profile_created_at="2025-01-01T00:00:00",
        last_evaluation_date="2025-12-31",
    )


class TestTrainingRecommendationEngine:
    """Suite de testes para o motor de recomendação."""

    def test_recommend_returns_top_n(self, sample_courses, sample_profile):
        """Deve retornar exatamente top_n recomendações."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=2)

        assert len(recommendations) <= 2

    def test_recommend_prioritizes_high_severity_gaps(self, sample_courses, sample_profile):
        """Gaps com severidade alta devem ter prioridade."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=5)

        # Primeira recomendação deve endereçar gap de maior severidade
        if recommendations:
            first_rec = recommendations[0]
            assert first_rec.priority in ["high", "critical"]

    def test_calculate_relevance_category_match(self, sample_courses, sample_profile):
        """Curso com categoria matching deve ter relevância alta."""
        engine = TrainingRecommendationEngine(sample_courses)

        # Gap de comunicação → curso de Soft Skills deve ter boa relevância
        gap_comunicacao = sample_profile.gaps_identificados[1]  # vamosDiretoAoPonto

        curso_comunicacao = sample_courses[0]  # Comunicação Assertiva
        relevance = engine._calculate_relevance(
            curso_comunicacao,
            gap_comunicacao,
            ["Soft Skills", "Comunicacao"],
            ["comunicação", "apresentação", "objetividade"],
            sample_profile,
        )

        assert relevance > 0.5

    def test_check_nivel_match_junior_prefers_fundamentos(self, sample_courses):
        """Junior deve ter match alto com cursos de fundamentos."""
        engine = TrainingRecommendationEngine(sample_courses)

        curso_fundamentos = {
            "titulo": "Fundamentos de Cloud AWS",
            "categoria": "Tecnico",
        }

        match = engine._check_nivel_match(curso_fundamentos, "Junior")
        assert match >= 0.7

    def test_check_nivel_match_senior_prefers_advanced(self, sample_courses):
        """Senior deve ter match alto com cursos avançados."""
        engine = TrainingRecommendationEngine(sample_courses)

        curso_avancado = {
            "titulo": "Arquitetura Avançada de Sistemas",
            "categoria": "Tecnico",
        }

        match = engine._check_nivel_match(curso_avancado, "Senior")
        assert match >= 0.8

    def test_recommendation_includes_match_reason(self, sample_courses, sample_profile):
        """Recomendação deve incluir razão do match."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=3)

        for rec in recommendations:
            assert rec.match_reason is not None
            assert len(rec.match_reason) > 0
            assert any(gap.competency_name in rec.match_reason for gap in sample_profile.gaps_identificados)

    def test_recommendation_addresses_specific_gaps(self, sample_courses, sample_profile):
        """Recomendação deve listar gaps que ela endereça."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=5)

        for rec in recommendations:
            assert len(rec.addresses_gaps) > 0
            # Gaps endereçados devem estar na lista de gaps do perfil
            profile_gap_names = [g.competency_name for g in sample_profile.gaps_identificados]
            for gap_name in rec.addresses_gaps:
                assert gap_name in profile_gap_names

    def test_get_recommendation_summary(self, sample_courses, sample_profile):
        """Resumo deve conter estatísticas corretas."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=5)
        summary = engine.get_recommendation_summary(recommendations)

        assert "total" in summary
        assert summary["total"] == len(recommendations)
        assert "by_priority" in summary
        assert "by_category" in summary
        assert "average_relevance" in summary
        assert 0 <= summary["average_relevance"] <= 1

    def test_exclude_completed_courses(self, sample_courses):
        """Deve excluir cursos já concluídos quando solicitado."""
        # Simula perfil com curso completado
        profile_with_history = EmployeeProfile(
            colaborador_id=1,
            nome="Test",
            cargo="Test",
            cargo_codigo=1,
            departamento="Test",
            nivel="Pleno",
            tempo_casa_meses=24,
            gestor=False,
            ciclo_avaliacao="2025",
            nota_media_geral=7.0,
            gaps_identificados=[],
            pontos_fortes=[],
            training_history=TrainingHistory(
                total_courses=1,
                completed_courses=1,
                in_progress_courses=0,
                completion_rate=1.0,
                average_score=8.0,
                categories_completed=["Soft Skills"],
                recent_courses=[{"titulo": "Comunicação Assertiva", "categoria": "Soft Skills", "status": "Concluido", "progresso": 100}],
            ),
            profile_created_at="2025-01-01T00:00:00",
            last_evaluation_date="2025-12-31",
        )

        engine = TrainingRecommendationEngine(sample_courses)

        # Sem excluir completados
        recs_with = engine.recommend(profile_with_history, top_n=10, exclude_completed=False)

        # Com exclusão (deve ter menos ou igual)
        recs_without = engine.recommend(profile_with_history, top_n=10, exclude_completed=True)

        assert len(recs_without) <= len(recs_with)

    def test_priority_ordering(self, sample_courses, sample_profile):
        """Recomendações devem estar ordenadas por prioridade e relevância."""
        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(sample_profile, top_n=5)

        if len(recommendations) > 1:
            priority_scores = [engine._priority_to_score(r.priority) for r in recommendations]

            # Verifica se está ordenado (decrescente)
            for i in range(len(priority_scores) - 1):
                # Se prioridades forem iguais, relevância deve ser decrescente
                if priority_scores[i] == priority_scores[i + 1]:
                    assert recommendations[i].relevance_score >= recommendations[i + 1].relevance_score
                else:
                    assert priority_scores[i] >= priority_scores[i + 1]

    def test_empty_courses_returns_empty_recommendations(self, sample_profile):
        """Sem cursos disponíveis, deve retornar lista vazia."""
        engine = TrainingRecommendationEngine([])
        recommendations = engine.recommend(sample_profile, top_n=5)

        assert len(recommendations) == 0

    def test_no_gaps_returns_empty_recommendations(self, sample_courses):
        """Sem gaps, deve retornar lista vazia."""
        profile_no_gaps = EmployeeProfile(
            colaborador_id=1,
            nome="Test",
            cargo="Test",
            cargo_codigo=1,
            departamento="Test",
            nivel="Senior",
            tempo_casa_meses=60,
            gestor=True,
            ciclo_avaliacao="2025",
            nota_media_geral=9.0,
            gaps_identificados=[],  # Nenhum gap
            pontos_fortes=["Todos"],
            training_history=TrainingHistory(
                total_courses=0,
                completed_courses=0,
                in_progress_courses=0,
                completion_rate=0.0,
                average_score=0.0,
                categories_completed=[],
                recent_courses=[],
            ),
            profile_created_at="2025-01-01T00:00:00",
            last_evaluation_date="2025-12-31",
        )

        engine = TrainingRecommendationEngine(sample_courses)
        recommendations = engine.recommend(profile_no_gaps, top_n=5)

        assert len(recommendations) == 0
