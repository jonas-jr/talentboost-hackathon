# 🚀 TalentBoost - Início Rápido

## ⚡ Iniciar Tudo em 3 Comandos

### **Terminal 1 - Backend:**
```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./start_backend.sh
```

### **Terminal 2 - Frontend:**
```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn/frontend
npm run dev
```

### **Navegador:**
```
http://localhost:5173
```

---

## 🔑 Login Rápido

- **Email:** `ana.ferreira@empresa.com`
- **Senha:** `123456`

Ou clique em qualquer usuário na lista da tela de login!

---

## 🧪 Testar se está funcionando

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./test_tutor.sh
```

Se todos os testes passarem ✅, está tudo funcionando!

---

## 📚 Documentação Completa

- **[TUTOR_VIRTUAL_SETUP.md](./TUTOR_VIRTUAL_SETUP.md)** - Guia completo do Tutor Virtual
- **[README_LOGIN.md](./frontend/README_LOGIN.md)** - Sistema de autenticação
- **[API_TOOLS.md](./API_TOOLS.md)** - Documentação das APIs

---

## 🎯 Principais Funcionalidades

### ✅ Sistema de Login
- 5 usuários de teste (3 colaboradores + 2 gestores)
- Sessão persistente
- Controle de acesso por role

### ✅ Meus Cursos
- Cursos recomendados personalizados
- Cursos em andamento
- Cursos concluídos
- Progresso e notas

### ✅ Explorar Catálogo
- Biblioteca completa de cursos
- Filtros por categoria e modalidade
- Busca por texto
- Ordenação

### ✅ Tutor Virtual 🤖
- Chat com IA (Azure OpenAI)
- Respostas contextualizadas ao curso e perfil
- Sugestões personalizadas
- Histórico de conversas

---

## 🛠️ Portas Usadas

| Serviço | Porta | URL |
|---------|-------|-----|
| Frontend (Vite) | 5173 | http://localhost:5173 |
| Backend (FastAPI) | 8001 | http://localhost:8001 |
| API Docs (Swagger) | 8001 | http://localhost:8001/docs |

---

## 🐛 Problemas Comuns

### ❌ **"Backend não inicia"**
```bash
# Ativa ambiente virtual
source .venv/bin/activate

# Instala dependências
pip install fastapi uvicorn langchain-openai structlog
```

### ❌ **"npm run dev" falha**
```bash
cd frontend
npm install
npm run dev
```

### ❌ **"Tutor não responde"**
1. Verifique se o backend está rodando: http://localhost:8001/docs
2. Execute `./test_tutor.sh` para diagnóstico
3. Veja logs no terminal do backend

---

## 📊 Dados de Teste

Os dados ficam em:
```
lg_ia_hub/app/modules/deep_agent/test_htn/
├── dados_cadastrais/    # Perfis dos colaboradores
├── avaliacoes/          # Avaliações de desempenho
└── treinamentos/        # Histórico de cursos
```

---

## 🎉 Pronto!

Agora você tem:
- ✅ Sistema de login funcional
- ✅ Recomendações personalizadas de cursos
- ✅ Tutor virtual com IA real
- ✅ Interface moderna e responsiva

**Divirta-se explorando o TalentBoost! 🚀**
