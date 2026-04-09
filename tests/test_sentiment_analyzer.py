"""
Testes para SentimentAnalyzer.

Valida detecção de tom, urgência e extração de hints.
"""

import pytest
from talent_boost_core.sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentTone,
    UrgencyLevel,
)


@pytest.fixture
def analyzer():
    """Fixture do analisador."""
    return SentimentAnalyzer()


class TestSentimentAnalyzer:
    """Suite de testes para análise de sentimentos."""

    def test_detect_positive_tone_with_high_score(self, analyzer):
        """Observação positiva com nota alta deve retornar tom POSITIVE."""
        result = analyzer.analyze(
            observation="Excelente desempenho, continuar assim!",
            competency_name="Colaboração",
            score=9,
            evaluator_role="gestor",
        )

        assert result.tone == SentimentTone.POSITIVE
        assert result.urgency == UrgencyLevel.LOW
        assert result.confidence > 0.7

    def test_detect_constructive_tone_with_pode_melhorar(self, analyzer):
        """Observação com 'pode melhorar' deve retornar tom CONSTRUCTIVE."""
        result = analyzer.analyze(
            observation="Pode melhorar a comunicação com stakeholders.",
            competency_name="Comunicação",
            score=6,
            evaluator_role="par",
        )

        assert result.tone == SentimentTone.CONSTRUCTIVE
        assert result.urgency in [UrgencyLevel.MEDIUM, UrgencyLevel.HIGH]
        assert "comunicação" in result.development_hints

    def test_detect_high_urgency_from_gestor_low_score(self, analyzer):
        """Nota baixa do gestor deve gerar urgência alta."""
        result = analyzer.analyze(
            observation="Precisa melhorar significativamente.",
            competency_name="Liderança",
            score=4,
            evaluator_role="gestor",
        )

        assert result.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]

    def test_extract_key_phrases(self, analyzer):
        """Deve extrair frases-chave relevantes."""
        result = analyzer.analyze(
            observation=(
                "Demonstra boa evolução técnica. "
                "Pode ampliar visão de negócio. "
                "Continuar investindo em aprendizado."
            ),
            competency_name="Aprendizado",
            score=7,
            evaluator_role="auto",
        )

        assert len(result.key_phrases) > 0
        assert any("evolução" in phrase.lower() for phrase in result.key_phrases)

    def test_generate_development_hints_from_keywords(self, analyzer):
        """Deve gerar hints baseado em keywords."""
        result = analyzer.analyze(
            observation="Pode melhorar apresentações e comunicação escrita.",
            competency_name="Comunicação",
            score=6,
            evaluator_role="gestor",
        )

        assert "comunicação" in result.development_hints

    def test_calculate_confidence_with_short_observation(self, analyzer):
        """Observação curta deve ter confiança menor."""
        result_short = analyzer.analyze(
            observation="Ok",
            competency_name="Test",
            score=7,
            evaluator_role="auto",
        )

        result_detailed = analyzer.analyze(
            observation="Demonstra evolução consistente nas entregas técnicas e busca sempre aprender novas tecnologias.",
            competency_name="Test",
            score=7,
            evaluator_role="auto",
        )

        assert result_detailed.confidence > result_short.confidence

    def test_analyze_all_observations_from_evaluation(self, analyzer):
        """Deve analisar todas as observações de uma avaliação."""
        evaluation_data = {
            "valores": {
                "temosFomeDeAprender": {
                    "auto": {
                        "nota": 8,
                        "observacao": "Estou investindo em cursos e projetos pessoais.",
                    },
                    "par": {
                        "nota": 8,
                        "observacao": "Sempre buscando aprender novas tecnologias.",
                    },
                    "gestor": {
                        "nota": 8,
                        "observacao": "Demonstra evolução técnica consistente.",
                    },
                },
            }
        }

        results = analyzer.analyze_all_observations(evaluation_data)

        assert "temosFomeDeAprender" in results
        assert len(results["temosFomeDeAprender"]) == 3  # auto, par, gestor

        for role, analysis in results["temosFomeDeAprender"]:
            assert role in ["auto", "par", "gestor"]
            assert isinstance(analysis.tone, SentimentTone)
            assert isinstance(analysis.urgency, UrgencyLevel)

    def test_role_weight_in_urgency_detection(self, analyzer):
        """Gestor deve ter peso maior que auto-avaliação na urgência."""
        # Mesma observação e nota, avaliadores diferentes
        result_auto = analyzer.analyze(
            observation="Pode melhorar.",
            competency_name="Test",
            score=5,
            evaluator_role="auto",
        )

        result_gestor = analyzer.analyze(
            observation="Pode melhorar.",
            competency_name="Test",
            score=5,
            evaluator_role="gestor",
        )

        # Gestor deve gerar urgência igual ou maior
        urgency_order = {
            UrgencyLevel.LOW: 1,
            UrgencyLevel.MEDIUM: 2,
            UrgencyLevel.HIGH: 3,
            UrgencyLevel.CRITICAL: 4,
        }

        assert urgency_order[result_gestor.urgency] >= urgency_order[result_auto.urgency]

    def test_no_observation_returns_empty_key_phrases(self, analyzer):
        """Observação vazia deve retornar listas vazias."""
        result = analyzer.analyze(
            observation="",
            competency_name="Test",
            score=7,
            evaluator_role="auto",
        )

        assert len(result.key_phrases) == 0

    @pytest.mark.parametrize("observation,expected_tone", [
        ("Mandou bem, continuar assim!", SentimentTone.POSITIVE),
        ("Pode melhorar a objetividade.", SentimentTone.CONSTRUCTIVE),
        ("Não demonstra evolução.", SentimentTone.NEGATIVE),
        ("Entrega no prazo.", SentimentTone.NEUTRAL),
    ])
    def test_tone_detection_patterns(self, analyzer, observation, expected_tone):
        """Testa padrões de detecção de tom."""
        result = analyzer.analyze(
            observation=observation,
            competency_name="Test",
            score=6 if expected_tone != SentimentTone.POSITIVE else 8,
            evaluator_role="gestor",
        )

        assert result.tone == expected_tone
