# 🚀 START HERE - TalentBoost Quick Start

## ⚡ Início Rápido (3 comandos)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Verificar setup
python check_setup.py

# 3. Iniciar backend
python api/main.py
```

**Frontend** (terminal separado):
```bash
cd frontend
npm install  # Primeira vez apenas
npm run dev
```

**Acesse:** http://localhost:5173

---

## 🔧 Solução do Erro ValidationError

### ❌ Problema:
```
ValidationError: DEEP_AGENT_CLASSIFY_AZURE_OPENAI_DEPLOYMENT
Input should be a valid string
```

### ✅ Solução:
O sistema agora tem **fallback automático em 3 níveis:**

```
1. DeepAgent (config completa) 
   ↓ (se falhar)
2. Azure OpenAI direto (vars AZURE_OPENAI_*)
   ↓ (se falhar)  
3. Modo simulado (sem LLM)
```

**Você não precisa fazer nada!** O sistema escolherá o melhor modo automaticamente.

---

## 🎯 Modos de Operação

### Modo 1: LLM via DeepAgent (Melhor)
✅ **Automático** - Se você tem o projeto lg-ia-hub configurado  
✅ Usa todas as configs avançadas do projeto  
✅ Melhor performance e features

**Logs esperados:**
```
✅ LLM inicializada via DeepAgent (configuração completa do projeto)
```

### Modo 2: LLM via Azure OpenAI Direto
✅ **Configuração mínima** - Apenas 3 variáveis de ambiente  
✅ Funciona standalone (sem o projeto principal)

**Configure:**
```bash
export AZURE_OPENAI_ENDPOINT="https://seu-recurso.cognitiveservices.azure.com/"
export AZURE_OPENAI_API_KEY="sua-chave"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"

python api/main.py
```

**Logs esperados:**
```
✅ LLM inicializada via Azure OpenAI direto (deployment: gpt-4o-mini)
```

### Modo 3: Simulado (Sem LLM)
✅ **Zero configuração** - Funciona out-of-the-box  
✅ Respostas baseadas em padrões e keywords  
✅ Útil para desenvolvimento e demonstração

**Logs esperados:**
```
⚠️  Nenhuma LLM disponível. Course Assistant rodará em modo simulado.
```

---

## 📋 Checklist de Inicialização

Execute este checklist antes de rodar:

```bash
# 1. Verificar setup completo
python check_setup.py

# Deve mostrar:
# 🎉 TUDO OK! Sistema pronto para rodar.
```

Se der erro, veja a seção [Troubleshooting](#troubleshooting) abaixo.

---

## 🧪 Testando o Sistema

### Teste 1: Backend
```bash
python api/main.py
```

**Sucesso:** `INFO:     Started server process`

### Teste 2: Frontend
```bash
cd frontend
npm run dev
```

**Sucesso:** `Local: http://localhost:5173/`

### Teste 3: Course Assistant
1. Acesse http://localhost:5173/courses
2. Clique em "Falar com Tutor Virtual"
3. Digite: "O que vou aprender neste curso?"
4. Receba resposta do tutor! 🎓

---

## 🔍 Troubleshooting

### ❌ ModuleNotFoundError: structlog
```bash
pip install structlog
```

### ❌ ModuleNotFoundError: langchain_openai
```bash
pip install langchain-openai langchain-core
```

### ❌ Frontend não conecta no backend
**Causa:** Backend não está rodando

**Solução:**
```bash
# Terminal 1: Backend
python api/main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### ⚠️ Course Assistant em modo simulado
**Isso é OK!** O sistema funcionará normalmente.

**Para usar LLM real:**
```bash
export AZURE_OPENAI_ENDPOINT="..."
export AZURE_OPENAI_API_KEY="..."
python api/main.py
```

---

## 📚 Documentação Completa

- **[QUICK_START.md](QUICK_START.md)** - Guia detalhado com troubleshooting
- **[README.md](README.md)** - Visão geral do sistema
- **[COURSE_ASSISTANT.md](COURSE_ASSISTANT.md)** - Documentação do tutor virtual
- **[COURSE_ASSISTANT_LLM_SETUP.md](COURSE_ASSISTANT_LLM_SETUP.md)** - Setup avançado da LLM

---

## 🎯 Funcionalidades Principais

### ✅ Recomendação de Treinamentos
- Content-based filtering
- Collaborative filtering
- Cold start inteligente
- Diversity & Serendipity
- Temporal decay

### ✅ Course Assistant (Tutor Virtual) 🆕
- Chat em tempo real durante o curso
- Respostas contextualizadas ao cargo/nível
- Classificação de perguntas
- Sugestões de próximos passos
- **3 modos:** DeepAgent / Azure direto / Simulado

### ✅ Analytics Dashboard
- CTR (Click-Through Rate)
- Taxa de matrícula
- Cursos populares
- Insights de performance

### ✅ Frontend Moderno
- Comparação de cursos
- Learning path visual
- Chat do tutor integrado
- Dashboard interativo

---

## ⚙️ Variáveis de Ambiente (Opcional)

O sistema funciona **sem configuração**, mas para LLM real:

```bash
# Mínimo para Azure OpenAI direto
AZURE_OPENAI_ENDPOINT=https://seu-recurso.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=sua-chave
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini  # ou gpt-5-mini
AZURE_OPENAI_API_VERSION=2024-10-01-preview
```

**Ou use o .env do projeto principal** (detecta automaticamente).

---

## 🆘 Precisa de Ajuda?

1. Execute `python check_setup.py` e veja o diagnóstico
2. Leia os logs de erro (são muito claros!)
3. Veja [QUICK_START.md](QUICK_START.md) para troubleshooting detalhado

---

**Status:** ✅ Sistema funcional em 3 modos (DeepAgent / Azure / Simulado)  
**Versão:** 2.0.0  
**Última atualização:** 2026-04-06
