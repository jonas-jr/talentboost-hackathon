"""
Detector de Gaps de Competências.

Identifica lacunas de desenvolvimento baseado em avaliações e análise de sentimentos.
"""

from dataclasses import dataclass
from typing import Literal

from .sentiment_analyzer import SentimentAnalyzer, SentimentAnalysis, UrgencyLevel


@dataclass
class CompetencyGap:
    """Representa um gap de competência identificado."""
    competency_name: str
    competency_key: str
    average_score: float
    gap_severity: Literal["low", "medium", "high", "critical"]
    urgency: UrgencyLevel
    context: str
    evaluator_consensus: float  # 0-1 (concordância entre avaliadores)
    development_hints: list[str]
    key_observations: list[str]


class CompetencyGapDetector:
    """
    Detecta gaps de competências para priorizar desenvolvimento.

    Considera:
    - Notas das avaliações
    - Análise de sentimentos
    - Consenso entre avaliadores
    - Urgência identificada
    """

    # Mapeamento de competências para categorias de treinamento
    COMPETENCY_TO_TRAINING_MAP = {
        "jogamosJuntosPelaCompanhia": {
            "category": "colaboracao",
            "keywords": ["trabalho em equipe", "colaboração", "integração"],
        },
        "inovamosComFocoNoCliente": {
            "category": "estrategia",
            "keywords": ["visão de negócio", "customer experience", "produto"],
        },
        "temosFomeDeAprender": {
            "category": "aprendizado",
            "keywords": ["desenvolvimento técnico", "novas tecnologias", "upskilling"],
        },
        "vamosDiretoAoPonto": {
            "category": "comunicacao",
            "keywords": ["comunicação assertiva", "objetividade", "clareza"],
        },
        "genteEResultadosAndamJuntos": {
            "category": "lideranca",
            "keywords": ["gestão de relacionamento", "entrega de resultados", "equilíbrio"],
        },
    }

    def __init__(self, sentiment_analyzer: SentimentAnalyzer):
        """
        Inicializa o detector.

        Args:
            sentiment_analyzer: Instância do analisador de sentimentos
        """
        self.sentiment_analyzer = sentiment_analyzer

    def detect_gaps(self, evaluation_data: dict) -> list[CompetencyGap]:
        """
        Detecta gaps de competências em uma avaliação.

        Args:
            evaluation_data: Dados da avaliação completa

        Returns:
            Lista de gaps ordenados por severidade (mais críticos primeiro)
        """
        gaps = []

        # Analisa sentimentos de todas as observações
        sentiment_results = self.sentiment_analyzer.analyze_all_observations(
            evaluation_data
        )

        valores = evaluation_data.get("valores", {})

        for competency_key, perspectives in valores.items():
            # Coleta notas de todos os avaliadores
            scores = []
            observations = []
            urgencies = []
            all_hints = []

            for role in ["auto", "par", "gestor"]:
                if role in perspectives and perspectives[role].get("nota"):
                    scores.append(perspectives[role]["nota"])
                    observations.append(perspectives[role].get("observacao", ""))

            # Pega análises de sentimentos para esta competência
            if competency_key in sentiment_results:
                for role, analysis in sentiment_results[competency_key]:
                    urgencies.append(analysis.urgency)
                    all_hints.extend(analysis.development_hints)

            if not scores:
                continue  # Sem dados para esta competência

            # Calcula média e consenso
            avg_score = sum(scores) / len(scores)
            consensus = self._calculate_consensus(scores)

            # Determina severidade
            severity = self._determine_severity(avg_score, urgencies, consensus)

            # Determina urgência máxima
            max_urgency = self._get_max_urgency(urgencies)

            # Gera contexto narrativo
            context = self._generate_context(
                competency_key, avg_score, perspectives, consensus
            )

            # Filtra observações mais relevantes
            key_obs = [obs for obs in observations if obs and len(obs.split()) > 5]

            # Cria gap apenas se nota < 7 ou urgência alta
            if avg_score < 7 or max_urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
                gap = CompetencyGap(
                    competency_name=self._get_competency_display_name(competency_key),
                    competency_key=competency_key,
                    average_score=round(avg_score, 2),
                    gap_severity=severity,
                    urgency=max_urgency,
                    context=context,
                    evaluator_consensus=consensus,
                    development_hints=list(set(all_hints)),
                    key_observations=key_obs[:2],  # Top 2 observações
                )
                gaps.append(gap)

        # Ordena por severidade e urgência
        return sorted(
            gaps,
            key=lambda g: (
                self._severity_to_score(g.gap_severity),
                self._urgency_to_score(g.urgency),
                -g.average_score,
            ),
            reverse=True,
        )

    def _calculate_consensus(self, scores: list[float]) -> float:
        """
        Calcula consenso entre avaliadores (0-1).

        Consenso alto = pouca variação entre notas.
        """
        if len(scores) < 2:
            return 1.0  # Apenas um avaliador = consenso total

        # Calcula desvio padrão normalizado
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # Normaliza para 0-1 (assumindo escala 0-10)
        # Quanto menor o desvio, maior o consenso
        consensus = 1 - min(std_dev / 3, 1.0)

        return round(consensus, 2)

    def _determine_severity(
        self,
        avg_score: float,
        urgencies: list[UrgencyLevel],
        consensus: float,
    ) -> Literal["low", "medium", "high", "critical"]:
        """Determina severidade do gap."""
        # Conta urgências críticas/altas
        high_urgency_count = sum(
            1 for u in urgencies
            if u in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]
        )

        # Regras de severidade
        if avg_score < 4 or (high_urgency_count >= 2 and consensus > 0.7):
            return "critical"
        elif avg_score < 6 or high_urgency_count >= 1:
            return "high"
        elif avg_score < 7:
            return "medium"
        else:
            return "low"

    def _get_max_urgency(self, urgencies: list[UrgencyLevel]) -> UrgencyLevel:
        """Retorna a maior urgência da lista."""
        if not urgencies:
            return UrgencyLevel.MEDIUM

        priority_order = [
            UrgencyLevel.CRITICAL,
            UrgencyLevel.HIGH,
            UrgencyLevel.MEDIUM,
            UrgencyLevel.LOW,
        ]

        for urgency in priority_order:
            if urgency in urgencies:
                return urgency

        return UrgencyLevel.MEDIUM

    def _generate_context(
        self,
        competency_key: str,
        avg_score: float,
        perspectives: dict,
        consensus: float,
    ) -> str:
        """Gera contexto narrativo do gap."""
        comp_name = self._get_competency_display_name(competency_key)

        # Identifica perspectiva com nota mais baixa
        lowest_role = None
        lowest_score = 10

        for role in ["gestor", "par", "auto"]:
            if role in perspectives and perspectives[role].get("nota"):
                score = perspectives[role]["nota"]
                if score < lowest_score:
                    lowest_score = score
                    lowest_role = role

        role_labels = {
            "gestor": "gestão",
            "par": "pares",
            "auto": "autoavaliação",
        }

        if consensus > 0.8:
            consensus_text = "Há forte consenso entre avaliadores"
        elif consensus > 0.6:
            consensus_text = "Há consenso moderado entre avaliadores"
        else:
            consensus_text = "Há divergência entre avaliadores"

        if lowest_role:
            context = (
                f"{comp_name}: nota média {avg_score:.1f}. "
                f"{consensus_text}. "
                f"Avaliação mais crítica veio da {role_labels.get(lowest_role, lowest_role)}."
            )
        else:
            context = (
                f"{comp_name}: nota média {avg_score:.1f}. {consensus_text}."
            )

        return context

    def _get_competency_display_name(self, key: str) -> str:
        """Retorna nome amigável da competência."""
        display_names = {
            "jogamosJuntosPelaCompanhia": "Colaboração e Trabalho em Equipe",
            "inovamosComFocoNoCliente": "Inovação com Foco no Cliente",
            "temosFomeDeAprender": "Fome de Aprender",
            "vamosDiretoAoPonto": "Comunicação Direta e Objetiva",
            "genteEResultadosAndamJuntos": "Equilíbrio entre Pessoas e Resultados",
        }
        return display_names.get(key, key)

    def _severity_to_score(self, severity: str) -> int:
        """Converte severidade para score numérico para ordenação."""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity, 0)

    def _urgency_to_score(self, urgency: UrgencyLevel) -> int:
        """Converte urgência para score numérico para ordenação."""
        scores = {
            UrgencyLevel.CRITICAL: 4,
            UrgencyLevel.HIGH: 3,
            UrgencyLevel.MEDIUM: 2,
            UrgencyLevel.LOW: 1,
        }
        return scores.get(urgency, 0)

    def get_training_categories(self, gap: CompetencyGap) -> list[str]:
        """
        Mapeia um gap para categorias de treinamento.

        Args:
            gap: Gap identificado

        Returns:
            Lista de categorias de treinamento recomendadas
        """
        mapping = self.COMPETENCY_TO_TRAINING_MAP.get(gap.competency_key)

        if not mapping:
            return []

        categories = [mapping["category"]]

        # Adiciona categorias baseadas em hints
        hint_to_category = {
            "comunicação": "comunicacao",
            "técnico": "tecnico",
            "liderança": "lideranca",
            "estratégia": "estrategia",
            "colaboração": "colaboracao",
        }

        for hint in gap.development_hints:
            if hint in hint_to_category:
                category = hint_to_category[hint]
                if category not in categories:
                    categories.append(category)

        return categories
