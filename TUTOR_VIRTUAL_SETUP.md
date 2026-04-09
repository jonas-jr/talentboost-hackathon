# 🤖 Guia de Setup - Tutor Virtual TalentBoost

## 📋 Visão Geral

O Tutor Virtual é um assistente de IA que ajuda os alunos durante os cursos, respondendo dúvidas contextualizadas baseadas no perfil do colaborador e progresso no curso.

---

## 🏗️ Arquitetura

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Frontend      │  HTTP   │  Backend FastAPI │   LLM   │  Azure OpenAI   │
│   React + Vite  │ ──────> │  (Port 8001)     │ ──────> │  GPT-4o-mini    │
│   (Port 5173)   │ <────── │  + CourseAssist  │ <────── │  API            │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │
        │  Proxy /api               │  Dados JSON
        └────────────────────────────┴─────────────────┐
                                                        │
                                            ┌───────────▼──────────┐
                                            │  data/               │
                                            │  ├─ cursos/          │
                                            │  ├─ dados_cadastrais/│
                                            │  └─ treinamentos/    │
                                            └──────────────────────┘
```

---

## ✅ Pré-requisitos

### 1. Variáveis de Ambiente (`.env`)

Certifique-se que o `.env` na raiz do projeto contém:

```bash
# Azure OpenAI (JÁ CONFIGURADO NO SEU .env)
AZURE_OPENAI_API_KEY=8qmowfKs37CR9JNv0Lbj8mvKYuO5NBJ8p2uT350cuXXLgTp6MSIAJQQJ99BBACHYHv6XJ3w3AAAAACOGd4e6
AZURE_OPENAI_ENDPOINT=https://ai-services-ligiapro.cognitiveservices.azure.com
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-evaluation

# Ou usar o deployment alternativo
# AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### 2. Dependências Python

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências (se necessário)
pip install fastapi uvicorn langchain-openai structlog
```

### 3. Dependências Frontend

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn/frontend
npm install  # Já deve estar instalado
```

---

## 🚀 Como Iniciar

### **Passo 1: Iniciar o Backend**

Abra um terminal e execute:

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./start_backend.sh
```

**Você verá:**
```
🚀 Iniciando TalentBoost Backend...
✅ Ativando ambiente virtual...
📋 Configuração:
   Endpoint: https://ai-services-ligiapro.cognitiveservices.azure.com
   Deployment: gpt-4.1-evaluation
   API Version: 2024-12-01-preview
🌐 Iniciando servidor na porta 8001...
   URL: http://localhost:8001
   Docs: http://localhost:8001/docs
```

✅ **Verifique se funcionou:** Acesse http://localhost:8001/docs

---

### **Passo 2: Iniciar o Frontend**

Em **outro terminal**, execute:

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn/frontend
npm run dev
```

**Você verá:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Verifique se funcionou:** Acesse http://localhost:5173

---

### **Passo 3: Fazer Login**

1. Acesse: http://localhost:5173/login
2. Use qualquer usuário de teste:
   - Email: `ana.ferreira@empresa.com`
   - Senha: `123456`

---

### **Passo 4: Testar o Tutor Virtual**

1. Vá para **"Meus Cursos"**
2. Clique em **"Tutor Virtual"** em qualquer curso
3. O chat abrirá com uma mensagem de boas-vindas
4. **Pergunte algo**, por exemplo:
   - "O que vou aprender neste curso?"
   - "Como posso aplicar isso no meu trabalho?"
   - "Quais são os principais tópicos?"

---

## 🔍 Como Funciona

### **1. Fluxo de Mensagem**

```typescript
// Frontend envia pergunta
POST /api/course-assistant/ask
{
  "session_id": "session-123",
  "curso_id": "C001",
  "employee_id": 2001,
  "employee_name": "Ana Paula Ferreira",
  "question": "O que vou aprender?",
  "progresso_curso": 45,
  "modulo_atual": "Módulo 2"
}

// Backend processa com LLM
CourseAssistant.answer()
  → Contexto do curso (título, categoria, carga horária)
  → Contexto do aluno (cargo, nível, progresso)
  → Pergunta do usuário
  → LLM Azure OpenAI (gpt-4.1-evaluation)

// Resposta personalizada
{
  "response": {
    "content": "Neste curso você aprenderá...",
    "timestamp": "2026-04-08T..."
  }
}
```

### **2. Personalização por Contexto**

O tutor ajusta a resposta baseado em:

| Contexto | Fonte | Uso |
|----------|-------|-----|
| **Curso** | `ALL_COURSES` | Título, categoria, modalidade, carga horária |
| **Aluno** | `dados_cadastrais/{nome}.json` | Cargo, departamento, nível |
| **Progresso** | Frontend (prop) | Adapta explicações ao estágio atual |
| **Módulo Atual** | Frontend (prop) | Foco no conteúdo relevante |

### **3. Modos de Operação**

O `llm_helper.py` tenta 3 opções automaticamente:

1. ✅ **DeepAgent** (usa configuração completa do projeto)
2. ✅ **Azure OpenAI Direto** (usa vars `AZURE_OPENAI_*`)
3. ⚠️ **Modo Simulado** (respostas mock, sem LLM real)

---

## 🐛 Troubleshooting

### ❌ **Backend não inicia**

**Erro:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
source .venv/bin/activate
pip install fastapi uvicorn langchain-openai structlog
```

---

### ❌ **"LLM não disponível, modo simulado"**

**Causa:** Variáveis de ambiente não carregadas

**Solução:**
```bash
# Verifique se as vars existem
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Se vazias, carregue manualmente
export $(cat .env | grep -v '^#' | xargs)

# Reinicie o backend
./start_backend.sh
```

---

### ❌ **Frontend: "Erro ao enviar pergunta"**

**Causa:** Backend não está rodando ou porta diferente

**Solução:**
1. Verifique se o backend está rodando: `curl http://localhost:8001/docs`
2. Verifique o console do navegador (F12)
3. Verifique se o proxy está correto no `vite.config.ts`:
   ```typescript
   proxy: {
     '/api': {
       target: 'http://localhost:8001',
       changeOrigin: true,
     },
   }
   ```

---

### ❌ **CORS Error**

**Causa:** Backend não permite origem do frontend

**Solução:** Já configurado em `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Se usar outra porta, adicione-a aqui.

---

### ❌ **Resposta lenta**

**Causa:** LLM levando tempo para processar

**Solução:** Normal! O Azure OpenAI pode levar 2-5s por resposta. O frontend mostra loading (três pontinhos animados).

---

## 📊 Logs e Debug

### **Backend Logs**

O backend usa logs estruturados (JSON):

```bash
# Logs aparecem no terminal onde rodou ./start_backend.sh
{
  "event": "course_assistant_question",
  "session_id": "session-123",
  "curso_id": "C001",
  "question_length": 25,
  "timestamp": "2026-04-08T..."
}
```

### **Frontend Logs**

Abra o DevTools (F12) → Console:

```javascript
// Erros de API aparecem aqui
console.error('Erro ao enviar pergunta:', error)
```

---

## 🧪 Testando Manualmente

### **1. Testar Backend Diretamente**

```bash
# Start session
curl -X POST http://localhost:8001/api/course-assistant/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "curso_id": "C001",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "progresso_curso": 0,
    "modulo_atual": "Introdução"
  }'

# Ask question
curl -X POST http://localhost:8001/api/course-assistant/ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "curso_id": "C001",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "question": "O que vou aprender?",
    "progresso_curso": 0,
    "modulo_atual": "Introdução"
  }'
```

---

## 🎯 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/course-assistant/start` | Inicia sessão do tutor |
| POST | `/api/course-assistant/ask` | Faz pergunta ao tutor |
| POST | `/api/course-assistant/suggestions` | Sugere próximos passos |
| GET | `/api/course-assistant/history/{session_id}` | Histórico da sessão |

Documentação interativa: http://localhost:8001/docs

---

## 🔐 Segurança

- ✅ API Key do Azure OpenAI nunca exposta ao frontend
- ✅ CORS restrito a localhost:5173
- ✅ Session ID gerado no cliente (temporário)
- ⚠️ Em produção: adicionar autenticação nos endpoints

---

## 📝 Próximos Passos (Opcional)

- [ ] Persistir histórico de conversas no banco
- [ ] Adicionar autenticação JWT nos endpoints
- [ ] Rate limiting para prevenir abuso
- [ ] Cache de respostas comuns
- [ ] Feedback thumbs up/down nas respostas

---

## ✅ Checklist de Funcionamento

- [ ] Backend rodando em http://localhost:8001
- [ ] Frontend rodando em http://localhost:5173
- [ ] Login funcionando
- [ ] Modal do tutor abre ao clicar no botão
- [ ] Mensagem de boas-vindas aparece
- [ ] Perguntas são respondidas (não "modo simulado")
- [ ] Respostas são contextualizadas ao curso/aluno

---

**🎉 Tudo pronto! O Tutor Virtual está funcionando com IA real do Azure OpenAI!**

Se algo não funcionar, revise a seção de Troubleshooting ou verifique os logs do backend.
