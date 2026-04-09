# 🚀 Deploy Rápido - 2 Minutos

## Para tornar o TalentBoost acessível publicamente:

### 1️⃣ Instalar Ngrok

```bash
# Download e instalação
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### 2️⃣ Configurar Token

1. Crie conta grátis: https://dashboard.ngrok.com/signup
2. Copie seu token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure:

```bash
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### 3️⃣ Deploy!

```bash
cd /home/jonasjunior/lg-ia-hub-produto/lg_ia_hub/app/modules/deep_agent/test_htn

./deploy_ngrok.sh
```

### 4️⃣ Pronto! ✅

O script vai exibir:

```
════════════════════════════════════════════════════
  ✅ TalentBoost está PÚBLICO e ACESSÍVEL! 🎉
════════════════════════════════════════════════════

📱 Aplicação Web (Frontend):
   https://abc123.ngrok.io

🔌 API Backend:
   https://def456.ngrok.io
```

**Compartilhe essas URLs!** São acessíveis de qualquer lugar do mundo via HTTPS.

---

## 🔍 URLs Geradas

As URLs são salvas automaticamente em:
```bash
cat PUBLIC_URLS.txt
```

---

## ⚠️ Importante

- URLs são **temporárias** (expiram ao fechar o script)
- Para URLs **permanentes**, veja [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- Pressione `Ctrl+C` para encerrar

---

## 📝 Para Produção Permanente

Veja opções de deploy em:
- Railway (gratuito para começar)
- Render (100% gratuito)
- Vercel + Railway (combinação recomendada)

Detalhes completos em: **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)**

---

**Tempo total: ~2 minutos** ⚡
