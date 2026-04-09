"""
Análise de Sentimentos para Observações de Avaliações de Desempenho.

Extrai tom, urgência e contexto das observações textuais.
"""

from dataclasses import dataclass
from enum import Enum
import re


class SentimentTone(str, Enum):
    """Tom do sentimento identificado."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CONSTRUCTIVE = "constructive"


class UrgencyLevel(str, Enum):
    """Nível de urgência para desenvolvimento."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SentimentAnalysis:
    """Resultado da análise de sentimento."""
    tone: SentimentTone
    urgency: UrgencyLevel
    confidence: float
    key_phrases: list[str]
    development_hints: list[str]


class SentimentAnalyzer:
    """
    Analisador de sentimentos para observações de avaliações.

    Usa abordagem híbrida:
    - Regras baseadas em padrões linguísticos
    - Análise de palavras-chave
    - Contexto da competência
    """

    # Padrões linguísticos para detecção de tom
    POSITIVE_PATTERNS = [
        r"\b(excelente|ótim[oa]|muito bem|destaca|supera|excepcional)\b",
        r"\b(mandou bem|parabéns|continuar|manter)\b",
        r"\b(evolução|progresso|crescimento|avanç[oa])\b",
    ]

    NEGATIVE_PATTERNS = [
        r"\b(precis[ao] melhorar|abaixo|insuficiente|falha|dificuldade)\b",
        r"\b(não|nunca|raramente)\s+\w+",
        r"\b(crítico|urgente|imediato)\b",
    ]

    CONSTRUCTIVE_PATTERNS = [
        r"\b(pode melhorar|desenvolver|ampliar|expandir|aprimorar)\b",
        r"\b(oportunidade|sugestão|recomend[oa])\b",
        r"\b(ainda|em desenvolvimento|evoluindo)\b",
    ]

    # Palavras-chave de urgência
    URGENCY_KEYWORDS = {
        "critical": ["crítico", "urgente", "imediato", "essencial", "bloqueador"],
        "high": ["importante", "significativo", "deve", "precisa", "necessário"],
        "medium": ["pode", "recomend", "suger", "consider", "convém"],
        "low": ["opcional", "futuro", "eventualmente", "quando possível"],
    }

    # Hints de desenvolvimento por padrão
    DEVELOPMENT_HINTS = {
        "comunicação": ["comunicação assertiva", "feedback", "apresentações"],
        "técnico": ["técnica", "tecnologia", "ferramenta", "método"],
        "liderança": ["gestão", "equipe", "delegação", "motivação"],
        "estratégia": ["visão", "negócio", "cliente", "impacto", "produto"],
        "colaboração": ["time", "equipe", "colabor", "compartilh"],
        "eficiência": ["prazo", "objetivo", "resultado", "entrega"],
        "aprendizado": ["aprend", "estudo", "conhecimento", "curso"],
    }

    def analyze(
        self,
        observation: str,
        competency_name: str,
        score: float,
        evaluator_role: str,
    ) -> SentimentAnalysis:
        """
        Analisa o sentimento de uma observação.

        Args:
            observation: Texto da observação
            competency_name: Nome da competência avaliada
            score: Nota atribuída (0-10)
            evaluator_role: Papel do avaliador (auto, par, gestor)

        Returns:
            SentimentAnalysis com tom, urgência e hints
        """
        observation_lower = observation.lower()

        # Detectar tom
        tone = self._detect_tone(observation_lower, score)

        # Detectar urgência
        urgency = self._detect_urgency(observation_lower, score, evaluator_role)

        # Extrair frases-chave
        key_phrases = self._extract_key_phrases(observation)

        # Gerar hints de desenvolvimento
        dev_hints = self._generate_development_hints(
            observation_lower, competency_name, tone
        )

        # Calcular confiança baseado em múltiplos sinais
        confidence = self._calculate_confidence(observation, score, tone)

        return SentimentAnalysis(
            tone=tone,
            urgency=urgency,
            confidence=confidence,
            key_phrases=key_phrases,
            development_hints=dev_hints,
        )

    def _detect_tone(self, observation: str, score: float) -> SentimentTone:
        """Detecta o tom da observação."""
        positive_matches = sum(
            1 for pattern in self.POSITIVE_PATTERNS
            if re.search(pattern, observation)
        )

        negative_matches = sum(
            1 for pattern in self.NEGATIVE_PATTERNS
            if re.search(pattern, observation)
        )

        constructive_matches = sum(
            1 for pattern in self.CONSTRUCTIVE_PATTERNS
            if re.search(pattern, observation)
        )

        # Lógica de decisão considerando nota e padrões
        if score >= 8 and positive_matches > 0:
            return SentimentTone.POSITIVE
        elif constructive_matches > 0 or "pode melhorar" in observation:
            return SentimentTone.CONSTRUCTIVE
        elif negative_matches > positive_matches and score < 6:
            return SentimentTone.NEGATIVE
        else:
            return SentimentTone.NEUTRAL

    def _detect_urgency(
        self, observation: str, score: float, evaluator_role: str
    ) -> UrgencyLevel:
        """Detecta o nível de urgência para desenvolvimento."""
        # Gestor tem peso maior que auto-avaliação
        role_weight = 1.5 if evaluator_role == "gestor" else 1.0

        # Verifica palavras-chave de urgência
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(kw in observation for kw in keywords):
                if level == "critical":
                    return UrgencyLevel.CRITICAL
                elif level == "high":
                    return UrgencyLevel.HIGH
                elif level == "medium":
                    return UrgencyLevel.MEDIUM

        # Baseado em nota (com peso do avaliador)
        adjusted_score = score * role_weight

        if adjusted_score < 4:
            return UrgencyLevel.CRITICAL
        elif adjusted_score < 6:
            return UrgencyLevel.HIGH
        elif adjusted_score < 7:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    def _extract_key_phrases(self, observation: str) -> list[str]:
        """Extrai frases-chave da observação."""
        # Remove pontuação e divide em sentenças
        sentences = [s.strip() for s in observation.split(".") if s.strip()]

        # Filtra sentenças curtas e significativas
        key_phrases = [
            s for s in sentences
            if len(s.split()) >= 3 and len(s.split()) <= 15
        ]

        return key_phrases[:3]  # Máximo 3 frases-chave

    def _generate_development_hints(
        self, observation: str, competency: str, tone: SentimentTone
    ) -> list[str]:
        """Gera hints de desenvolvimento baseado no contexto."""
        hints = []

        # Adiciona hints específicos da competência
        for category, keywords in self.DEVELOPMENT_HINTS.items():
            if any(kw in competency.lower() or kw in observation for kw in keywords):
                hints.append(category)

        # Adiciona hints baseados no tom
        if tone == SentimentTone.CONSTRUCTIVE:
            if "visão" in observation or "negócio" in observation:
                hints.append("visão_estratégica")
            if "comunicação" in observation or "objetivo" in observation:
                hints.append("comunicação_efetiva")

        return list(set(hints))  # Remove duplicatas

    def _calculate_confidence(
        self, observation: str, score: float, tone: SentimentTone
    ) -> float:
        """
        Calcula confiança na análise.

        Maior confiança quando:
        - Observação é detalhada (mais de 5 palavras)
        - Tom e nota são consistentes
        - Múltiplos padrões foram detectados
        """
        confidence = 0.5  # Base

        # Comprimento da observação
        word_count = len(observation.split())
        if word_count > 10:
            confidence += 0.2
        elif word_count > 5:
            confidence += 0.1

        # Consistência entre nota e tom
        if (score >= 7 and tone == SentimentTone.POSITIVE) or \
           (score < 6 and tone in [SentimentTone.CONSTRUCTIVE, SentimentTone.NEGATIVE]):
            confidence += 0.2

        # Múltiplos padrões detectados
        pattern_count = sum([
            any(re.search(p, observation.lower()) for p in self.POSITIVE_PATTERNS),
            any(re.search(p, observation.lower()) for p in self.NEGATIVE_PATTERNS),
            any(re.search(p, observation.lower()) for p in self.CONSTRUCTIVE_PATTERNS),
        ])

        if pattern_count >= 2:
            confidence += 0.1

        return min(confidence, 1.0)  # Cap em 1.0

    def analyze_all_observations(
        self, evaluation_data: dict
    ) -> dict[str, list[SentimentAnalysis]]:
        """
        Analisa todas as observações de uma avaliação.

        Args:
            evaluation_data: Dados da avaliação completa

        Returns:
            Dict com competência -> lista de análises (auto, par, gestor)
        """
        results = {}

        valores = evaluation_data.get("valores", {})

        for competency_name, perspectives in valores.items():
            analyses = []

            for role, data in perspectives.items():
                if "observacao" in data and data["observacao"]:
                    analysis = self.analyze(
                        observation=data["observacao"],
                        competency_name=competency_name,
                        score=data.get("nota", 0),
                        evaluator_role=role,
                    )
                    analyses.append((role, analysis))

            if analyses:
                results[competency_name] = analyses

        return results
