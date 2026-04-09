"""
Teste do sistema de recomendação com Cold Start.
"""
import json
from pathlib import Path
from talent_boost_core.profile_builder import EmployeeProfile, TrainingHistory
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine


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


# Carrega cursos
data_dir = Path(".")
cursos = load_all_courses(data_dir)
print(f"✓ Carregados {len(cursos)} cursos únicos")

# Cria motor de recomendação
engine = TrainingRecommendationEngine(cursos)

# Perfil SEM avaliação (cold start)
perfil_sem_avaliacao = EmployeeProfile(
    colaborador_id=999,
    nome="João Silva",
    cargo="Desenvolvedor Backend",
    cargo_codigo=101,
    departamento="Tecnologia",
    nivel="Pleno",
    tempo_casa_meses=12,
    gestor=False,
    ciclo_avaliacao="N/A",
    nota_media_geral=0.0,
    gaps_identificados=[],  # ← SEM GAPS = SEM AVALIAÇÃO
    pontos_fortes=[],
    training_history=TrainingHistory(
        total_courses=0,
        completed_courses=0,
        in_progress_courses=0,
        completion_rate=0.0,
        average_score=0.0,
        categories_completed=[],
        recent_courses=[]
    ),
    profile_created_at="2026-04-06",
    last_evaluation_date="N/A"
)

print()
print("=" * 80)
print("TESTE: COLD START (colaborador sem avaliação)")
print("=" * 80)
print(f"Nome: {perfil_sem_avaliacao.nome}")
print(f"Cargo: {perfil_sem_avaliacao.cargo}")
print(f"Nível: {perfil_sem_avaliacao.nivel}")
print(f"Departamento: {perfil_sem_avaliacao.departamento}")
print(f"Gaps identificados: {len(perfil_sem_avaliacao.gaps_identificados)}")
print()

# Gera recomendações
recomendacoes = engine.recommend(perfil_sem_avaliacao, top_n=5)

print(f"✓ Recomendações geradas: {len(recomendacoes)}")
print()

if recomendacoes:
    print("✅ COLD START FUNCIONOU! Recomendações geradas:")
    print()
    for i, rec in enumerate(recomendacoes, 1):
        print(f"{i}. {rec.titulo}")
        print(f"   Categoria: {rec.categoria}")
        print(f"   Modalidade: {rec.modalidade}")
        print(f"   Carga Horária: {rec.carga_horaria}h")
        print(f"   Obrigatório: {'Sim' if rec.obrigatorio else 'Não'}")
        print(f"   Prioridade: {rec.priority}")
        print(f"   Relevância: {rec.relevance_score:.2f}")
        print(f"   Motivo: {rec.match_reason}")
        print()
else:
    print("❌ NENHUMA RECOMENDAÇÃO GERADA!")
    print("O cold start NÃO funcionou.")
