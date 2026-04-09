"""
Script de demonstração do TalentBoost.

Executa o pipeline completo:
1. Carrega dados de um colaborador
2. Analisa sentimentos nas observações
3. Detecta gaps de competências
4. Constrói perfil completo
5. Gera recomendações personalizadas
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Import dos componentes
from talent_boost_core.sentiment_analyzer import SentimentAnalyzer
from talent_boost_core.competency_gap_detector import CompetencyGapDetector
from talent_boost_core.profile_builder import EmployeeProfileBuilder
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine


console = Console()


def load_employee_data(employee_name: str, data_dir: Path):
    """Carrega todos os dados de um colaborador."""
    # Normaliza nome para nome de arquivo
    normalized = employee_name.lower().replace(" ", "_")

    # Carrega avaliação
    avaliacao_path = data_dir / "avaliacoes" / f"avaliacao_{normalized}.json"
    if not avaliacao_path.exists():
        raise FileNotFoundError(f"Avaliação não encontrada: {avaliacao_path}")

    with open(avaliacao_path, "r", encoding="utf-8") as f:
        avaliacao = json.load(f)

    # Carrega dados cadastrais
    cadastro_path = data_dir / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"
    if not cadastro_path.exists():
        raise FileNotFoundError(f"Dados cadastrais não encontrados: {cadastro_path}")

    with open(cadastro_path, "r", encoding="utf-8") as f:
        cadastro = json.load(f)

    # Carrega treinamentos
    treinamento_path = data_dir / "treinamentos" / f"treinamentos_{normalized}.json"
    if not treinamento_path.exists():
        console.print(f"[yellow]⚠ Histórico de treinamentos não encontrado, usando dados vazios[/yellow]")
        treinamentos = {"colaboradores": [], "cursos": [], "matriculas": [], "resultados": []}
    else:
        with open(treinamento_path, "r", encoding="utf-8") as f:
            treinamentos = json.load(f)

    return avaliacao, cadastro, treinamentos


def load_all_courses(data_dir: Path):
    """Carrega todos os cursos disponíveis."""
    all_courses = []
    treinamentos_dir = data_dir / "treinamentos"

    for file in treinamentos_dir.glob("treinamentos_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            courses = data.get("cursos", [])
            # Deduplica
            for course in courses:
                if not any(c.get("cursoID") == course.get("cursoID") for c in all_courses):
                    all_courses.append(course)

    return all_courses


def display_sentiment_analysis(sentiment_results: dict):
    """Exibe análise de sentimentos."""
    console.print("\n[bold cyan]📊 Análise de Sentimentos das Observações[/bold cyan]\n")

    for competency, analyses in sentiment_results.items():
        console.print(f"[bold]{competency}[/bold]")

        table = Table(box=box.SIMPLE)
        table.add_column("Avaliador", style="cyan")
        table.add_column("Tom", style="magenta")
        table.add_column("Urgência", style="yellow")
        table.add_column("Confiança", style="green")
        table.add_column("Hints", style="blue")

        for role, analysis in analyses:
            table.add_row(
                role.capitalize(),
                analysis.tone.value,
                analysis.urgency.value,
                f"{analysis.confidence:.0%}",
                ", ".join(analysis.development_hints[:2]) if analysis.development_hints else "-",
            )

        console.print(table)
        console.print()


def display_gaps(gaps):
    """Exibe gaps de competências."""
    console.print("\n[bold red]🎯 Gaps de Competências Identificados[/bold red]\n")

    if not gaps:
        console.print("[green]✓ Nenhum gap crítico identificado![/green]")
        return

    table = Table(box=box.ROUNDED)
    table.add_column("Competência", style="cyan", width=30)
    table.add_column("Nota", justify="center", style="yellow")
    table.add_column("Severidade", justify="center", style="red")
    table.add_column("Urgência", justify="center", style="magenta")
    table.add_column("Consenso", justify="center", style="green")
    table.add_column("Contexto", style="white", width=40)

    for gap in gaps:
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }

        table.add_row(
            gap.competency_name,
            f"{gap.average_score:.1f}",
            f"{severity_emoji.get(gap.gap_severity, '')} {gap.gap_severity}",
            gap.urgency.value,
            f"{gap.evaluator_consensus:.0%}",
            gap.context,
        )

    console.print(table)


def display_profile(profile):
    """Exibe perfil do colaborador."""
    console.print("\n[bold green]👤 Perfil do Colaborador[/bold green]\n")

    info = f"""
[bold]Nome:[/bold] {profile.nome}
[bold]Cargo:[/bold] {profile.cargo} ({profile.nivel})
[bold]Departamento:[/bold] {profile.departamento}
[bold]Tempo de Casa:[/bold] {profile.tempo_casa_meses} meses
[bold]É Gestor:[/bold] {"Sim" if profile.gestor else "Não"}

[bold cyan]Desempenho:[/bold cyan]
[bold]Nota Média Geral:[/bold] {profile.nota_media_geral:.2f}
[bold]Pontos Fortes:[/bold] {", ".join(profile.pontos_fortes) if profile.pontos_fortes else "N/A"}
[bold]Total de Gaps:[/bold] {len(profile.gaps_identificados)}

[bold magenta]Histórico de Treinamentos:[/bold magenta]
[bold]Cursos Concluídos:[/bold] {profile.training_history.completed_courses}
[bold]Cursos em Andamento:[/bold] {profile.training_history.in_progress_courses}
[bold]Taxa de Conclusão:[/bold] {profile.training_history.completion_rate:.0%}
[bold]Nota Média:[/bold] {profile.training_history.average_score:.1f}
[bold]Categorias Completadas:[/bold] {", ".join(profile.training_history.categories_completed) if profile.training_history.categories_completed else "N/A"}
    """

    console.print(Panel(info.strip(), title="Perfil Completo", border_style="green"))


def display_recommendations(recommendations, summary):
    """Exibe recomendações."""
    console.print("\n[bold yellow]🎓 Recomendações Personalizadas de Treinamentos[/bold yellow]\n")

    if not recommendations:
        console.print("[red]Nenhuma recomendação gerada.[/red]")
        return

    table = Table(box=box.DOUBLE)
    table.add_column("Prioridade", justify="center", style="red")
    table.add_column("Curso", style="cyan", width=30)
    table.add_column("Categoria", style="magenta")
    table.add_column("CH", justify="center", style="yellow")
    table.add_column("Relevância", justify="center", style="green")
    table.add_column("Razão", style="white", width=40)

    for rec in recommendations:
        priority_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
        }

        table.add_row(
            f"{priority_emoji.get(rec.priority, '')} {rec.priority.upper()}",
            rec.titulo,
            rec.categoria,
            f"{rec.carga_horaria}h",
            f"{rec.relevance_score:.0%}",
            rec.match_reason,
        )

    console.print(table)

    # Exibe resumo
    console.print(f"\n[bold]Resumo:[/bold]")
    console.print(f"  • Total de recomendações: {summary['total']}")
    console.print(f"  • Relevância média: {summary['average_relevance']:.0%}")

    if summary.get("by_priority"):
        console.print(f"\n[bold]Por Prioridade:[/bold]")
        for priority, courses in summary["by_priority"].items():
            console.print(f"  • {priority.upper()}: {len(courses)} curso(s)")


def main():
    """Executa demonstração completa."""
    console.print("[bold blue]" + "="*70 + "[/bold blue]")
    console.print("[bold blue]  LG TalentBoost - Sistema Inteligente de Recomendação de Treinamentos[/bold blue]")
    console.print("[bold blue]" + "="*70 + "[/bold blue]\n")

    # Diretório de dados
    data_dir = Path(__file__).parent

    # Colaborador exemplo
    employee_name = "Ana Paula Ferreira"

    console.print(f"[bold]Analisando colaborador:[/bold] {employee_name}\n")

    # 1. Carrega dados
    console.print("[dim]→ Carregando dados...[/dim]")
    avaliacao, cadastro, treinamentos = load_employee_data(employee_name, data_dir)
    all_courses = load_all_courses(data_dir)
    console.print(f"[green]✓ Dados carregados ({len(all_courses)} cursos disponíveis)[/green]")

    # 2. Análise de sentimentos
    console.print("[dim]→ Analisando sentimentos das observações...[/dim]")
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_results = sentiment_analyzer.analyze_all_observations(avaliacao)
    console.print("[green]✓ Análise de sentimentos concluída[/green]")

    display_sentiment_analysis(sentiment_results)

    # 3. Detecção de gaps
    console.print("[dim]→ Detectando gaps de competências...[/dim]")
    gap_detector = CompetencyGapDetector(sentiment_analyzer)
    gaps = gap_detector.detect_gaps(avaliacao)
    console.print(f"[green]✓ {len(gaps)} gap(s) identificado(s)[/green]")

    display_gaps(gaps)

    # 4. Construção de perfil
    console.print("\n[dim]→ Construindo perfil completo...[/dim]")
    profile_builder = EmployeeProfileBuilder()
    profile = profile_builder.build_profile(
        employee_data=cadastro,
        evaluation_data=avaliacao,
        training_data=treinamentos,
        gaps=gaps,
    )
    console.print("[green]✓ Perfil construído[/green]")

    display_profile(profile)

    # 5. Geração de recomendações
    console.print("\n[dim]→ Gerando recomendações personalizadas...[/dim]")
    recommendation_engine = TrainingRecommendationEngine(all_courses)
    recommendations = recommendation_engine.recommend(profile, top_n=5)
    summary = recommendation_engine.get_recommendation_summary(recommendations)
    console.print(f"[green]✓ {len(recommendations)} recomendação(ões) gerada(s)[/green]")

    display_recommendations(recommendations, summary)

    # Finalização
    console.print("\n[bold blue]" + "="*70 + "[/bold blue]")
    console.print("[bold green]✓ Análise completa![/bold green]")
    console.print("[bold blue]" + "="*70 + "[/bold blue]\n")

    # Salva resultado em JSON
    output_file = data_dir / "demo_output.json"
    output = {
        "employee_name": employee_name,
        "profile": {
            "cargo": profile.cargo,
            "nivel": profile.nivel,
            "nota_media_geral": profile.nota_media_geral,
            "pontos_fortes": profile.pontos_fortes,
            "total_gaps": len(profile.gaps_identificados),
        },
        "gaps": [
            {
                "competency": g.competency_name,
                "score": g.average_score,
                "severity": g.gap_severity,
                "urgency": g.urgency.value,
            }
            for g in gaps
        ],
        "recommendations": [
            {
                "titulo": r.titulo,
                "categoria": r.categoria,
                "priority": r.priority,
                "relevance_score": r.relevance_score,
                "match_reason": r.match_reason,
            }
            for r in recommendations
        ],
        "summary": summary,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    console.print(f"[dim]Resultado salvo em: {output_file}[/dim]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red]Erro:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
