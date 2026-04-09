#!/usr/bin/env python3
"""
Script de Validação do Sistema de Recomendação.

Executa bateria de testes para validar:
- Personalização por perfil
- Cobertura de gaps
- Diversidade das recomendações
- Cold start handling
- Performance

Usage:
    python validate_recommendations.py
    python validate_recommendations.py --employee "Ana Paula Ferreira"
    python validate_recommendations.py --full-report
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from talent_boost_core.profile_builder import EmployeeProfileBuilder
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine
from talent_boost_core.sentiment_analyzer import SentimentAnalyzer
from talent_boost_core.competency_gap_detector import CompetencyGapDetector


# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def load_courses() -> list[dict]:
    """Carrega catálogo de cursos."""
    all_courses = []
    treinamentos_dir = Path(__file__).parent / "treinamentos"

    if not treinamentos_dir.exists():
        raise FileNotFoundError(f"Diretório de treinamentos não encontrado: {treinamentos_dir}")

    for json_file in treinamentos_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            courses = json.load(f)
            all_courses.extend(courses)

    if not all_courses:
        raise ValueError("Nenhum curso encontrado")

    return all_courses


def load_employee_data(employee_name: str) -> tuple[dict, dict, dict]:
    """Carrega dados de um colaborador."""
    data_dir = Path(__file__).parent / "data" / "avaliacoes"

    # Mapeia nomes para arquivos
    file_map = {
        "Ana Paula Ferreira": "ana_paula_ferreira",
        "Colaborador Modelo": "colaborador_modelo",
    }

    file_key = file_map.get(employee_name, employee_name.lower().replace(" ", "_"))

    try:
        with open(data_dir / f"{file_key}.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        return (
            data.get("avaliacao", {}),
            data.get("historico_treinamento", {}),
            data.get("perfil_profissional", {}),
        )
    except FileNotFoundError:
        raise ValueError(f"Dados não encontrados para: {employee_name}")


def print_section(title: str):
    """Imprime cabeçalho de seção."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_check(test_name: str, passed: bool, details: str = ""):
    """Imprime resultado de teste."""
    if passed:
        symbol = f"{Colors.GREEN}✓{Colors.RESET}"
        status = f"{Colors.GREEN}PASS{Colors.RESET}"
    else:
        symbol = f"{Colors.RED}✗{Colors.RESET}"
        status = f"{Colors.RED}FAIL{Colors.RESET}"

    print(f"{symbol} [{status}] {test_name}")
    if details:
        print(f"  └─ {details}")


def validate_personalization(profile: Any, recommendations: list) -> dict:
    """Valida se recomendações são personalizadas."""
    results = {}

    # 1. Cobertura de gaps
    all_gaps = {g.competency_name for g in profile.gaps_identificados}
    addressed_gaps = set()

    for rec in recommendations:
        addressed_gaps.update(rec.addresses_gaps)

    gap_coverage = len(addressed_gaps) / len(all_gaps) if all_gaps else 0
    results["gap_coverage"] = gap_coverage
    print_check(
        "Cobertura de Gaps",
        gap_coverage >= 0.6,
        f"{len(addressed_gaps)}/{len(all_gaps)} gaps endereçados ({gap_coverage*100:.0f}%)"
    )

    # 2. Adequação ao nível
    nivel = profile.nivel.lower()
    nivel_keywords = {
        "junior": ["fundamentos", "introdução", "básico"],
        "senior": ["avançado", "expert", "arquitetura"],
    }

    nivel_appropriate = 0
    for rec in recommendations:
        titulo_lower = rec.titulo.lower()
        if nivel in nivel_keywords:
            if any(kw in titulo_lower for kw in nivel_keywords[nivel]):
                nivel_appropriate += 1

    nivel_score = nivel_appropriate / len(recommendations) if recommendations else 0
    results["nivel_match"] = nivel_score
    print_check(
        f"Adequação ao Nível ({profile.nivel})",
        nivel_score >= 0.3,
        f"{nivel_appropriate}/{len(recommendations)} cursos com keywords de nível ({nivel_score*100:.0f}%)"
    )

    # 3. Relevância média
    avg_relevance = sum(r.relevance_score for r in recommendations) / len(recommendations) if recommendations else 0
    results["avg_relevance"] = avg_relevance
    print_check(
        "Relevância Média",
        avg_relevance >= 0.6,
        f"Score médio: {avg_relevance:.2f}"
    )

    # 4. Priorização por severidade
    critical_gaps = [g for g in profile.gaps_identificados if g.gap_severity in ["critical", "high"]]
    if critical_gaps:
        top_priorities = [r.priority for r in recommendations[:3]]
        has_high_priority = any(p in ["critical", "high"] for p in top_priorities)
        results["prioritization"] = has_high_priority
        print_check(
            "Priorização Correta",
            has_high_priority,
            f"Top 3 incluem prioridades: {', '.join(top_priorities)}"
        )
    else:
        results["prioritization"] = True
        print_check("Priorização Correta", True, "Sem gaps críticos")

    return results


def validate_diversity(recommendations: list) -> dict:
    """Valida diversidade das recomendações."""
    results = {}

    if not recommendations:
        print_check("Diversidade de Categorias", False, "Nenhuma recomendação gerada")
        return {"diversity_score": 0}

    # 1. Diversidade de categorias
    categories = [r.categoria for r in recommendations]
    unique_categories = len(set(categories))
    diversity_score = unique_categories / len(categories)
    results["diversity_score"] = diversity_score
    print_check(
        "Diversidade de Categorias",
        diversity_score >= 0.5,
        f"{unique_categories}/{len(categories)} categorias únicas ({diversity_score*100:.0f}%)"
    )

    # 2. Mix de modalidades
    modalidades = [r.modalidade for r in recommendations]
    has_ead = "EAD" in modalidades
    has_presencial = "Presencial" in modalidades
    has_mix = has_ead and has_presencial
    results["modality_mix"] = has_mix
    print_check(
        "Mix de Modalidades",
        True,  # Não é obrigatório
        f"EAD: {modalidades.count('EAD')}, Presencial: {modalidades.count('Presencial')}"
    )

    # 3. Variação de carga horária
    cargas = [r.carga_horaria for r in recommendations]
    carga_variance = len(set(cargas)) / len(cargas) if cargas else 0
    results["workload_variance"] = carga_variance
    print_check(
        "Variação de Carga Horária",
        carga_variance >= 0.4,
        f"{len(set(cargas))}/{len(cargas)} cargas distintas ({carga_variance*100:.0f}%)"
    )

    return results


def validate_explanations(recommendations: list) -> dict:
    """Valida explicabilidade (XAI)."""
    results = {}

    # Todas as recomendações devem ter explicação
    all_have_explanation = all(r.explanation is not None for r in recommendations)
    results["has_explanations"] = all_have_explanation
    print_check(
        "Explicações Presentes",
        all_have_explanation,
        f"{sum(1 for r in recommendations if r.explanation)}/{len(recommendations)} com XAI"
    )

    # Confidence média
    confidences = [r.explanation.confidence for r in recommendations if r.explanation]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    results["avg_confidence"] = avg_confidence
    print_check(
        "Confiança Média",
        avg_confidence >= 0.5,
        f"Confidence: {avg_confidence:.2f}"
    )

    # Razões primárias diversificadas
    primary_reasons = [r.explanation.primary_reason for r in recommendations if r.explanation]
    unique_reasons = len(set(primary_reasons))
    results["reason_diversity"] = unique_reasons
    print_check(
        "Diversidade de Razões",
        True,  # Informativo
        f"{unique_reasons} tipos de razões primárias"
    )

    return results


def validate_cold_start(engine: TrainingRecommendationEngine) -> dict:
    """Valida tratamento de cold start."""
    results = {}

    # Cria perfil sem gaps (novo colaborador)
    from talent_boost_core.profile_builder import (
        EmployeeProfile,
        TrainingHistory,
    )

    cold_profile = EmployeeProfile(
        colaborador_id="COLD001",
        nome="Novo Colaborador",
        cargo="Desenvolvedor",
        departamento="TI",
        nivel="Junior",
        gaps_identificados=[],  # SEM GAPS
        pontos_fortes=["Proatividade"],
        training_history=TrainingHistory(
            completed_courses=[],
            recent_courses=[],
            preferred_modality=None,
        ),
        last_evaluation_date=None,
    )

    # Gera recomendações
    recommendations = engine.recommend(cold_profile, top_n=5)

    # Deve retornar recomendações mesmo sem gaps
    has_recommendations = len(recommendations) > 0
    results["cold_start_handled"] = has_recommendations
    print_check(
        "Cold Start - Recomendações Geradas",
        has_recommendations,
        f"{len(recommendations)} cursos recomendados sem avaliação"
    )

    # Recomendações devem incluir obrigatórios
    has_mandatory = any(r.obrigatorio for r in recommendations)
    results["includes_mandatory"] = has_mandatory
    print_check(
        "Cold Start - Cursos Obrigatórios",
        has_mandatory,
        "Inclui cursos mandatórios"
    )

    return results


def validate_performance(engine: TrainingRecommendationEngine, profile: Any) -> dict:
    """Valida performance do sistema."""
    import time

    results = {}

    # 1. Teste de resposta sem cache
    engine.enable_cache = False
    start = time.time()
    _ = engine.recommend(profile, top_n=5)
    no_cache_time = (time.time() - start) * 1000  # ms

    results["no_cache_ms"] = no_cache_time
    print_check(
        "Performance Sem Cache",
        no_cache_time < 500,
        f"{no_cache_time:.2f}ms"
    )

    # 2. Teste com cache
    engine.enable_cache = True
    start = time.time()
    _ = engine.recommend(profile, top_n=5)
    start = time.time()
    _ = engine.recommend(profile, top_n=5)  # Segunda vez = cache hit
    cache_time = (time.time() - start) * 1000  # ms

    results["cache_ms"] = cache_time
    print_check(
        "Performance Com Cache",
        cache_time < 50,
        f"{cache_time:.2f}ms (speedup: {no_cache_time/cache_time:.1f}x)"
    )

    # 3. Cache TTL
    cache_ttl = engine._cache_ttl
    results["cache_ttl"] = cache_ttl
    print_check(
        "Cache TTL Configurado",
        cache_ttl > 0,
        f"{cache_ttl}s"
    )

    return results


def generate_report(employee_name: str, full_report: bool = False):
    """Gera relatório completo de validação."""
    print_section(f"Validação de Recomendações - {employee_name}")

    # Setup
    courses = load_courses()
    engine = TrainingRecommendationEngine(courses)

    sentiment_analyzer = SentimentAnalyzer()
    gap_detector = CompetencyGapDetector(sentiment_analyzer)
    profile_builder = EmployeeProfileBuilder(gap_detector)

    # Carrega dados
    avaliacao, historico, perfil = load_employee_data(employee_name)
    profile = profile_builder.build_profile(avaliacao, historico, perfil)

    # Gera recomendações
    recommendations = engine.recommend(profile, top_n=5)

    print(f"{Colors.BOLD}Perfil:{Colors.RESET}")
    print(f"  Nome: {profile.nome}")
    print(f"  Cargo: {profile.cargo}")
    print(f"  Nível: {profile.nivel}")
    print(f"  Gaps: {len(profile.gaps_identificados)}")
    print(f"  Recomendações: {len(recommendations)}")

    # Validações
    all_results = {}

    print_section("1. Validação de Personalização")
    all_results["personalization"] = validate_personalization(profile, recommendations)

    print_section("2. Validação de Diversidade")
    all_results["diversity"] = validate_diversity(recommendations)

    print_section("3. Validação de Explicabilidade (XAI)")
    all_results["explanations"] = validate_explanations(recommendations)

    print_section("4. Validação de Cold Start")
    all_results["cold_start"] = validate_cold_start(engine)

    print_section("5. Validação de Performance")
    all_results["performance"] = validate_performance(engine, profile)

    # Resumo final
    print_section("Resumo da Validação")

    total_tests = 0
    passed_tests = 0

    for category, results in all_results.items():
        for key, value in results.items():
            total_tests += 1
            if isinstance(value, bool) and value:
                passed_tests += 1
            elif isinstance(value, (int, float)) and value >= 0.5:
                passed_tests += 1

    success_rate = passed_tests / total_tests if total_tests > 0 else 0

    print(f"Total de Testes: {total_tests}")
    print(f"Testes Passados: {Colors.GREEN}{passed_tests}{Colors.RESET}")
    print(f"Taxa de Sucesso: {Colors.GREEN if success_rate >= 0.8 else Colors.YELLOW}{success_rate*100:.0f}%{Colors.RESET}\n")

    # Detalhes das recomendações
    if full_report:
        print_section("Detalhes das Recomendações")
        for i, rec in enumerate(recommendations, 1):
            print(f"{Colors.BOLD}{i}. {rec.titulo}{Colors.RESET}")
            print(f"   Categoria: {rec.categoria}")
            print(f"   Modalidade: {rec.modalidade}")
            print(f"   Carga: {rec.carga_horaria}h")
            print(f"   Prioridade: {rec.priority}")
            print(f"   Relevância: {rec.relevance_score:.2f}")
            print(f"   Razão: {rec.match_reason}")
            if rec.explanation:
                print(f"   Confiança: {rec.explanation.confidence:.2f}")
                print(f"   Gaps: {', '.join(rec.addresses_gaps)}")
            print()

    # Status final
    if success_rate >= 0.8:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ VALIDAÇÃO APROVADA{Colors.RESET}\n")
        return 0
    elif success_rate >= 0.6:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ VALIDAÇÃO COM RESSALVAS{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ VALIDAÇÃO REPROVADA{Colors.RESET}\n")
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="Valida eficácia do sistema de recomendação"
    )
    parser.add_argument(
        "--employee",
        default="Ana Paula Ferreira",
        help="Nome do colaborador para testar"
    )
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Exibe relatório completo com detalhes de cada recomendação"
    )

    args = parser.parse_args()

    try:
        exit_code = generate_report(args.employee, args.full_report)
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Colors.RED}ERRO: {e}{Colors.RESET}")
        sys.exit(3)


if __name__ == "__main__":
    main()
