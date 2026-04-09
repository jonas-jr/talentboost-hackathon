"""
Servidor MCP para TalentBoost.

Expõe ferramentas de análise de desempenho e recomendação de treinamentos
via protocolo MCP para integração com o deep_agent.
"""

import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import dos componentes core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from talent_boost_core.sentiment_analyzer import SentimentAnalyzer
from talent_boost_core.competency_gap_detector import CompetencyGapDetector
from talent_boost_core.profile_builder import EmployeeProfileBuilder
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine


logger = logging.getLogger(__name__)


class TalentBoostMCPServer:
    """Servidor MCP para TalentBoost."""

    def __init__(self, data_directory: str):
        """
        Inicializa o servidor.

        Args:
            data_directory: Caminho para o diretório com os dados JSON
        """
        self.data_dir = Path(data_directory)
        self.server = Server("talent-boost-server")

        # Inicializa componentes core
        self.sentiment_analyzer = SentimentAnalyzer()
        self.gap_detector = CompetencyGapDetector(self.sentiment_analyzer)
        self.profile_builder = EmployeeProfileBuilder()

        # Carrega dados estáticos na inicialização
        self._load_static_data()

        # Registra handlers
        self._register_handlers()

    def _load_static_data(self):
        """Carrega dados estáticos (lista de cursos)."""
        try:
            # Carrega todos os cursos disponíveis
            all_courses = []

            # Itera sobre todos os arquivos de treinamento
            treinamentos_dir = self.data_dir / "treinamentos"
            if treinamentos_dir.exists():
                for file in treinamentos_dir.glob("treinamentos_*.json"):
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        courses = data.get("cursos", [])
                        # Deduplica cursos por ID
                        for course in courses:
                            if not any(c.get("cursoID") == course.get("cursoID") for c in all_courses):
                                all_courses.append(course)

            self.all_courses = all_courses
            self.recommendation_engine = TrainingRecommendationEngine(all_courses)
            logger.info(f"Loaded {len(all_courses)} unique courses")

        except Exception as e:
            logger.error(f"Error loading static data: {e}")
            self.all_courses = []
            self.recommendation_engine = TrainingRecommendationEngine([])

    def _register_handlers(self):
        """Registra handlers das tools MCP."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Lista todas as ferramentas disponíveis."""
            return [
                Tool(
                    name="get_employee_evaluation",
                    description=(
                        "Busca a avaliação de desempenho de um colaborador. "
                        "Retorna dados completos da avaliação incluindo notas, "
                        "observações e critérios de todas as competências."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_name": {
                                "type": "string",
                                "description": "Nome completo do colaborador",
                            },
                        },
                        "required": ["employee_name"],
                    },
                ),
                Tool(
                    name="get_employee_profile",
                    description=(
                        "Busca dados cadastrais de um colaborador. "
                        "Retorna informações como cargo, departamento, tempo de casa, etc."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_name": {
                                "type": "string",
                                "description": "Nome completo do colaborador",
                            },
                        },
                        "required": ["employee_name"],
                    },
                ),
                Tool(
                    name="analyze_competency_gaps",
                    description=(
                        "Analisa gaps de competências a partir de uma avaliação de desempenho. "
                        "Usa análise de sentimentos nas observações e identifica áreas prioritárias "
                        "de desenvolvimento. Retorna lista ordenada por severidade e urgência."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_name": {
                                "type": "string",
                                "description": "Nome completo do colaborador",
                            },
                        },
                        "required": ["employee_name"],
                    },
                ),
                Tool(
                    name="recommend_training",
                    description=(
                        "Gera recomendações personalizadas de treinamentos baseadas nos gaps "
                        "de competências identificados. Usa sistema híbrido (content-based + "
                        "context-aware) e prioriza por urgência. Retorna top N cursos mais relevantes."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_name": {
                                "type": "string",
                                "description": "Nome completo do colaborador",
                            },
                            "top_n": {
                                "type": "integer",
                                "description": "Número de recomendações a retornar (padrão: 5)",
                                "default": 5,
                            },
                            "exclude_completed": {
                                "type": "boolean",
                                "description": "Se true, exclui cursos já concluídos (padrão: true)",
                                "default": True,
                            },
                        },
                        "required": ["employee_name"],
                    },
                ),
                Tool(
                    name="get_available_courses",
                    description=(
                        "Lista todos os cursos disponíveis no LMS, opcionalmente filtrados por categoria. "
                        "Retorna informações completas de cada curso (título, categoria, modalidade, "
                        "carga horária, obrigatoriedade)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Categoria para filtrar (opcional)",
                            },
                        },
                    },
                ),
                Tool(
                    name="get_employee_training_history",
                    description=(
                        "Busca histórico completo de treinamentos de um colaborador. "
                        "Retorna cursos concluídos, em andamento, notas, e estatísticas."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_name": {
                                "type": "string",
                                "description": "Nome completo do colaborador",
                            },
                        },
                        "required": ["employee_name"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Executa uma ferramenta."""
            try:
                if name == "get_employee_evaluation":
                    result = await self._get_employee_evaluation(arguments)
                elif name == "get_employee_profile":
                    result = await self._get_employee_profile(arguments)
                elif name == "analyze_competency_gaps":
                    result = await self._analyze_competency_gaps(arguments)
                elif name == "recommend_training":
                    result = await self._recommend_training(arguments)
                elif name == "get_available_courses":
                    result = await self._get_available_courses(arguments)
                elif name == "get_employee_training_history":
                    result = await self._get_employee_training_history(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    async def _get_employee_evaluation(self, args: dict) -> dict:
        """Busca avaliação de um colaborador."""
        employee_name = args.get("employee_name")
        if not employee_name:
            return {"error": "employee_name é obrigatório"}

        file_path = self._find_file("avaliacoes", f"avaliacao_{self._normalize_name(employee_name)}.json")

        if not file_path:
            return {"error": f"Avaliação não encontrada para {employee_name}"}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def _get_employee_profile(self, args: dict) -> dict:
        """Busca dados cadastrais de um colaborador."""
        employee_name = args.get("employee_name")
        if not employee_name:
            return {"error": "employee_name é obrigatório"}

        file_path = self._find_file("dados_cadastrais", f"dadoscadastrais_{self._normalize_name(employee_name)}.json")

        if not file_path:
            return {"error": f"Dados cadastrais não encontrados para {employee_name}"}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def _analyze_competency_gaps(self, args: dict) -> dict:
        """Analisa gaps de competências."""
        employee_name = args.get("employee_name")
        if not employee_name:
            return {"error": "employee_name é obrigatório"}

        # Carrega avaliação
        eval_data = await self._get_employee_evaluation({"employee_name": employee_name})
        if "error" in eval_data:
            return eval_data

        # Detecta gaps
        gaps = self.gap_detector.detect_gaps(eval_data)

        # Serializa gaps para JSON
        gaps_json = [
            {
                "competency_name": g.competency_name,
                "competency_key": g.competency_key,
                "average_score": g.average_score,
                "gap_severity": g.gap_severity,
                "urgency": g.urgency.value,
                "context": g.context,
                "evaluator_consensus": g.evaluator_consensus,
                "development_hints": g.development_hints,
                "key_observations": g.key_observations,
            }
            for g in gaps
        ]

        return {
            "employee_name": employee_name,
            "total_gaps": len(gaps),
            "gaps": gaps_json,
        }

    async def _recommend_training(self, args: dict) -> dict:
        """Gera recomendações de treinamento."""
        employee_name = args.get("employee_name")
        if not employee_name:
            return {"error": "employee_name é obrigatório"}

        top_n = args.get("top_n", 5)
        exclude_completed = args.get("exclude_completed", True)

        # Carrega dados necessários
        eval_data = await self._get_employee_evaluation({"employee_name": employee_name})
        if "error" in eval_data:
            return eval_data

        profile_data = await self._get_employee_profile({"employee_name": employee_name})
        if "error" in profile_data:
            return profile_data

        training_data = await self._get_employee_training_history({"employee_name": employee_name})
        if "error" in training_data:
            # Se não tiver histórico, usa dados vazios
            training_data = {"colaboradores": [], "cursos": [], "matriculas": [], "resultados": []}

        # Detecta gaps
        gaps = self.gap_detector.detect_gaps(eval_data)

        # Constrói perfil completo
        profile = self.profile_builder.build_profile(
            employee_data=profile_data,
            evaluation_data=eval_data,
            training_data=training_data,
            gaps=gaps,
        )

        # Gera recomendações
        recommendations = self.recommendation_engine.recommend(
            profile=profile,
            top_n=top_n,
            exclude_completed=exclude_completed,
        )

        # Serializa recomendações
        recs_json = [
            {
                "curso_id": r.curso_id,
                "titulo": r.titulo,
                "categoria": r.categoria,
                "modalidade": r.modalidade,
                "carga_horaria": r.carga_horaria,
                "obrigatorio": r.obrigatorio,
                "relevance_score": r.relevance_score,
                "match_reason": r.match_reason,
                "addresses_gaps": r.addresses_gaps,
                "priority": r.priority,
            }
            for r in recommendations
        ]

        # Gera resumo
        summary = self.recommendation_engine.get_recommendation_summary(recommendations)

        return {
            "employee_name": employee_name,
            "profile_summary": {
                "cargo": profile.cargo,
                "nivel": profile.nivel,
                "nota_media_geral": profile.nota_media_geral,
                "total_gaps": len(profile.gaps_identificados),
            },
            "recommendations": recs_json,
            "summary": summary,
        }

    async def _get_available_courses(self, args: dict) -> dict:
        """Lista cursos disponíveis."""
        category = args.get("category")

        courses = self.all_courses

        if category:
            courses = [c for c in courses if c.get("categoria") == category]

        return {
            "total": len(courses),
            "category_filter": category,
            "courses": courses,
        }

    async def _get_employee_training_history(self, args: dict) -> dict:
        """Busca histórico de treinamentos."""
        employee_name = args.get("employee_name")
        if not employee_name:
            return {"error": "employee_name é obrigatório"}

        file_path = self._find_file("treinamentos", f"treinamentos_{self._normalize_name(employee_name)}.json")

        if not file_path:
            return {"error": f"Histórico de treinamentos não encontrado para {employee_name}"}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _find_file(self, subdir: str, filename: str) -> Path | None:
        """Busca um arquivo no diretório de dados."""
        file_path = self.data_dir / subdir / filename
        if file_path.exists():
            return file_path
        return None

    def _normalize_name(self, name: str) -> str:
        """Normaliza nome para match com arquivo (snake_case, lowercase, sem acentos)."""
        import unicodedata
        # Remove acentos
        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ascii', 'ignore').decode('ascii')
        # Converte para snake_case
        name = name.lower().replace(" ", "_")
        return name

    async def run(self):
        """Inicia o servidor MCP."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """Entry point do servidor."""
    import os

    # Pega diretório de dados da env var ou usa padrão
    data_dir = os.getenv(
        "TALENT_BOOST_DATA_DIR",
        str(Path(__file__).parent.parent),
    )

    logger.info(f"Starting TalentBoost MCP Server with data dir: {data_dir}")

    server = TalentBoostMCPServer(data_directory=data_dir)
    await server.run()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
