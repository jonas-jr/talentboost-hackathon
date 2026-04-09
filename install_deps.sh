#!/bin/bash
#
# Script de instalação de dependências do TalentBoost
#
# Uso: bash install_deps.sh

echo "🚀 TalentBoost - Instalando dependências..."
echo ""

# Vai para o diretório correto
cd "$(dirname "$0")"

# Instala dependências básicas
echo "📦 Instalando dependências do requirements.txt..."
pip install -r requirements.txt

# Verifica se quer instalar dependências opcionais
echo ""
read -p "Deseja instalar dependências opcionais (numpy, scikit-learn para Matrix Factorization)? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Instalando numpy e scikit-learn..."
    pip install numpy scikit-learn
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "Para iniciar o backend:"
echo "  python api/main.py"
echo ""
echo "Para testar o Course Assistant:"
echo "  python test_course_assistant_llm.py"
