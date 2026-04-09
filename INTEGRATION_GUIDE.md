# Guia de Integração com Deep Agent

Este documento descreve como integrar o **TalentBoost MCP Server** com o módulo `deep_agent` do projeto.

## 📋 Pré-requisitos

- Deep Agent configurado e funcionando
- Servidor MCP TalentBoost implementado (✅ concluído)
- Dados de avaliações, cadastros e treinamentos disponíveis
- Python 3.12+

## 🏗️ Arquitetura de Integração

```
┌─────────────────────────────────────────┐
│      FastAPI / Flask (HTTP Layer)       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Deep Agent Orchestrator (LangGraph)   │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     Supervisor Agent               │ │
│  └────────────┬───────────────────────┘ │
│               │                          │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │   TalentBoost SubAgent             │ │
│  │   (delega para MCP tools)          │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   MCP Anti-Corruption Layer             │
│   (interceptors, tool_cache, etc.)      │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   TalentBoost MCP Server (STDIO)        │
│   • get_employee_evaluation             │
│   • analyze_competency_gaps             │
│   • recommend_training                  │
│   • ... (6 tools)                       │
└─────────────────────────────────────────┘
```

## 🔧 Passo 1: Configurar MCP Server em Settings

### 1.1 Adicionar variáveis de ambiente

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/core/config.py`

```python
class DeepAgentSettings(BaseSettings):
    # ... campos existentes ...

    # TalentBoost MCP Server
    TALENT_BOOST_MCP_ENABLED: bool = Field(
        default=False,
        validation_alias=AliasChoices("TALENT_BOOST_MCP_ENABLED"),
    )

    TALENT_BOOST_MCP_DATA_DIR: str = Field(
        default="",
        validation_alias=AliasChoices("TALENT_BOOST_MCP_DATA_DIR"),
    )
```

### 1.2 Atualizar `.env.example`

```bash
# TalentBoost MCP Server
TALENT_BOOST_MCP_ENABLED=true
TALENT_BOOST_MCP_DATA_DIR=/home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn
```

## 🛠️ Passo 2: Registrar Servidor MCP

### 2.1 Adicionar configuração de servidor

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/mcp/servers.py`

Adicionar ao dicionário de servidores MCP:

```python
from lg_ia_hub.app.modules.deep_agent.core.config import get_deep_agent_settings

def get_mcp_servers_config() -> dict:
    settings = get_deep_agent_settings()

    servers = {
        # ... servidores existentes ...
    }

    # TalentBoost (condicional)
    if settings.TALENT_BOOST_MCP_ENABLED:
        servers["talent-boost"] = {
            "command": "python",
            "args": [
                "-m",
                "lg_ia_hub.app.modules.deep_agent.test_htn.mcp_server.talent_boost_server",
            ],
            "env": {
                "TALENT_BOOST_DATA_DIR": settings.TALENT_BOOST_MCP_DATA_DIR,
            },
        }

    return servers
```

## 🎯 Passo 3: Criar Subagente TalentBoost

### 3.1 Implementar subagente

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/orchestration/subagents/talent_boost_agent.py`

```python
"""
Subagente para recomendação de treinamentos baseada em avaliações.

Delega para ferramentas MCP do TalentBoost Server.
"""

from typing import Annotated

from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langgraph.types import Command

from lg_ia_hub.app.modules.deep_agent.core.types import AgentState
from lg_ia_hub.app.modules.deep_agent.orchestration.subagents.base import CompiledSubAgent


class TalentBoostAgent(CompiledSubAgent):
    """
    Agente especializado em recomendação de treinamentos.

    Responsabilidades:
    - Analisar gaps de competências a partir de avaliações
    - Gerar recomendações personalizadas de treinamentos
    - Explicar justificativas das recomendações
    """

    async def run(self, state: AgentState) -> AgentState:
        """
        Processa solicitação de recomendação de treinamentos.

        Args:
            state: Estado com mensagens do usuário

        Returns:
            Estado atualizado com recomendações
        """
        messages = state["messages"]
        last_message = messages[-1] if messages else None

        if not last_message:
            return {
                **state,
                "messages": [
                    AIMessage(
                        content="Nenhuma solicitação recebida. Como posso ajudar com treinamentos?"
                    )
                ],
            }

        # Extrai nome do colaborador da mensagem
        employee_name = self._extract_employee_name(last_message.content)

        if not employee_name:
            return {
                **state,
                "messages": [
                    AIMessage(
                        content="Por favor, informe o nome do colaborador para o qual deseja recomendações de treinamento."
                    )
                ],
            }

        # Chama ferramentas MCP em sequência
        # 1. Busca avaliação
        # 2. Analisa gaps
        # 3. Gera recomendações

        try:
            # Análise de gaps (já inclui avaliação internamente)
            gaps_result = await self._call_tool(
                "analyze_competency_gaps",
                {"employee_name": employee_name}
            )

            # Recomendações
            recommendations_result = await self._call_tool(
                "recommend_training",
                {"employee_name": employee_name, "top_n": 5}
            )

            # Formata resposta
            response = self._format_recommendations_response(
                employee_name,
                gaps_result,
                recommendations_result,
            )

            return {
                **state,
                "messages": [AIMessage(content=response)],
            }

        except Exception as e:
            return {
                **state,
                "messages": [
                    AIMessage(
                        content=f"Erro ao processar recomendações para {employee_name}: {str(e)}"
                    )
                ],
            }

    def _extract_employee_name(self, content: str) -> str | None:
        """
        Extrai nome do colaborador da mensagem.

        Heurísticas simples — em produção, usar NER ou LLM.
        """
        # Padrão: "para [Nome]" ou "de [Nome]"
        import re
        patterns = [
            r"para\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*)",
            r"de\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*)",
            r"colaborador[a]?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return None

    async def _call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Chama ferramenta MCP (placeholder — integrar com MCP client real)."""
        # Em produção, usar mcp_client do projeto
        # Para demo, importa o servidor diretamente
        from lg_ia_hub.app.modules.deep_agent.test_htn.mcp_server.talent_boost_server import TalentBoostMCPServer
        import os

        data_dir = os.getenv("TALENT_BOOST_MCP_DATA_DIR", "/path/to/test_htn")
        server = TalentBoostMCPServer(data_directory=data_dir)

        # Simula chamada MCP
        if tool_name == "analyze_competency_gaps":
            return await server._analyze_competency_gaps(arguments)
        elif tool_name == "recommend_training":
            return await server._recommend_training(arguments)
        else:
            raise ValueError(f"Tool desconhecida: {tool_name}")

    def _format_recommendations_response(
        self,
        employee_name: str,
        gaps_result: dict,
        recommendations_result: dict,
    ) -> str:
        """Formata resposta com recomendações."""
        response_parts = [
            f"## Recomendações de Treinamento para {employee_name}\n",
        ]

        # Resumo do perfil
        if "profile_summary" in recommendations_result:
            profile = recommendations_result["profile_summary"]
            response_parts.append(
                f"**Cargo:** {profile.get('cargo', 'N/A')} ({profile.get('nivel', 'N/A')})\n"
                f"**Nota Média Geral:** {profile.get('nota_media_geral', 0):.1f}\n"
                f"**Gaps Identificados:** {profile.get('total_gaps', 0)}\n"
            )

        # Gaps principais
        if gaps_result.get("gaps"):
            response_parts.append("\n### 🎯 Principais Gaps de Competências\n")
            for gap in gaps_result["gaps"][:3]:  # Top 3
                response_parts.append(
                    f"- **{gap['competency_name']}** (nota {gap['average_score']}, "
                    f"severidade: {gap['gap_severity']}, urgência: {gap['urgency']})\n"
                )

        # Recomendações
        if recommendations_result.get("recommendations"):
            response_parts.append("\n### 🎓 Treinamentos Recomendados\n")
            for i, rec in enumerate(recommendations_result["recommendations"], 1):
                response_parts.append(
                    f"{i}. **{rec['titulo']}** ({rec['categoria']}, {rec['carga_horaria']}h)\n"
                    f"   - Prioridade: {rec['priority'].upper()}\n"
                    f"   - Relevância: {rec['relevance_score']:.0%}\n"
                    f"   - {rec['match_reason']}\n"
                )

        # Resumo
        if "summary" in recommendations_result:
            summary = recommendations_result["summary"]
            response_parts.append(
                f"\n**Total de recomendações:** {summary['total']}\n"
                f"**Relevância média:** {summary['average_relevance']:.0%}\n"
            )

        return "".join(response_parts)
```

### 3.2 Registrar subagente no factory

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/orchestration/subagents/__init__.py`

```python
from .talent_boost_agent import TalentBoostAgent

__all__ = [
    # ... outros subagentes ...
    "TalentBoostAgent",
]
```

## 📝 Passo 4: Atualizar Regras do Supervisor

### 4.1 Adicionar regras de roteamento

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/orchestration/prompts/supervisor_rules.json`

Adicionar nova regra:

```json
{
  "version": 3,
  "rules": [
    {
      "rule_id": "supervisor.talent_boost",
      "match": {
        "type": "keywords",
        "value": ["treinamento", "curso", "capacitação", "recomendação", "desenvolvimento", "avaliação de desempenho"]
      },
      "action": {
        "delegate_to": "talent_boost_agent",
        "reason": "Solicitação relacionada a recomendação de treinamentos baseada em avaliação de desempenho"
      },
      "priority": "high",
      "examples": [
        "Recomende treinamentos para Ana Paula Ferreira",
        "Quais cursos devo fazer para melhorar minha comunicação?",
        "Qual o plano de desenvolvimento baseado na minha última avaliação?"
      ]
    }
  ]
}
```

## 🧪 Passo 5: Testes de Integração

### 5.1 Teste unitário do subagente

**Arquivo:** `lg_ia_hub/app/modules/deep_agent/tests/test_talent_boost_agent.py`

```python
import pytest
from lg_ia_hub.app.modules.deep_agent.orchestration.subagents import TalentBoostAgent
from lg_ia_hub.app.modules.deep_agent.core.types import AgentState
from langchain_core.messages import HumanMessage


@pytest.mark.asyncio
async def test_talent_boost_agent_extracts_name():
    """Subagente deve extrair nome do colaborador da mensagem."""
    agent = TalentBoostAgent()

    state: AgentState = {
        "messages": [HumanMessage(content="Recomende treinamentos para Ana Paula Ferreira")],
        "thread_id": "test-001",
        "request_id": "req-001",
        "domain": "talent_boost",
        "max_steps": 10,
    }

    result = await agent.run(state)

    assert len(result["messages"]) > 0
    response = result["messages"][-1].content
    assert "Ana Paula Ferreira" in response or "recomendações" in response.lower()


@pytest.mark.asyncio
async def test_talent_boost_agent_handles_missing_name():
    """Subagente deve pedir nome se não for fornecido."""
    agent = TalentBoostAgent()

    state: AgentState = {
        "messages": [HumanMessage(content="Recomende treinamentos")],
        "thread_id": "test-002",
        "request_id": "req-002",
        "domain": "talent_boost",
        "max_steps": 10,
    }

    result = await agent.run(state)

    response = result["messages"][-1].content
    assert "nome" in response.lower() or "colaborador" in response.lower()
```

### 5.2 Teste end-to-end via HTTP

```bash
# Inicia o servidor
uvicorn lg_ia_hub.app.main:app --reload

# Testa endpoint
curl -X POST http://localhost:8000/deep-agent/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Recomende treinamentos para Ana Paula Ferreira",
    "thread_id": "test-123",
    "domain": "talent_boost"
  }'
```

## 🚀 Passo 6: Deploy

### 6.1 Variáveis de ambiente em produção

```bash
# .env (produção)
TALENT_BOOST_MCP_ENABLED=true
TALENT_BOOST_MCP_DATA_DIR=/app/data/talent_boost
```

### 6.2 Verificar permissões de dados

```bash
# Garantir que o servidor pode ler os arquivos JSON
chmod -R 644 /app/data/talent_boost/avaliacoes/*.json
chmod -R 644 /app/data/talent_boost/dados_cadastrais/*.json
chmod -R 644 /app/data/talent_boost/treinamentos/*.json
```

### 6.3 Monitoramento

Adicionar logs estruturados:

```python
from lg_ia_hub.app.modules.deep_agent.core.observability import get_logger

logger = get_logger(__name__)

# No subagente
logger.info("talent_boost_recommendation_generated", extra={
    "request_id": state["request_id"],
    "thread_id": state["thread_id"],
    "employee_name": employee_name,
    "total_recommendations": len(recommendations),
    "top_priority": recommendations[0]["priority"] if recommendations else None,
})
```

## ✅ Checklist de Integração

- [ ] Variáveis de ambiente adicionadas em `config.py`
- [ ] Servidor MCP registrado em `servers.py`
- [ ] Subagente `TalentBoostAgent` implementado
- [ ] Regras do supervisor atualizadas
- [ ] Testes unitários do subagente criados
- [ ] Teste end-to-end via HTTP executado com sucesso
- [ ] Logs estruturados adicionados
- [ ] Deploy em staging realizado
- [ ] Validação com dados reais
- [ ] Documentação de uso atualizada

## 🐛 Troubleshooting

### Erro: "MCP server talent-boost not found"

**Causa:** Servidor não registrado ou env var desabilitada.

**Solução:**
```bash
export TALENT_BOOST_MCP_ENABLED=true
export TALENT_BOOST_MCP_DATA_DIR=/path/to/test_htn
```

### Erro: "Tool 'recommend_training' não disponível"

**Causa:** Servidor MCP não iniciou corretamente.

**Solução:** Verificar logs do servidor MCP:
```bash
python -m lg_ia_hub.app.modules.deep_agent.test_htn.mcp_server.talent_boost_server
# Deve exibir: "Starting TalentBoost MCP Server..."
```

### Erro: "Avaliação não encontrada para [Nome]"

**Causa:** Nome não corresponde ao arquivo JSON ou arquivo ausente.

**Solução:**
1. Verificar nome exato do arquivo:
   ```bash
   ls /path/to/test_htn/avaliacoes/
   ```
2. Garantir normalização correta (snake_case, lowercase, sem acentos)

## 📚 Referências

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [LangGraph Subagents](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Deep Agent Architecture](/lg-ia-hub-produto/.claude/rules/architecture.md)
- [TalentBoost README](./README.md)

---

**Versão**: 1.0 | **Data**: Janeiro 2026 | **LG TalentBoost Team**
