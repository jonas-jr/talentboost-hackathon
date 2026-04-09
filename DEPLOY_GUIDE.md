# 🚀 Guia de Deploy - TalentBoost

Este guia mostra como fazer deploy do TalentBoost em diferentes plataformas para torná-lo acessível publicamente.

---

## Opção 1: Deploy Rápido com Ngrok ⚡ (Recomendado para Demo)

### Passo 1: Configurar Ngrok

```bash
# 1. Instalar ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# 2. Criar conta gratuita em https://dashboard.ngrok.com/signup

# 3. Configurar authtoken (pegar em https://dashboard.ngrok.com/get-started/your-authtoken)
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### Passo 2: Executar Deploy

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

./deploy_ngrok.sh
```

**O script faz automaticamente:**
1. ✅ Build do frontend para produção
2. ✅ Inicia backend na porta 8001
3. ✅ Serve frontend (build estático)
4. ✅ Expõe backend via ngrok (URL pública HTTPS)
5. ✅ Expõe frontend via ngrok (URL pública HTTPS)
6. ✅ Configura CORS automaticamente
7. ✅ Salva URLs em `PUBLIC_URLS.txt`

**Saída esperada:**
```
════════════════════════════════════════════════════
  ✅ TalentBoost está PÚBLICO e ACESSÍVEL! 🎉
════════════════════════════════════════════════════

📱 Aplicação Web (Frontend):
   https://abc123.ngrok.io

🔌 API Backend:
   https://def456.ngrok.io

📖 Documentação da API:
   https://def456.ngrok.io/docs
```

**Vantagens:**
- ⚡ Setup em < 2 minutos
- 🆓 Gratuito
- 🔒 HTTPS automático
- 🌐 Acessível de qualquer lugar

**Desvantagens:**
- ⏰ URLs temporárias (expiram ao fechar o script)
- 🔄 URLs mudam a cada execução

---

## Opção 2: Deploy em Railway (Permanente) 🚂

### Backend (API FastAPI)

1. **Criar conta no Railway**: https://railway.app

2. **Criar arquivo `railway.json`:**

```bash
cat > railway.json <<EOF
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python api/main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
```

3. **Criar `requirements.txt` na raiz:**

```bash
cat > requirements.txt <<EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
EOF
```

4. **Deploy via Railway CLI:**

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar projeto
railway init

# Deploy
railway up
```

**URL gerada:** `https://seu-projeto.up.railway.app`

### Frontend (React)

1. **Deploy no Vercel** (gratuito):

```bash
cd frontend

# Instalar Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

2. **Configurar variável de ambiente no Vercel:**

```
VITE_API_URL=https://seu-projeto.up.railway.app
```

**URL gerada:** `https://talentboost.vercel.app`

---

## Opção 3: Deploy em Render (Gratuito) 🎨

### Backend

1. **Criar conta no Render**: https://render.com

2. **Novo Web Service** → Conectar repositório Git

3. **Configurações:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api/main.py`
   - Environment: Python 3

4. **Deploy automático** a cada push no Git

**URL gerada:** `https://talentboost-api.onrender.com`

### Frontend

1. **Novo Static Site** no Render

2. **Configurações:**
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Environment Variable: `VITE_API_URL=https://talentboost-api.onrender.com`

**URL gerada:** `https://talentboost.onrender.com`

---

## Opção 4: Docker + Servidor VPS 🐳

### Passo 1: Criar Dockerfiles

**Backend Dockerfile:**

```bash
cat > Dockerfile.backend <<EOF
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "api/main.py"]
EOF
```

**Frontend Dockerfile:**

```bash
cat > frontend/Dockerfile <<EOF
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
```

### Passo 2: Docker Compose

```bash
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8001:8001"
    volumes:
      - ./avaliacoes:/app/avaliacoes
      - ./dados_cadastrais:/app/dados_cadastrais
      - ./treinamentos:/app/treinamentos

  frontend:
    build:
      context: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://SEU_IP:8001
    depends_on:
      - backend
EOF
```

### Passo 3: Deploy

```bash
# Build e executar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

**Acessar:** `http://SEU_IP` (frontend) e `http://SEU_IP:8001` (backend)

---

## Opção 5: Heroku (Simples) 🟣

### Backend

```bash
# Criar Procfile
echo "web: python api/main.py" > Procfile

# Criar runtime.txt
echo "python-3.12.0" > runtime.txt

# Heroku CLI
heroku login
heroku create talentboost-api
git push heroku main
```

### Frontend

```bash
cd frontend

# Configurar buildpack
heroku buildpacks:set heroku/nodejs

# Deploy
git push heroku main
```

---

## Comparação de Opções

| Opção | Setup | Custo | Permanente | HTTPS | Recomendado Para |
|-------|-------|-------|------------|-------|------------------|
| **Ngrok** | ⚡ 2 min | 🆓 Grátis | ❌ Temporário | ✅ Sim | Demo rápido, hackathon |
| **Railway** | 🚀 5 min | 💰 $5/mês (depois free tier) | ✅ Sim | ✅ Sim | MVP, produção |
| **Render** | 🌟 5 min | 🆓 Grátis | ✅ Sim | ✅ Sim | Projetos pessoais |
| **Docker VPS** | 🔧 30 min | 💰 $5-10/mês | ✅ Sim | ⚙️ Configurar | Controle total |
| **Heroku** | 💜 10 min | 💰 $7/mês | ✅ Sim | ✅ Sim | Simplicidade |

---

## URLs Públicas Geradas (Exemplos)

Após o deploy, você terá URLs como:

### Com Ngrok:
- Frontend: `https://abc123.ngrok.io`
- Backend: `https://def456.ngrok.io`
- API Docs: `https://def456.ngrok.io/docs`

### Com Railway/Render:
- Frontend: `https://talentboost.vercel.app`
- Backend: `https://talentboost-api.railway.app`
- API Docs: `https://talentboost-api.railway.app/docs`

---

## Teste de Conectividade

Após deploy, teste se está acessível:

```bash
# Testar backend
curl https://SUA_URL_BACKEND/

# Testar API
curl https://SUA_URL_BACKEND/api/employees

# Testar frontend (no navegador)
# Abra: https://SUA_URL_FRONTEND
```

---

## Atualizar CORS (se necessário)

Se tiver erro de CORS, edite `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://SUA_URL_FRONTEND",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 Recomendação para Hackathon

**Use Ngrok** (Opção 1):

1. Rápido (< 2 minutos)
2. Gratuito
3. HTTPS automático
4. Funciona imediatamente
5. Perfeito para apresentação/demo

```bash
# Um único comando:
./deploy_ngrok.sh

# Compartilhe as URLs geradas!
cat PUBLIC_URLS.txt
```

---

## 📝 Checklist de Deploy

- [ ] Ngrok instalado e configurado (authtoken)
- [ ] Dependências instaladas (Python + Node)
- [ ] Script `deploy_ngrok.sh` executado
- [ ] URLs públicas geradas e salvas
- [ ] Frontend acessível via HTTPS
- [ ] Backend respondendo via HTTPS
- [ ] API docs acessível (`/docs`)
- [ ] Teste de ponta a ponta realizado
- [ ] URLs compartilhadas com equipe/avaliadores

---

**Desenvolvido para o Hackathon LG TalentBoost** | Janeiro 2026
