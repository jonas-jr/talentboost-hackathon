"""
TalentBoost Core Module

Módulo de análise inteligente para recomendação de treinamentos
baseada em avaliações de desempenho.

Componentes:
- sentiment_analyzer: Análise de sentimentos nas observações
- competency_gap_detector: Identificação de gaps de competências
- profile_builder: Construção de perfil do colaborador
- recommendation_engine: Sistema de recomendação híbrido
"""

from .sentiment_analyzer import SentimentAnalyzer
from .competency_gap_detector import CompetencyGapDetector
from .profile_builder import EmployeeProfileBuilder
from .recommendation_engine import TrainingRecommendationEngine

__all__ = [
    "SentimentAnalyzer",
    "CompetencyGapDetector",
    "EmployeeProfileBuilder",
    "TrainingRecommendationEngine",
]
