# 🚀 Guia de Execução Fullstack - TalentBoost

Este guia mostra como executar o sistema completo (backend + frontend).

---

## 📋 Pré-requisitos

- **Python 3.12+** instalado
- **Node.js 18+** instalado
- **npm** ou **yarn**

---

## 🔧 Parte 1: Backend API (FastAPI)

### 1.1 Instalar dependências Python

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

# Dependências do core já instaladas anteriormente
pip install fastapi uvicorn pydantic
```

### 1.2 Iniciar servidor backend

```bash
# Terminal 1 - Backend
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

python api/main.py
```

**Output esperado:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Testar API:**
```bash
curl http://localhost:8001/
# Resposta: {"status":"ok","service":"TalentBoost API","version":"1.0.0"}

curl http://localhost:8001/api/employees
# Resposta: [{"name":"Ana Paula Ferreira","cargo":"..."}]
```

---

## 🎨 Parte 2: Frontend (React + Vite)

### 2.1 Instalar dependências Node

```bash
# Terminal 2 - Frontend
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn/frontend

npm install
```

### 2.2 Iniciar servidor de desenvolvimento

```bash
npm run dev
```

**Output esperado:**
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 2.3 Acessar aplicação

Abra no navegador: **http://localhost:5173**

---

## 🎯 Funcionalidades Disponíveis

### 1. Dashboard
- **URL**: http://localhost:5173/
- **Conteúdo**:
  - Total de colaboradores
  - Total de cursos
  - Categorias de cursos
  - Gráficos interativos

### 2. Lista de Colaboradores
- **URL**: http://localhost:5173/employees
- **Conteúdo**:
  - Grid de todos os colaboradores
  - Busca por nome, cargo ou departamento
  - Cards clicáveis

### 3. Detalhes do Colaborador
- **URL**: http://localhost:5173/employees/Ana%20Paula%20Ferreira
- **Conteúdo**:
  - Perfil completo (cargo, nível, nota média)
  - Pontos fortes
  - **Tab Gaps**: gráfico + lista detalhada de gaps
  - **Tab Recomendações**: top 5 cursos personalizados

---

## 📸 Preview das Telas

### Dashboard
```
┌─────────────────────────────────────────────────────┐
│ LG TalentBoost                                      │
│ Dashboard | Colaboradores | Cursos                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [21]           [50+]          [6]                  │
│  Colaboradores  Cursos         Categorias           │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Cursos por   │  │ Distribuição │                │
│  │ Categoria    │  │ (Pizza)      │                │
│  │ (Barras)     │  │              │                │
│  └──────────────┘  └──────────────┘                │
└─────────────────────────────────────────────────────┘
```

### Lista de Colaboradores
```
┌─────────────────────────────────────────────────────┐
│ 🔍 Buscar colaborador...                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ 👤 Ana     │  │ 👤 Bruno   │  │ 👤 Carla   │   │
│  │ Paula      │  │ Henrique   │  │ Menezes    │   │
│  │ Backend    │  │ Frontend   │  │ QA Analyst │   │
│  │ Tecnologia │  │ Tecnologia │  │ Qualidade  │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Detalhes do Colaborador
```
┌─────────────────────────────────────────────────────┐
│ ← Ana Paula Ferreira                                │
│   Desenvolvedora Backend · Junior                   │
├─────────────────────────────────────────────────────┤
│  Nota: 6.8  |  Gaps: 2  |  Fortes: 1  |  Recs: 5   │
│                                                     │
│  ✅ Pontos Fortes: [Aprendizado]                    │
│                                                     │
│  [Gaps de Competências] [Recomendações]  ← Tabs    │
│                                                     │
│  🟠 Inovação com Foco no Cliente  (5.3) HIGH       │
│  "Foca no técnico, pode ampliar visão..."          │
│  • Urgência: HIGH | Consenso: 90%                  │
│                                                     │
│  🟡 Comunicação Direta e Objetiva (6.0) MEDIUM     │
│  "Pode melhorar objetividade em updates..."        │
│  • Urgência: MEDIUM | Consenso: 80%                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Testando o Fluxo Completo

### Passo 1: Verificar backend está rodando

```bash
curl http://localhost:8001/api/stats/overview
```

Deve retornar JSON com estatísticas.

### Passo 2: Acessar dashboard

1. Abra http://localhost:5173/
2. Verifique se os cards mostram números corretos
3. Verifique se os gráficos estão carregando

### Passo 3: Buscar colaborador

1. Clique em "Colaboradores" no menu
2. Digite "Ana" na busca
3. Clique no card de "Ana Paula Ferreira"

### Passo 4: Ver recomendações

1. Na página de detalhes, veja os cards de resumo
2. Clique na tab "Recomendações de Treinamento"
3. Verifique os 5 cursos recomendados
4. Note a relevância e prioridade de cada um

---

## 🐛 Troubleshooting

### Erro: "Network Error" no frontend

**Causa**: Backend não está rodando ou porta incorreta.

**Solução**:
```bash
# Verifique se backend está rodando
curl http://localhost:8001/

# Se não, inicie:
python api/main.py
```

### Erro: "EADDRINUSE: address already in use"

**Causa**: Porta 5173 já está em uso.

**Solução**:
```bash
# Matar processo na porta 5173
npx kill-port 5173

# Ou usar porta diferente
npm run dev -- --port 3000
```

### Erro: "Module not found" no frontend

**Causa**: Dependências não instaladas.

**Solução**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Error

**Causa**: Backend não está aceitando requests do frontend.

**Solução**: Verificar em `api/main.py` se o CORS está configurado:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

---

## 📊 Endpoints da API

| Endpoint | Método | Descrição | Exemplo |
|----------|--------|-----------|---------|
| `/api/employees` | GET | Lista todos os colaboradores | `curl http://localhost:8001/api/employees` |
| `/api/employees/{name}/gaps` | GET | Analisa gaps | `curl http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/gaps` |
| `/api/employees/{name}/recommendations` | POST | Gera recomendações | Ver curl abaixo |
| `/api/stats/overview` | GET | Estatísticas gerais | `curl http://localhost:8001/api/stats/overview` |

**Exemplo POST recommendations:**
```bash
curl -X POST http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "employee_name": "Ana Paula Ferreira",
    "top_n": 5,
    "exclude_completed": true
  }'
```

---

## 🚀 Deploy em Produção

### Backend (FastAPI)

```bash
# Usar Gunicorn + Uvicorn workers
pip install gunicorn

gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001
```

### Frontend (React)

```bash
# Build estático
cd frontend
npm run build

# Servir com nginx, Apache, ou qualquer servidor estático
# Os arquivos estarão em frontend/dist/
```

---

## 📝 Variáveis de Ambiente

### Backend

Nenhuma variável obrigatória — usa dados locais em JSON.

### Frontend

Criar `.env` se necessário:
```env
VITE_API_URL=http://localhost:8001
```

---

## ✅ Checklist de Execução

- [ ] Python 3.12+ instalado
- [ ] Node.js 18+ instalado
- [ ] Dependências Python instaladas (`pip install fastapi uvicorn`)
- [ ] Backend rodando na porta 8001
- [ ] Dependências Node instaladas (`npm install`)
- [ ] Frontend rodando na porta 5173
- [ ] Navegador aberto em http://localhost:5173
- [ ] Dashboard carregando dados corretamente
- [ ] Lista de colaboradores mostrando todos os 21
- [ ] Detalhes de colaborador com gaps e recomendações

---

**Sistema pronto para uso!** 🎉

Para mais informações, consulte:
- [README.md](README.md) — Documentação técnica completa
- [frontend/README.md](frontend/README.md) — Documentação do frontend
- [QUICKSTART.md](QUICKSTART.md) — Guia de início rápido do backend

---

**Desenvolvido para o Hackathon LG TalentBoost** | Janeiro 2026
