# 🚀 Deploy no Vercel - Guia Completo

## 📋 Visão Geral

- **Frontend** → Vercel (gratuito)
- **Backend** → Render ou Railway (gratuito)

---

## Parte 1: Deploy do Frontend no Vercel

### Passo 1: Preparar projeto

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn/frontend

# Criar arquivo vercel.json (configuração)
cat > vercel.json <<EOF
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
EOF
```

### Passo 2: Deploy via CLI (Mais Rápido)

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login (abre navegador)
vercel login

# Deploy de produção
vercel --prod
```

**OU**

### Passo 2 (Alternativa): Deploy via Interface Web

1. Acesse: https://vercel.com/signup (criar conta grátis)
2. Clique em "Add New Project"
3. Importe o diretório `frontend/`
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Clique em "Deploy"

### Passo 3: Configurar Variável de Ambiente

Depois do deploy inicial:

1. Vá em "Settings" → "Environment Variables"
2. Adicione:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://seu-backend.onrender.com` (vamos criar no Passo 4)
   - **Environments**: Production, Preview, Development

3. Redeploy para aplicar

---

## Parte 2: Deploy do Backend no Render (Gratuito)

### Passo 1: Preparar arquivos

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

# Criar requirements.txt na raiz
cat > requirements.txt <<EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
EOF

# Criar arquivo de configuração do Render
cat > render.yaml <<EOF
services:
  - type: web
    name: talentboost-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python api/main.py"
    envVars:
      - key: PORT
        value: 8001
      - key: PYTHON_VERSION
        value: 3.12.0
EOF
```

### Passo 2: Deploy no Render

**Opção A: Via Interface Web**

1. Acesse: https://render.com (criar conta grátis)
2. Clique em "New" → "Web Service"
3. Conecte ao GitHub ou faça upload dos arquivos
4. Configure:
   - **Name**: `talentboost-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api/main.py`
   - **Instance Type**: Free

5. Clique em "Create Web Service"

**Opção B: Via CLI**

```bash
# Instalar Render CLI
npm install -g render-cli

# Deploy
render deploy
```

### Passo 3: Copiar URL do Backend

Após deploy, você terá algo como:
```
https://talentboost-api.onrender.com
```

### Passo 4: Atualizar CORS no Backend

Edite `api/main.py` para aceitar o domínio do Vercel:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-projeto.vercel.app",  # Vercel frontend
        "http://localhost:5173",           # Dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Faça commit e push para atualizar o Render.

---

## Parte 3: Conectar Frontend e Backend

### No Vercel (Frontend):

1. Vá em "Settings" → "Environment Variables"
2. Atualize `VITE_API_URL`:
   ```
   https://talentboost-api.onrender.com
   ```

3. Redeploy (ou será automático se conectado ao Git)

### Testar Conexão

```bash
# Testar backend
curl https://talentboost-api.onrender.com/

# Testar API
curl https://talentboost-api.onrender.com/api/employees
```

---

## 🎯 Resultado Final

Você terá 2 URLs públicas e permanentes:

- **Frontend**: `https://talentboost.vercel.app`
- **Backend**: `https://talentboost-api.onrender.com`
- **API Docs**: `https://talentboost-api.onrender.com/docs`

---

## 📊 Comparação: Render vs Railway

| Recurso | Render | Railway |
|---------|--------|---------|
| **Custo** | 🆓 100% Gratuito | 🆓 $5/mês depois free tier |
| **Build** | Pode ser lento | Muito rápido |
| **Domínio** | `.onrender.com` | `.railway.app` |
| **Sleep** | Dorme após inatividade | Sem sleep no paid plan |
| **Banco de Dados** | PostgreSQL grátis | PostgreSQL pago |
| **Logs** | 7 dias | 30 dias (paid) |

**Recomendação**: Use **Render** (100% grátis, sem cartão)

---

## 🔄 Deploy Automático (CI/CD)

### Com Git conectado:

1. **Vercel**: Auto-deploy a cada push no `main`
2. **Render**: Auto-deploy a cada push no `main`

### Branches:

- `main` → Produção
- Outras branches → Preview automático (apenas Vercel)

---

## 🐛 Troubleshooting

### Erro: "VITE_API_URL is not defined"

**Solução**: 
1. Adicione variável no Vercel
2. Redeploy
3. Limpe cache do navegador

### Erro: "CORS policy"

**Solução**: 
Adicione o domínio Vercel no `allow_origins` do backend:

```python
allow_origins=[
    "https://talentboost.vercel.app",  # ← Adicione aqui
    ...
]
```

### Backend dorme (Render Free)

**Solução**: 
- Normal no plano gratuito do Render
- Primeira requisição pode demorar ~30s (cold start)
- Considere usar cron job para manter ativo:
  ```bash
  # Cron-job.org (grátis) ping a cada 5 min
  curl https://talentboost-api.onrender.com/
  ```

---

## 💰 Custos

| Serviço | Plano | Custo |
|---------|-------|-------|
| **Vercel** | Hobby | 🆓 $0/mês |
| **Render** | Free | 🆓 $0/mês |
| **Total** | | **🆓 $0/mês** |

---

## 🚀 Deploy Rápido (Comandos)

### Frontend (Vercel):

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

### Backend (Render):

1. Acesse https://render.com
2. New Web Service
3. Configure conforme Passo 2 acima

---

## 📝 Checklist de Deploy

- [ ] Conta Vercel criada
- [ ] Conta Render criada
- [ ] `vercel.json` criado no frontend
- [ ] `requirements.txt` criado na raiz
- [ ] Frontend deployed no Vercel
- [ ] Backend deployed no Render
- [ ] `VITE_API_URL` configurado no Vercel
- [ ] CORS atualizado no backend
- [ ] Teste: Frontend acessível
- [ ] Teste: Backend respondendo
- [ ] Teste: Integração funcionando (frontend → backend)

---

## 🎉 URLs Exemplo

Após deploy completo:

```
Frontend:
https://talentboost-lg.vercel.app

Backend:
https://talentboost-api.onrender.com

API Docs:
https://talentboost-api.onrender.com/docs
```

Compartilhe essas URLs com os avaliadores!

---

**Tempo total**: ~10 minutos  
**Custo**: 🆓 $0/mês  
**Permanente**: ✅ Sim

---

**Desenvolvido para o Hackathon LG TalentBoost** | Janeiro 2026
