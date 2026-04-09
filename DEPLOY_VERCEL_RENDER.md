# Deploy Fullstack do TalentBoost

Este fluxo deixa:

- `frontend` publicado na Vercel
- `api` publicada no Render
- `Tutor Virtual` rodando com LLM real via Azure OpenAI ou OpenAI

## Arquitetura recomendada

- Frontend: Vercel
- Backend FastAPI: Render
- LLM:
  - preferencialmente `AZURE_OPENAI_*`
  - fallback suportado: `OPENAI_API_KEY` + `OPENAI_MODEL`

## 1. Subir a API no Render

No Render, crie um Blueprint apontando para este arquivo:

- `lg_ia_hub/app/modules/deep_agent/test_htn/render.yaml`

O serviço já está configurado para usar:

- `rootDir: lg_ia_hub/app/modules/deep_agent/test_htn`
- `buildCommand: pip install -r requirements.txt`
- `startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- `healthCheckPath: /api/health`

### Variáveis obrigatórias no Render

Para Azure OpenAI:

- `CORS_ALLOWED_ORIGINS=https://talentboost.vercel.app`
- `AZURE_OPENAI_ENDPOINT=...`
- `AZURE_OPENAI_API_KEY=...`
- `AZURE_OPENAI_DEPLOYMENT=...`
- `AZURE_OPENAI_API_VERSION=2024-10-01-preview`

Ou para OpenAI:

- `CORS_ALLOWED_ORIGINS=https://talentboost.vercel.app`
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-4o-mini`

### Testes do backend

Depois do deploy, teste:

- `https://SEU-BACKEND.onrender.com/api/health`
- `https://SEU-BACKEND.onrender.com/api/courses`

Se o tutor estiver com LLM real, `api/health` deve mostrar:

- `"llm_mode": "llm_powered"`

## 2. Apontar o frontend da Vercel para a API

No projeto `talentboost` da Vercel, adicione:

- `VITE_API_URL=https://SEU-BACKEND.onrender.com/api`

Importante:

- mudanças de env na Vercel só entram em novos deploys
- então depois de salvar a variável, faça novo deploy do frontend

## 3. Redeploy do frontend

Dentro de:

- `lg_ia_hub/app/modules/deep_agent/test_htn/frontend`

rode novamente:

```bash
vercel --prod
```

## 4. Checklist final

- login funcionando na Vercel
- tela `Meus Cursos` carregando cursos reais da API
- tela `Catálogo` carregando `/api/courses`
- dashboard do gestor carregando gaps e recomendações
- `Tutor Virtual` respondendo com conteúdo gerado por LLM
- `GET /api/health` retornando `llm_powered`

## Observações

- Sem `VITE_API_URL`, o frontend entra em fallback local para demo estática.
- Com `VITE_API_URL`, ele prioriza a API remota e usa o backend real.
- Se quiser liberar previews da Vercel também, use por exemplo:
  - `CORS_ALLOWED_ORIGINS=https://talentboost.vercel.app,https://SEU-PREVIEW.vercel.app`
- O regex padrão do backend já aceita domínios `*.vercel.app`.
