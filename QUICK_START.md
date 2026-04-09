# 🚀 TalentBoost - Quick Start

## Instalação Rápida

### 1. Instalar dependências

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn

# Opção 1: Script automático
bash install_deps.sh

# Opção 2: Manual
pip install -r requirements.txt
```

### 2. Verificar instalação

```bash
# Verifica se todas as dependências estão instaladas
python -c "import fastapi, uvicorn, structlog, langchain_openai; print('✅ Todas as dependências instaladas!')"
```

### 3. (Opcional) Configurar LLM Real

**Opção A: Usar .env do projeto principal** (recomendado)
- O sistema detectará automaticamente as variáveis do `.env` da raiz
- Nenhuma configuração adicional necessária

**Opção B: Configurar standalone** (sem o projeto principal)
```bash
# Copie o exemplo
cp .env.example .env

# Edite com suas credenciais Azure OpenAI
nano .env
```

**Opção C: Modo simulado** (sem LLM)
- Não configure nada
- O sistema funcionará com respostas simuladas

---

## Executar o Sistema

### Backend (API REST)

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
python api/main.py
```

**Logs esperados:**
```json
{
  "event": "course_assistant_initialized",
  "mode": "llm_powered"  // ou "simulated" se LLM não disponível
}
```

**API rodando em:** http://localhost:8001

### Frontend (React)

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn/frontend
npm install  # Primeira vez apenas
npm run dev
```

**Frontend rodando em:** http://localhost:5173

---

## Testar o Course Assistant

### Teste 1: Backend isolado

```bash
python test_course_assistant_llm.py
```

**Resultado:**
- ✅ Com LLM: Respostas contextualizadas do Azure OpenAI
- ⚠️ Sem LLM: Respostas simuladas (padrões básicos)

### Teste 2: Via API

```bash
curl -X POST http://localhost:8001/api/course-assistant/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "curso_id": "C001",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "progresso_curso": 0
  }'
```

### Teste 3: Via Frontend

1. Acesse http://localhost:5173/courses
2. Clique em "Falar com Tutor Virtual" em qualquer curso
3. Digite: "O que vou aprender neste curso?"
4. Receba resposta do tutor!

---

## Troubleshooting

### ❌ Erro: `ModuleNotFoundError: No module named 'structlog'`

**Solução:**
```bash
pip install structlog
```

### ❌ Erro: `ModuleNotFoundError: No module named 'langchain_openai'`

**Solução:**
```bash
pip install langchain-openai langchain-core
```

### ❌ Erro: `ValidationError: DEEP_AGENT_CLASSIFY_AZURE_OPENAI_DEPLOYMENT`

**Causa:** Falta variável do DeepAgent no `.env` do projeto principal

**Solução:** Sistema agora usa fallback automático:
1. Tenta DeepAgent (se disponível)
2. Usa Azure OpenAI direto (vars `AZURE_OPENAI_*`)
3. Fallback para modo simulado

```bash
# Reinicie o backend
python api/main.py
```

**Logs esperados:**
```
✅ LLM inicializada via Azure OpenAI direto (deployment: gpt-4o-mini)
```

### ⚠️ Course Assistant em "modo simulado"

**Causa:** Nenhuma LLM configurada

**Verificar logs de inicialização:**
```
⚠️  Nenhuma LLM disponível. Course Assistant rodará em modo simulado.
```

**Soluções:**

1. **Configure Azure OpenAI direto (mais simples):**
   ```bash
   export AZURE_OPENAI_ENDPOINT="https://seu-recurso.cognitiveservices.azure.com/"
   export AZURE_OPENAI_API_KEY="sua-chave"
   export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
   
   python api/main.py
   ```

2. **Ou use o .env local:**
   ```bash
   cp .env.example .env
   # Edite o .env com suas credenciais
   python api/main.py
   ```

3. **Ou não faça nada:**
   - O sistema funcionará em **modo simulado** (sem LLM)
   - Respostas serão baseadas em padrões (ainda úteis!)

### ❌ Erro 401 ao chamar Azure OpenAI

**Causa:** API Key inválida

**Solução:** Atualize `AZURE_OPENAI_API_KEY` no `.env`

---

## Modos de Operação

### 1. **Modo Completo** (LLM Real)
- Requer: Projeto DeepAgent + Azure OpenAI configurado
- Respostas: Geradas por IA, contextualizadas
- Performance: ~2-3s por resposta
- Custo: ~$0.002/pergunta

### 2. **Modo Simulado** (Padrões)
- Requer: Apenas FastAPI + dependências básicas
- Respostas: Baseadas em regex/keywords
- Performance: ~50ms por resposta
- Custo: $0 (grátis)

---

## Estrutura do Projeto

```
test_htn/
├── api/
│   └── main.py                    ← Backend FastAPI
├── talent_boost_core/
│   ├── course_assistant.py        ← Tutor Virtual
│   ├── recommendation_engine.py   ← Motor de recomendação
│   └── ...
├── frontend/
│   └── src/
│       └── components/
│           └── CourseAssistantChat.tsx  ← Chat UI
├── requirements.txt               ← Dependências Python
├── test_course_assistant_llm.py   ← Script de teste
└── QUICK_START.md                 ← Este arquivo
```

---

## Endpoints da API

### Course Assistant

```
POST   /api/course-assistant/start        # Inicia sessão
POST   /api/course-assistant/ask          # Envia pergunta
GET    /api/course-assistant/history/{id} # Histórico
POST   /api/course-assistant/suggestions  # Sugestões
```

### Recomendações

```
GET    /api/employees                     # Lista colaboradores
POST   /api/employees/{name}/recommendations  # Recomendações
GET    /api/employees/{name}/gaps         # Análise de gaps
```

### Analytics

```
POST   /api/feedback/track                # Registra feedback
GET    /api/analytics/summary             # Resumo geral
GET    /api/analytics/popular-courses     # Cursos populares
```

---

## Próximos Passos

1. ✅ Sistema funcionando? Teste com dados reais!
2. ✅ Configure Azure OpenAI para LLM real
3. ✅ Customize prompts em `course_assistant.py`
4. ✅ Adicione novos cursos em `treinamentos/`
5. ✅ Integre com banco de dados (PostgreSQL)

---

## Documentação Completa

- **README.md** - Visão geral do sistema
- **OPTIMIZATIONS.md** - Detalhes técnicos
- **COURSE_ASSISTANT.md** - Documentação do tutor
- **COURSE_ASSISTANT_LLM_SETUP.md** - Setup da LLM
- **DELIVERABLES.md** - Checklist de entregáveis

---

**Versão:** 2.0.0  
**Última atualização:** 2026-04-06
