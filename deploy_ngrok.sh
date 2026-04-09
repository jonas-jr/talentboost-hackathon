#!/bin/bash

# Script de deploy com ngrok para demo/produção temporária

echo "🚀 TalentBoost - Deploy com Ngrok"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Diretório base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Função de limpeza
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Encerrando servidores...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $NGROK_BACKEND_PID 2>/dev/null
    kill $NGROK_FRONTEND_PID 2>/dev/null
    echo "${GREEN}✓ Servidores encerrados${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "${RED}✗ ngrok não encontrado${NC}"
    echo ""
    echo "Instale o ngrok:"
    echo "  wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  tar xvzf ngrok-v3-stable-linux-amd64.tgz"
    echo "  sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "Depois execute: ngrok config add-authtoken YOUR_TOKEN"
    echo "Obtenha seu token em: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# 2. Verificar dependências Python
echo "${BLUE}📦 Verificando dependências Python...${NC}"
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "${YELLOW}⚠ Instalando dependências Python...${NC}"
    pip install fastapi uvicorn pydantic 2>&1 | grep -v "Requirement already satisfied" || true
fi
echo "${GREEN}✓ Dependências Python OK${NC}"
echo ""

# 3. Build do Frontend (produção)
echo "${BLUE}🔨 Fazendo build do frontend...${NC}"
cd "$BASE_DIR/frontend"

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo "${YELLOW}⚠ Instalando dependências Node...${NC}"
    npm install
fi

# Build
npm run build
echo "${GREEN}✓ Build do frontend concluído${NC}"
echo ""

# 4. Iniciar Backend
echo "${BLUE}🔧 Iniciando Backend API...${NC}"
cd "$BASE_DIR"
python3 api/main.py > /tmp/talentboost_backend.log 2>&1 &
BACKEND_PID=$!

# Aguardar backend iniciar
sleep 3

if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "${GREEN}✓ Backend iniciado (localhost:8001)${NC}"
else
    echo "${RED}✗ Falha ao iniciar backend${NC}"
    cat /tmp/talentboost_backend.log
    exit 1
fi
echo ""

# 5. Servir Frontend (build estático)
echo "${BLUE}🎨 Servindo Frontend (build de produção)...${NC}"
cd "$BASE_DIR/frontend/dist"
python3 -m http.server 5173 > /tmp/talentboost_frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 2
echo "${GREEN}✓ Frontend servido (localhost:5173)${NC}"
echo ""

# 6. Expor Backend via Ngrok
echo "${BLUE}🌐 Expondo Backend via Ngrok...${NC}"
ngrok http 8001 --log=stdout > /tmp/ngrok_backend.log 2>&1 &
NGROK_BACKEND_PID=$!

sleep 3

# Pegar URL do ngrok backend
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo "${RED}✗ Falha ao obter URL do ngrok backend${NC}"
    echo "Verifique se você configurou o authtoken:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    cleanup
fi

echo "${GREEN}✓ Backend exposto publicamente${NC}"
echo "${GREEN}  URL: $BACKEND_URL${NC}"
echo ""

# 7. Atualizar configuração do frontend com URL pública do backend
echo "${BLUE}🔄 Configurando frontend para usar backend público...${NC}"

# Criar arquivo .env.production
cat > "$BASE_DIR/frontend/.env.production" <<EOF
VITE_API_URL=$BACKEND_URL
EOF

# Rebuild frontend com nova URL
cd "$BASE_DIR/frontend"
npm run build > /dev/null 2>&1

# Reiniciar servidor de frontend
kill $FRONTEND_PID 2>/dev/null
cd "$BASE_DIR/frontend/dist"
python3 -m http.server 5173 > /tmp/talentboost_frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 2
echo "${GREEN}✓ Frontend reconfigurado${NC}"
echo ""

# 8. Expor Frontend via Ngrok
echo "${BLUE}🌐 Expondo Frontend via Ngrok...${NC}"
ngrok http 5173 --log=stdout > /tmp/ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!

sleep 3

# Pegar URL do ngrok frontend
FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | tail -1)

if [ -z "$FRONTEND_URL" ]; then
    echo "${RED}✗ Falha ao obter URL do ngrok frontend${NC}"
    cleanup
fi

echo "${GREEN}✓ Frontend exposto publicamente${NC}"
echo "${GREEN}  URL: $FRONTEND_URL${NC}"
echo ""

# 9. Atualizar CORS do backend
echo "${BLUE}🔒 Atualizando CORS do backend...${NC}"

# Backup do arquivo original
cp "$BASE_DIR/api/main.py" "$BASE_DIR/api/main.py.backup"

# Atualizar CORS para aceitar URL pública
sed -i "s|allow_origins=\[.*\]|allow_origins=[\"$FRONTEND_URL\", \"http://localhost:5173\", \"http://localhost:3000\"]|" "$BASE_DIR/api/main.py"

# Reiniciar backend
kill $BACKEND_PID 2>/dev/null
cd "$BASE_DIR"
python3 api/main.py > /tmp/talentboost_backend.log 2>&1 &
BACKEND_PID=$!

sleep 3
echo "${GREEN}✓ CORS atualizado${NC}"
echo ""

# 10. Salvar URLs em arquivo
cat > "$BASE_DIR/PUBLIC_URLS.txt" <<EOF
TalentBoost - URLs Públicas
============================

Frontend (Aplicação Web):
$FRONTEND_URL

Backend API:
$BACKEND_URL

API Docs (Swagger):
$BACKEND_URL/docs

Endpoints principais:
- $BACKEND_URL/api/employees
- $BACKEND_URL/api/stats/overview

Criado em: $(date)

IMPORTANTE: Estas URLs são temporárias e expiram quando o ngrok é fechado.
Para URLs permanentes, considere deploy em Heroku, Railway ou Vercel.
EOF

# 11. Exibir resumo
echo "${GREEN}════════════════════════════════════════════════════${NC}"
echo "${GREEN}  ✅ TalentBoost está PÚBLICO e ACESSÍVEL! 🎉${NC}"
echo "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo "${BLUE}📱 Aplicação Web (Frontend):${NC}"
echo "   ${GREEN}$FRONTEND_URL${NC}"
echo ""
echo "${BLUE}🔌 API Backend:${NC}"
echo "   ${GREEN}$BACKEND_URL${NC}"
echo ""
echo "${BLUE}📖 Documentação da API:${NC}"
echo "   ${GREEN}$BACKEND_URL/docs${NC}"
echo ""
echo "${BLUE}📋 URLs salvas em:${NC}"
echo "   $BASE_DIR/PUBLIC_URLS.txt"
echo ""
echo "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   • Estas URLs são públicas e acessíveis de qualquer lugar"
echo "   • As URLs expiram quando você fechar este script (Ctrl+C)"
echo "   • Para URLs permanentes, faça deploy em serviço cloud"
echo ""
echo "${BLUE}🔍 Para ver logs em tempo real:${NC}"
echo "   Backend:  tail -f /tmp/talentboost_backend.log"
echo "   Frontend: tail -f /tmp/talentboost_frontend.log"
echo ""
echo "${YELLOW}Pressione Ctrl+C para encerrar${NC}"
echo ""

# Manter script rodando
wait
