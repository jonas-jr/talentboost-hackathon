# 🚀 Quick Start - LG TalentBoost

## Instalação Rápida

### 1. Instalar dependências

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

# Instalar dependências do módulo
pip install -r requirements.txt
```

### 2. Verificar estrutura de dados

Certifique-se de que os diretórios com dados estão presentes:

```
test_htn/
├── avaliacoes/           ← Avaliações de desempenho (JSON)
├── dados_cadastrais/     ← Dados cadastrais dos colaboradores (JSON)
├── treinamentos/         ← Histórico de treinamentos e cursos (JSON)
```

## Execução

### Opção 1: Demo Standalone (Recomendado para teste)

Execute o script de demonstração que mostra o pipeline completo:

```bash
python demo_talent_boost.py
```

**O que ele faz:**
1. Carrega dados de exemplo (Ana Paula Ferreira)
2. Analisa sentimentos nas observações
3. Detecta gaps de competências
4. Constrói perfil completo
5. Gera recomendações personalizadas
6. Exibe resultados formatados no terminal
7. Salva output em `demo_output.json`

**Output esperado:**
- Tabelas formatadas com análise de sentimentos
- Lista de gaps ordenados por severidade
- Perfil completo do colaborador
- Top 5 recomendações de treinamentos com justificativas

### Opção 2: MCP Server (Para integração com deep_agent)

Inicie o servidor MCP:

```bash
export TALENT_BOOST_DATA_DIR=/home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

python -m lg_ia_hub.app.modules.deep_agent.test_htn.mcp_server.talent_boost_server
```

O servidor ficará escutando em STDIO (protocolo MCP).

**Para testar via MCP client:**

```python
# Exemplo de uso via MCP client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=[
        "-m",
        "lg_ia_hub.app.modules.deep_agent.test_htn.mcp_server.talent_boost_server",
    ],
    env={"TALENT_BOOST_DATA_DIR": "/path/to/test_htn"},
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Listar tools disponíveis
        tools = await session.list_tools()
        print("Tools:", [t.name for t in tools.tools])

        # Chamar tool
        result = await session.call_tool(
            "recommend_training",
            arguments={"employee_name": "Ana Paula Ferreira", "top_n": 3}
        )
        print(result)
```

### Opção 3: Uso Programático

Use os componentes diretamente em código Python:

```python
from pathlib import Path
import json

from talent_boost_core.sentiment_analyzer import SentimentAnalyzer
from talent_boost_core.competency_gap_detector import CompetencyGapDetector
from talent_boost_core.profile_builder import EmployeeProfileBuilder
from talent_boost_core.recommendation_engine import TrainingRecommendationEngine

# 1. Carrega dados
with open("avaliacoes/avaliacao_ana_paula_ferreira.json") as f:
    avaliacao = json.load(f)

with open("dados_cadastrais/dadoscadastrais_ana_paula_ferreira.json") as f:
    cadastro = json.load(f)

with open("treinamentos/treinamentos_ana_paula_ferreira.json") as f:
    treinamentos = json.load(f)

# 2. Pipeline de análise
analyzer = SentimentAnalyzer()
gap_detector = CompetencyGapDetector(analyzer)
profile_builder = EmployeeProfileBuilder()

gaps = gap_detector.detect_gaps(avaliacao)
profile = profile_builder.build_profile(cadastro, avaliacao, treinamentos, gaps)

# 3. Recomendações
# Carrega todos os cursos disponíveis primeiro
all_courses = []  # carregar de todos os JSONs de treinamento

engine = TrainingRecommendationEngine(all_courses)
recommendations = engine.recommend(profile, top_n=5)

# 4. Resultado
for rec in recommendations:
    print(f"{rec.titulo} - {rec.match_reason}")
```

## Testes

Execute os testes unitários:

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=talent_boost_core --cov-report=term-missing

# Apenas um arquivo
pytest tests/test_sentiment_analyzer.py -v
```

## Dados de Exemplo

O projeto já inclui dados de 20+ colaboradores. Para testar com outro colaborador:

```bash
# Liste os colaboradores disponíveis
ls avaliacoes/

# Execute o demo modificando a variável employee_name:
# Em demo_talent_boost.py, linha ~173:
employee_name = "Bruno Henrique Costa"  # ou outro nome
```

## Troubleshooting

### Erro: "Avaliação não encontrada"

**Causa:** Nome do colaborador não corresponde ao arquivo JSON.

**Solução:** Verifique o nome exato no arquivo:
```bash
ls avaliacoes/ | grep -i "bruno"
# Resultado: avaliacao_bruno_henrique_costa.json
# Nome correto: "Bruno Henrique Costa"
```

### Erro: "ModuleNotFoundError: No module named 'talent_boost_core'"

**Causa:** Python não está encontrando o módulo.

**Solução:** Execute do diretório correto:
```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn
python demo_talent_boost.py
```

Ou adicione ao PYTHONPATH:
```bash
export PYTHONPATH=/home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn:$PYTHONPATH
```

### Erro: "No module named 'rich'"

**Causa:** Dependências não instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

## Estrutura de Output

### Demo Output (`demo_output.json`)

```json
{
  "employee_name": "Ana Paula Ferreira",
  "profile": {
    "cargo": "Desenvolvedora Backend",
    "nivel": "Junior",
    "nota_media_geral": 6.8,
    "pontos_fortes": ["Aprendizado"],
    "total_gaps": 2
  },
  "gaps": [
    {
      "competency": "Inovação com Foco no Cliente",
      "score": 5.3,
      "severity": "high",
      "urgency": "high"
    }
  ],
  "recommendations": [
    {
      "titulo": "Visão de Produto para Desenvolvedores",
      "categoria": "Gestao",
      "priority": "high",
      "relevance_score": 0.87,
      "match_reason": "Altamente recomendado..."
    }
  ]
}
```

## Próximos Passos

1. **Integração com Deep Agent**: adicionar subagente TalentBoost ao orchestrator
2. **Interface Web**: dashboard para visualização de recomendações
3. **Batch Processing**: processar múltiplos colaboradores em paralelo
4. **Fine-tuning**: ajustar pesos do sistema de recomendação com feedback real
5. **Produção**: deploy do MCP server com Redis para persistência

## Suporte

- **Documentação completa**: [README.md](./README.md)
- **Código fonte**: `talent_boost_core/`
- **Testes**: `tests/`
- **Issues**: Entre em contato com a equipe TalentBoost

---

**Versão**: 1.0.0 | **Data**: Janeiro 2026 | **LG TalentBoost Team**
