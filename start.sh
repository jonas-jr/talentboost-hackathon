#!/bin/bash

# Script de inicialização do TalentBoost (Backend + Frontend)

echo "🚀 Iniciando LG TalentBoost..."
echo ""

# Diretório base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Encerrando servidores...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "${GREEN}✓ Servidores encerrados${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Verificar dependências Python
echo "${BLUE}📦 Verificando dependências Python...${NC}"
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "${YELLOW}⚠ Instalando dependências Python...${NC}"
    pip install fastapi uvicorn pydantic 2>&1 | grep -v "Requirement already satisfied" || true
fi
echo "${GREEN}✓ Dependências Python OK${NC}"
echo ""

# 2. Iniciar Backend
echo "${BLUE}🔧 Iniciando Backend API (porta 8001)...${NC}"
cd "$BASE_DIR"
python3 api/main.py > /tmp/talentboost_backend.log 2>&1 &
BACKEND_PID=$!

# Aguardar backend iniciar
sleep 3

# Verificar se backend está rodando
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "${GREEN}✓ Backend iniciado com sucesso${NC}"
    echo "  URL: http://localhost:8001"
    echo "  Logs: /tmp/talentboost_backend.log"
else
    echo "${YELLOW}⚠ Backend pode não ter iniciado corretamente${NC}"
    echo "  Verifique os logs em /tmp/talentboost_backend.log"
fi
echo ""

# 3. Verificar dependências Node
echo "${BLUE}📦 Verificando dependências Node...${NC}"
cd "$BASE_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "${YELLOW}⚠ Instalando dependências Node (primeira vez, pode demorar)...${NC}"
    npm install
fi
echo "${GREEN}✓ Dependências Node OK${NC}"
echo ""

# 4. Iniciar Frontend
echo "${BLUE}🎨 Iniciando Frontend (porta 5173)...${NC}"
npm run dev > /tmp/talentboost_frontend.log 2>&1 &
FRONTEND_PID=$!

# Aguardar frontend iniciar
sleep 5

echo "${GREEN}✓ Frontend iniciado${NC}"
echo "  URL: http://localhost:5173"
echo "  Logs: /tmp/talentboost_frontend.log"
echo ""

# 5. Resumo
echo "${GREEN}════════════════════════════════════════${NC}"
echo "${GREEN}  LG TalentBoost está rodando! 🎉${NC}"
echo "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "  📊 Dashboard:      ${BLUE}http://localhost:5173${NC}"
echo "  👥 Colaboradores:  ${BLUE}http://localhost:5173/employees${NC}"
echo "  🔌 API Docs:       ${BLUE}http://localhost:8001/docs${NC}"
echo ""
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "${YELLOW}Pressione Ctrl+C para encerrar${NC}"
echo ""

# Manter script rodando
wait
