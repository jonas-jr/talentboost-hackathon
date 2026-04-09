# ⚡ Deploy Vercel - Comandos Rápidos

## 🎯 Passo a Passo Simplificado

### 1. Instalar Vercel CLI

```bash
npm install -g vercel
```

### 2. Deploy do Frontend

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn/frontend

# Login (abre navegador)
vercel login

# Deploy de produção
vercel --prod
```

**Anote a URL gerada**, algo como: `https://talentboost-abc123.vercel.app`

---

### 3. Deploy do Backend (Render)

**Via Interface Web** (mais fácil):

1. Acesse: https://render.com/signup (criar conta grátis - **sem cartão**)

2. Clique em "New" → "Web Service"

3. Clique em "Public Git repository" e cole:
   ```
   /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn
   ```
   
   **OU** faça upload dos arquivos manualmente

4. Configure:
   - **Name**: `talentboost-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api/main.py`
   - **Instance Type**: `Free`

5. Clique em "Create Web Service"

6. **Aguarde o build** (~2-3 minutos)

7. **Anote a URL gerada**, algo como: `https://talentboost-api.onrender.com`

---

### 4. Conectar Frontend ao Backend

**No Vercel:**

```bash
# Configurar variável de ambiente
vercel env add VITE_API_URL

# Quando perguntar, cole a URL do Render:
# https://talentboost-api.onrender.com

# Selecione: Production, Preview, Development

# Redeploy para aplicar
vercel --prod
```

**OU via Interface Web:**

1. Acesse seu projeto no Vercel
2. Settings → Environment Variables
3. Adicione:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://talentboost-api.onrender.com` (sua URL do Render)
   - **Environments**: Production ✅ Preview ✅ Development ✅

4. Vá em "Deployments" → Três pontinhos do último deploy → "Redeploy"

---

### 5. Atualizar CORS no Backend

**No Render**, vá em "Shell" (ou edite localmente e faça commit):

Edite `api/main.py` linha ~20:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://talentboost-abc123.vercel.app",  # ← Coloque SUA URL do Vercel aqui
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Salve e o Render fará redeploy automático.

---

## ✅ Pronto!

Você agora tem:

- ✅ **Frontend**: `https://talentboost-abc123.vercel.app` (sua URL)
- ✅ **Backend**: `https://talentboost-api.onrender.com` (sua URL)
- ✅ **API Docs**: `https://talentboost-api.onrender.com/docs`

**100% Gratuito** e **Permanente**! 🎉

---

## 🧪 Testar

```bash
# Testar backend
curl https://talentboost-api.onrender.com/

# Testar API
curl https://talentboost-api.onrender.com/api/employees

# Testar frontend no navegador
# Abra: https://talentboost-abc123.vercel.app
```

---

## 📝 Salvar URLs

```bash
cat > PUBLIC_URLS_VERCEL.txt <<EOF
TalentBoost - URLs Públicas (Vercel + Render)
==============================================

Frontend:
https://talentboost-abc123.vercel.app

Backend:
https://talentboost-api.onrender.com

API Docs:
https://talentboost-api.onrender.com/docs

Status: Permanente
Custo: R$ 0,00/mês
Deploy: $(date)
EOF
```

---

## ⚠️ Importante

- **Render Free**: Backend pode "dormir" após 15 min de inatividade
  - Primeira requisição pode demorar ~30s (cold start)
  - Isso é normal e esperado no plano gratuito
  
- **Vercel**: Sem limites de sleep, sempre ativo

---

## 🔄 Atualizar Deploy

### Frontend:
```bash
cd frontend
vercel --prod
```

### Backend:
- Faça commit e push → Render faz auto-deploy
- OU clique em "Manual Deploy" no painel do Render

---

**Tempo total**: ~10 minutos  
**Custo**: 🆓 R$ 0,00  
**Validade**: ♾️ Permanente
