# 🔧 Como Corrigir o Tutor Virtual

## ❌ Problema

O tutor está respondendo com mensagens simuladas (mock) em vez de usar o Azure OpenAI de verdade.

**Resposta atual:**
```
[Aqui entraria a resposta contextualizada usando a LLM real]
```

## ✅ Solução

### **Passo 1: Pare o backend atual**

```bash
# Ctrl+C no terminal onde o backend está rodando
# Ou:
pkill -f "uvicorn main:app"
```

---

### **Passo 2: Execute o script de correção**

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./fix_and_restart.sh
```

**O que o script faz:**
1. ✅ Para o backend anterior
2. ✅ Carrega variáveis do `.env`
3. ✅ Verifica se `AZURE_OPENAI_DEPLOYMENT` está configurado
4. ✅ Inicia o backend com LLM ativada

---

### **Passo 3: Teste se funcionou**

Em **outro terminal**:

```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./test_tutor.sh
```

**Você deve ver:**
```
✅ Todos os testes passaram!
```

---

## 🔍 O que Foi Corrigido

### **1. Variável Faltando no Config**

**Antes:**
```python
# config.py NÃO tinha AZURE_OPENAI_DEPLOYMENT
```

**Depois:**
```python
# config.py AGORA tem:
AZURE_OPENAI_DEPLOYMENT: str | None = Field(
    default=None,
    validation_alias=AliasChoices(
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",  # ← Lê do .env
    ),
)
```

### **2. O .env Já Tinha a Variável**

```bash
# No seu .env (linha 18):
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-evaluation
```

Agora o config consegue ler essa variável! ✅

---

## 🧪 Verificar Manualmente

### **1. Verificar se o deployment está carregado:**

```bash
python3 << 'EOF'
from lg_ia_hub.app.core.config import get_settings
settings = get_settings()
print(f"DEPLOYMENT: {settings.AZURE_OPENAI_DEPLOYMENT}")
EOF
```

**Esperado:** `DEPLOYMENT: gpt-4.1-evaluation`

---

### **2. Testar o tutor com curl:**

```bash
curl -X POST http://localhost:8001/api/course-assistant/ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-final",
    "curso_id": "C001",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "question": "O que é criptografia?",
    "progresso_curso": 10,
    "modulo_atual": "Fundamentos"
  }'
```

**Esperado:** Resposta detalhada sobre criptografia (não mock!)

---

## 🎯 Como Saber se Está Funcionando

### **❌ Resposta MOCK (errado):**
```json
{
  "content": "Entendo sua dúvida sobre o conteúdo de **Segurança da Informação**.\n\nComo Desenvolvedora Backend com nível Pleno, acredito que esse ponto é importante para você.\n\n[Aqui entraria a resposta contextualizada usando a LLM real]\n\nIsso responde sua pergunta?"
}
```

### **✅ Resposta REAL (correto):**
```json
{
  "content": "Criptografia é uma técnica de segurança que transforma dados legíveis em formato codificado...\n\nComo Desenvolvedora Backend Pleno, você provavelmente já trabalhou com bibliotecas como bcrypt, JWT, ou TLS/SSL...\n\nOs 3 principais tipos de criptografia são:\n1. Simétrica (AES, DES)\n2. Assimétrica (RSA, ECC)\n3. Hash (SHA-256, MD5)\n\nQuer que eu explique algum desses em mais detalhes?"
}
```

**Diferença:** A resposta real é **específica, detalhada e contextualizada**!

---

## 📊 Logs do Backend

Quando o LLM estiver funcionando, você verá nos logs:

```
✅ LLM inicializada via DeepAgent (configuração completa do projeto)
```

Ou:

```
✅ LLM inicializada via Azure OpenAI direto (deployment: gpt-4.1-evaluation)
```

**Se ver:**
```
⚠️  Nenhuma LLM disponível. Course Assistant rodará em modo simulado.
```

**= LLM NÃO está funcionando!**

---

## 🐛 Troubleshooting

### **Erro: "DEPLOYMENT: None"**

**Causa:** `.env` não foi carregado

**Solução:**
```bash
export $(cat .env | grep -v '^#' | xargs)
./fix_and_restart.sh
```

---

### **Erro: "API_KEY: MISSING!"**

**Causa:** `AZURE_OPENAI_API_KEY` não está no `.env`

**Solução:** Verifique se a linha 17 do `.env` existe:
```bash
AZURE_OPENAI_API_KEY=8qmowfKs37CR9JNv0Lbj8mvKYuO5NBJ8p2uT350cuXXLgTp6MSIAJQQJ99BBACHYHv6XJ3w3AAAAACOGd4e6
```

---

### **Backend não inicia**

**Causa:** Porta 8001 em uso

**Solução:**
```bash
# Mata processo na porta
kill $(lsof -t -i:8001)

# Reinicia
./fix_and_restart.sh
```

---

## ✅ Checklist Final

Após reiniciar o backend, verifique:

- [ ] Backend rodando em http://localhost:8001
- [ ] Logs mostram "LLM inicializada"
- [ ] `./test_tutor.sh` passa todos os testes
- [ ] Frontend recebe respostas reais (não mock)
- [ ] Tutor responde perguntas específicas com detalhes
- [ ] Respostas são contextualizadas ao cargo/nível do usuário

---

## 🚀 Pronto!

Agora o Tutor Virtual funciona com **IA real do Azure OpenAI**! 🤖✨

**Teste no navegador:**
1. Acesse: http://localhost:5173
2. Login: `ana.ferreira@empresa.com` / `123456`
3. Clique no **balão flutuante** no canto direito 💬
4. Pergunte algo específico: *"Como implementar criptografia em Python?"*
5. Receba uma resposta detalhada e contextualizada!

---

**Se ainda não funcionar, verifique:**
- Backend está com os logs mostrando "LLM inicializada"?
- `.env` tem as 3 variáveis: `ENDPOINT`, `API_KEY`, `DEPLOYMENT_NAME`?
- Teste com curl retorna resposta real (não mock)?

Se todos os acima estiverem OK e ainda não funcionar, compartilhe os logs do backend comigo!
