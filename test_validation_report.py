#!/usr/bin/env python3
"""
Relatório de Validação do Sistema de Recomendação.
Testa e valida a eficácia das recomendações.
"""

import requests
import json
from typing import Dict, List

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Imprime cabeçalho."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_result(label: str, value: str, status: str = "info"):
    """Imprime resultado formatado."""
    color = {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.CYAN
    }.get(status, Colors.RESET)

    print(f"{color}▸ {label}:{Colors.RESET} {value}")


def validate_gap_coverage(gaps: List[Dict], recommendations: List[Dict]) -> Dict:
    """Valida se as recomendações cobrem os gaps."""
    print_header("1. VALIDAÇÃO DE COBERTURA DE GAPS")

    # Extrai competências dos gaps
    gap_competencies = {g['competency_name'] for g in gaps}

    # Extrai competências endereçadas pelas recomendações
    addressed_competencies = set()
    for rec in recommendations:
        addressed_competencies.update(rec.get('addresses_gaps', []))

    # Calcula cobertura
    coverage = len(addressed_competencies) / len(gap_competencies) if gap_competencies else 0

    print_result("Total de Gaps Identificados", str(len(gaps)), "info")
    print_result("Gaps Endereçados", f"{len(addressed_competencies)}/{len(gap_competencies)}",
                 "success" if coverage >= 0.6 else "warning")
    print_result("Taxa de Cobertura", f"{coverage*100:.1f}%",
                 "success" if coverage >= 0.6 else "warning")

    # Mostra gaps não cobertos
    uncovered = gap_competencies - addressed_competencies
    if uncovered:
        print(f"\n{Colors.YELLOW}Gaps NÃO cobertos:{Colors.RESET}")
        for gap in uncovered:
            print(f"  • {gap}")

    return {
        "total_gaps": len(gaps),
        "addressed_gaps": len(addressed_competencies),
        "coverage_rate": coverage,
        "uncovered": list(uncovered)
    }


def validate_recommendation_quality(recommendations: List[Dict], gaps: List[Dict]) -> Dict:
    """Valida qualidade das recomendações."""
    print_header("2. VALIDAÇÃO DE QUALIDADE DAS RECOMENDAÇÕES")

    if not recommendations:
        print_result("Status", "❌ NENHUMA RECOMENDAÇÃO GERADA", "error")
        return {"quality_score": 0}

    # Relevância média
    avg_relevance = sum(r['relevance_score'] for r in recommendations) / len(recommendations)
    print_result("Relevância Média", f"{avg_relevance:.2f}",
                 "success" if avg_relevance >= 0.6 else "warning")

    # Diversidade de categorias
    categories = [r['categoria'] for r in recommendations]
    unique_categories = len(set(categories))
    diversity = unique_categories / len(categories)
    print_result("Diversidade de Categorias", f"{unique_categories}/{len(categories)} ({diversity*100:.0f}%)",
                 "success" if diversity >= 0.5 else "warning")

    # Priorização
    priorities = [r['priority'] for r in recommendations]
    high_priority_count = sum(1 for p in priorities if p in ['critical', 'high'])
    critical_gaps = sum(1 for g in gaps if g['gap_severity'] in ['critical', 'high'])

    print_result("Recomendações Prioritárias", f"{high_priority_count}/{len(recommendations)}",
                 "success" if high_priority_count > 0 or critical_gaps == 0 else "warning")

    # Explicabilidade
    with_explanation = sum(1 for r in recommendations if r.get('explanation'))
    print_result("Com Explicação (XAI)", f"{with_explanation}/{len(recommendations)}",
                 "success" if with_explanation == len(recommendations) else "warning")

    return {
        "avg_relevance": avg_relevance,
        "diversity": diversity,
        "high_priority_count": high_priority_count,
        "with_explanation": with_explanation
    }


def analyze_manual_matches(gaps: List[Dict], courses: List[Dict]) -> Dict:
    """Análise manual de matches esperados."""
    print_header("3. ANÁLISE MANUAL DE MATCHES ESPERADOS")

    # Mapeia gaps para cursos esperados
    gap_to_expected_courses = {
        "Inovação com Foco no Cliente": [
            "Design Thinking e Inovação",
            "Metodologias Ágeis e Scrum"
        ],
        "Comunicação Direta e Objetiva": [
            "Comunicação Assertiva"
        ],
        "Colaboração e Trabalho em Equipe": [
            "Feedback e Desenvolvimento de Equipes",
            "Metodologias Ágeis e Scrum",
            "Gestão de Pessoas e Liderança"
        ]
    }

    courses_dict = {c['titulo']: c for c in courses}

    expected_matches = []
    for gap in gaps:
        gap_name = gap['competency_name']
        if gap_name in gap_to_expected_courses:
            print(f"\n{Colors.BOLD}{gap_name}{Colors.RESET} (nota: {gap['average_score']}, severidade: {gap['gap_severity']})")
            print(f"{Colors.CYAN}Cursos esperados:{Colors.RESET}")

            for course_title in gap_to_expected_courses[gap_name]:
                if course_title in courses_dict:
                    course = courses_dict[course_title]
                    print(f"  ✓ {course_title} ({course['categoria']}, {course['cargaHoraria']}h)")
                    expected_matches.append({
                        "gap": gap_name,
                        "course": course_title,
                        "course_id": course['cursoID']
                    })
                else:
                    print(f"  ✗ {course_title} (NÃO ENCONTRADO NO CATÁLOGO)")

    return {"expected_matches": expected_matches}


def compare_with_expected(recommendations: List[Dict], expected_matches: List[Dict]) -> Dict:
    """Compara recomendações com matches esperados."""
    print_header("4. COMPARAÇÃO COM MATCHES ESPERADOS")

    recommended_ids = {r['curso_id'] for r in recommendations}
    expected_ids = {m['course_id'] for m in expected_matches}

    matched = recommended_ids & expected_ids
    missing = expected_ids - recommended_ids
    extra = recommended_ids - expected_ids

    precision = len(matched) / len(recommended_ids) if recommended_ids else 0
    recall = len(matched) / len(expected_ids) if expected_ids else 0

    print_result("Cursos Esperados", str(len(expected_ids)), "info")
    print_result("Cursos Recomendados", str(len(recommended_ids)), "info")
    print_result("Matches Corretos", str(len(matched)),
                 "success" if len(matched) > 0 else "warning")
    print_result("Precision (relevância)", f"{precision*100:.1f}%",
                 "success" if precision >= 0.6 else "warning")
    print_result("Recall (cobertura)", f"{recall*100:.1f}%",
                 "success" if recall >= 0.4 else "warning")

    if missing:
        print(f"\n{Colors.YELLOW}Cursos esperados MAS NÃO recomendados:{Colors.RESET}")
        for match in expected_matches:
            if match['course_id'] not in recommended_ids:
                print(f"  • {match['course']} (para gap: {match['gap']})")

    if extra:
        print(f"\n{Colors.CYAN}Cursos recomendados ALÉM do esperado:{Colors.RESET}")
        for rec in recommendations:
            if rec['curso_id'] not in expected_ids:
                print(f"  • {rec['titulo']} (relevância: {rec['relevance_score']:.2f})")

    return {
        "precision": precision,
        "recall": recall,
        "matched": len(matched),
        "missing": len(missing),
        "extra": len(extra)
    }


def generate_final_score(results: Dict) -> Dict:
    """Gera score final da validação."""
    print_header("5. SCORE FINAL DE VALIDAÇÃO")

    # Pesos
    weights = {
        "coverage": 0.3,
        "relevance": 0.25,
        "precision": 0.25,
        "recall": 0.2
    }

    scores = {
        "coverage": results.get('gap_coverage', {}).get('coverage_rate', 0),
        "relevance": min(results.get('quality', {}).get('avg_relevance', 0) / 0.8, 1.0),  # normaliza para 0-1
        "precision": results.get('comparison', {}).get('precision', 0),
        "recall": results.get('comparison', {}).get('recall', 0)
    }

    final_score = sum(scores[k] * weights[k] for k in weights)

    print_result("Cobertura de Gaps", f"{scores['coverage']*100:.1f}%",
                 "success" if scores['coverage'] >= 0.6 else "warning")
    print_result("Relevância Média", f"{scores['relevance']*100:.1f}%",
                 "success" if scores['relevance'] >= 0.75 else "warning")
    print_result("Precision", f"{scores['precision']*100:.1f}%",
                 "success" if scores['precision'] >= 0.6 else "warning")
    print_result("Recall", f"{scores['recall']*100:.1f}%",
                 "success" if scores['recall'] >= 0.4 else "warning")

    print(f"\n{Colors.BOLD}SCORE FINAL: {final_score*100:.1f}%{Colors.RESET}")

    if final_score >= 0.7:
        status = f"{Colors.GREEN}✓ SISTEMA VALIDADO{Colors.RESET}"
        recommendation = "O sistema está funcionando adequadamente."
    elif final_score >= 0.5:
        status = f"{Colors.YELLOW}⚠ VALIDAÇÃO COM RESSALVAS{Colors.RESET}"
        recommendation = "Sistema funcional mas precisa de melhorias."
    else:
        status = f"{Colors.RED}✗ VALIDAÇÃO REPROVADA{Colors.RESET}"
        recommendation = "Sistema precisa de ajustes significativos."

    print(f"\n{status}")
    print(f"{Colors.CYAN}→ {recommendation}{Colors.RESET}\n")

    return {"final_score": final_score, "scores": scores}


def main():
    BASE_URL = "http://localhost:8001/api"
    EMPLOYEE = "Ana Paula Ferreira"

    print_header("RELATÓRIO DE VALIDAÇÃO - SISTEMA DE RECOMENDAÇÃO")
    print(f"{Colors.BOLD}Colaborador:{Colors.RESET} {EMPLOYEE}")
    print(f"{Colors.BOLD}Data:{Colors.RESET} 2026-04-06\n")

    try:
        # 1. Busca gaps
        print("Buscando gaps identificados...")
        gaps_response = requests.get(f"{BASE_URL}/employees/{EMPLOYEE}/gaps")
        gaps_data = gaps_response.json()
        gaps = gaps_data['gaps']

        # 2. Busca recomendações
        print("Gerando recomendações personalizadas...")
        rec_response = requests.post(
            f"{BASE_URL}/employees/{EMPLOYEE}/recommendations",
            json={"employee_name": EMPLOYEE, "top_n": 5, "exclude_completed": True}
        )
        rec_data = rec_response.json()
        recommendations = rec_data['recommendations']

        # 3. Busca cursos disponíveis
        print("Carregando catálogo de cursos...")
        courses_response = requests.get(f"{BASE_URL}/courses")
        courses_data = courses_response.json()
        courses = courses_data['courses']

        print(f"\n{Colors.GREEN}✓ Dados carregados com sucesso!{Colors.RESET}")

        # Validações
        results = {}

        # 1. Cobertura de gaps
        results['gap_coverage'] = validate_gap_coverage(gaps, recommendations)

        # 2. Qualidade
        results['quality'] = validate_recommendation_quality(recommendations, gaps)

        # 3. Análise manual
        analysis = analyze_manual_matches(gaps, courses)

        # 4. Comparação
        results['comparison'] = compare_with_expected(recommendations, analysis['expected_matches'])

        # 5. Score final
        results['final'] = generate_final_score(results)

        # Salva relatório
        with open('validation_report.json', 'w', encoding='utf-8') as f:
            json.dump({
                "employee": EMPLOYEE,
                "gaps": gaps,
                "recommendations": recommendations,
                "results": results
            }, f, indent=2, ensure_ascii=False)

        print(f"{Colors.CYAN}📄 Relatório completo salvo em: validation_report.json{Colors.RESET}\n")

    except Exception as e:
        print(f"\n{Colors.RED}❌ ERRO: {e}{Colors.RESET}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
