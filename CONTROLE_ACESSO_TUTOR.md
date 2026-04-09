# 🔐 Controle de Acesso - Tutor Virtual

## 📋 Visão Geral

O Tutor Virtual agora tem **controle de acesso baseado em role**:

- 👔 **Gestores:** Podem consultar cursos/informações de **qualquer colaborador**
- 👤 **Colaboradores:** Veem **apenas seus próprios dados**

---

## 🎯 Como Funciona

### **👤 Colaborador (Employee)**

```
┌──────────────────────────┐
│ 💬 Tutor Virtual    [_][X]│
├──────────────────────────┤
│ Progresso: 45%           │
├──────────────────────────┤
│ 🤖 Olá Ana! Como posso...│  ← Sempre vê seus próprios dados
│                          │
│ 👤 O que vou aprender?   │
└──────────────────────────┘

✅ Vê: Seus cursos, seu progresso, suas recomendações
❌ NÃO vê: Dados de outros colaboradores
```

---

### **👔 Gestor (Manager)**

```
┌──────────────────────────┐
│ 💬 Tutor Virtual    [_][X]│
│ Consultando: Maria Santos │  ← Mostra quem está consultando
├──────────────────────────┤
│ [👥 Carlos Silva (Você) ▼]│  ← Seletor de colaborador
├──────────────────────────┤
│ Progresso: 30%           │
├──────────────────────────┤
│ 🤖 Olá! Sobre Maria...   │  ← Chat contextualizado
│                          │
│ 👤 Qual progresso dela?  │
└──────────────────────────┘

✅ Pode selecionar qualquer colaborador
✅ Vê dados do colaborador selecionado
✅ Chat adapta respostas ao contexto do colaborador
```

---

## 🔄 Fluxo de Uso

### **Colaborador:**
1. Clica no balão flutuante 💬
2. Chat abre com **seus próprios dados**
3. Não há opção de selecionar outro colaborador

### **Gestor:**
1. Clica no balão flutuante 💬
2. Chat abre com **seus próprios dados** (padrão)
3. **Clica no seletor** 👥 (abaixo do header)
4. **Dropdown abre** com lista de colaboradores
5. **Seleciona um colaborador**
6. Chat **recarrega** com dados do colaborador selecionado
7. Header mostra: *"Consultando: Nome do Colaborador"*

---

## 🎨 Interface - Seletor de Colaborador

### **Fechado (padrão):**
```
┌────────────────────────────────┐
│ [👥 Carlos Silva (Você)     ▼] │
└────────────────────────────────┘
```

### **Aberto (clique):**
```
┌────────────────────────────────┐
│ [👥 Carlos Silva (Você)     ▲] │
├────────────────────────────────┤
│ ✓ Carlos Silva (Você)          │
│   Gerente de TI                │
├────────────────────────────────┤
│   Ana Paula Ferreira           │
│   Desenvolvedora Backend       │
├────────────────────────────────┤
│   Maria Santos                 │
│   Analista de Dados · Analytics│
└────────────────────────────────┘
```

---

## 🔒 Implementação Técnica

### **Detecção de Role:**

```typescript
const isManager = user?.role === 'manager';

// Carrega colaboradores (só para gestores)
useEffect(() => {
  if (isManager) {
    const data = await talentBoostApi.listEmployees();
    setEmployees(data);
  }
}, [isManager]);
```

### **Colaborador Alvo:**

```typescript
// Define quem será consultado
const targetEmployee = isManager && selectedEmployee 
  ? selectedEmployee  // Gestor selecionou alguém
  : {                 // Padrão: usuário logado
      name: user.name,
      cargo: user.cargo,
      // ...
    };

// Chat usa targetEmployee
<CourseAssistantChat
  employeeName={targetEmployee.name}
  // ...
/>
```

### **Componente Condicional:**

```typescript
{/* Seletor só aparece para gestores */}
{isManager && (
  <div className="bg-blue-50 border-b border-blue-200 p-3">
    <button onClick={() => setShowEmployeeSelector(!showEmployeeSelector)}>
      {/* Dropdown de colaboradores */}
    </button>
  </div>
)}
```

---

## 📊 Diferenças por Role

| Funcionalidade | Colaborador | Gestor |
|----------------|-------------|--------|
| **Acesso ao Tutor** | ✅ | ✅ |
| **Consultar próprios dados** | ✅ | ✅ |
| **Consultar dados de outros** | ❌ | ✅ |
| **Seletor de colaborador** | ❌ Não aparece | ✅ Aparece |
| **Lista de colaboradores** | ❌ Não carrega | ✅ Carrega via API |
| **Header mostra quem consulta** | ❌ | ✅ "Consultando: Nome" |

---

## 🧪 Testando

### **1. Como Colaborador:**

```bash
# Login como colaborador
Email: ana.ferreira@empresa.com
Senha: 123456
```

**Verificar:**
- [ ] Balão flutuante aparece
- [ ] Clica no balão → Chat abre
- [ ] **NÃO** aparece seletor de colaborador
- [ ] Chat mostra progresso de Ana
- [ ] Perguntas são contextualizadas a Ana

---

### **2. Como Gestor:**

```bash
# Login como gestor
Email: carlos.silva@empresa.com
Senha: 123456
```

**Verificar:**
- [ ] Balão flutuante aparece
- [ ] Clica no balão → Chat abre
- [ ] **APARECE** seletor de colaborador (👥 dropdown)
- [ ] Por padrão mostra: "Carlos Silva (Você)"
- [ ] Clica no seletor → Lista abre
- [ ] Lista mostra: Ana Paula, Maria Santos, João Pedro, etc.
- [ ] Seleciona "Ana Paula Ferreira"
- [ ] Header muda para: "Consultando: Ana Paula Ferreira"
- [ ] Chat recarrega com contexto de Ana
- [ ] Perguntas são sobre Ana (não sobre Carlos)

---

## 🔍 Backend - Como o Tutor Adapta

O backend recebe `employeeName` e busca dados do colaborador:

```python
# main.py - Endpoint /course-assistant/ask

# Busca dados cadastrais do colaborador
cadastro_path = DATA_DIR / "dados_cadastrais" / f"dadoscadastrais_{normalized}.json"
with open(cadastro_path) as f:
    cadastro = json.load(f)

cargo = cadastro.get("CARGO_NOME", "Colaborador")
nivel = "Pleno"  # ou lógica para detectar nível

# Contexto do aluno
student_context = StudentContext(
    employee_id=request.employee_id,
    nome=request.employee_name,  # ← Nome do colaborador selecionado
    cargo=cargo,
    nivel=nivel,
    progresso_curso=request.progresso_curso,
)

# LLM usa esse contexto para gerar resposta personalizada
response = course_assistant.ask(...)
```

**Exemplo de adaptação:**

**Pergunta do Gestor:** "Qual o progresso dela?"

**Contexto enviado:**
```json
{
  "employee_name": "Ana Paula Ferreira",
  "cargo": "Desenvolvedora Backend",
  "nivel": "Junior",
  "progresso_curso": 45
}
```

**Resposta do Tutor:**
```
Ana Paula Ferreira está com 45% do curso "Segurança da Informação" concluído.

Como Desenvolvedora Backend Junior, ela já completou os módulos:
1. Fundamentos de Segurança
2. Criptografia Básica

Ela está atualmente no módulo "Autenticação e Autorização".

Recomendo que ela pratique os exercícios de JWT e OAuth antes de avançar.
```

---

## 🎯 Casos de Uso

### **Caso 1: Gestor acompanha progresso do time**

```
Gestor Carlos quer ver como Ana está indo em "Segurança da Informação"

1. Carlos abre o Tutor Virtual
2. Seleciona "Ana Paula Ferreira" no dropdown
3. Pergunta: "Qual o progresso dela neste curso?"
4. Tutor responde com dados de Ana (45%, módulo atual, etc.)
5. Pergunta: "Ela está com dificuldades?"
6. Tutor analisa histórico de Ana e responde
```

### **Caso 2: Colaborador usa para si**

```
Ana quer tirar dúvida sobre criptografia

1. Ana abre o Tutor Virtual
2. Não há seletor (só vê seus dados)
3. Pergunta: "Como funciona criptografia assimétrica?"
4. Tutor responde adaptado ao nível Junior de Backend de Ana
5. Ana continua perguntando sobre Python e exemplos práticos
```

---

## 🐛 Troubleshooting

### **Gestor não vê o seletor**

**Causa:** Role não é 'manager'

**Solução:** Verificar no `AuthContext.tsx` se o usuário tem `role: 'manager'`:
```typescript
// Mock users em AuthContext.tsx
{
  email: "carlos.silva@empresa.com",
  role: "manager",  // ← Deve ser 'manager'
}
```

---

### **Lista de colaboradores vazia**

**Causa:** API `/employees` não retorna dados

**Solução:** Verificar backend:
```bash
curl http://localhost:8001/api/employees
```

Se retornar vazio, verificar arquivo de dados em:
```
lg_ia_hub/app/modules/deep_agent/test_htn/dados_cadastrais/
```

---

### **Chat não atualiza ao selecionar colaborador**

**Causa:** Key do componente não está mudando

**Solução:** Adicionar `key` ao `CourseAssistantChat`:
```typescript
<CourseAssistantChat
  key={targetEmployee.name}  // ← Force re-render
  employeeName={targetEmployee.name}
  // ...
/>
```

---

## 🔐 Segurança

### **Frontend:**
- ✅ Role verificado em `useAuth()`
- ✅ Seletor só renderiza se `isManager === true`
- ✅ Lista de colaboradores só carrega se gestor

### **Backend (TODO - Recomendado):**
- [ ] Adicionar autenticação nos endpoints
- [ ] Verificar role do usuário no backend
- [ ] Gestor pode acessar qualquer `/employees/:name`
- [ ] Colaborador só pode acessar `/employees/:seu-nome`

**Exemplo de verificação no backend:**
```python
@app.get("/api/employees/{employee_name}/profile")
def get_employee_profile(
    employee_name: str,
    current_user: User = Depends(get_current_user)
):
    # Se não é gestor, só pode ver próprio perfil
    if current_user.role != "manager":
        if employee_name != current_user.name:
            raise HTTPException(403, "Acesso negado")
    
    # Busca dados...
    return profile
```

---

## ✅ Checklist de Funcionamento

**Colaborador:**
- [ ] Balão aparece após login
- [ ] NÃO aparece seletor de colaborador
- [ ] Chat mostra dados do próprio usuário
- [ ] Respostas contextualizadas ao seu cargo/nível

**Gestor:**
- [ ] Balão aparece após login
- [ ] APARECE seletor de colaborador
- [ ] Pode selecionar qualquer colaborador da lista
- [ ] Header mostra "Consultando: [Nome]"
- [ ] Chat adapta ao colaborador selecionado
- [ ] Pode voltar a consultar próprios dados

---

## 📝 Exemplo Completo de Uso

```
🎬 CENÁRIO: Gestor Carlos revisa progresso de Ana

1. Carlos faz login como gestor
   → carlos.silva@empresa.com / 123456

2. Clica no balão flutuante 💬
   → Chat abre com seus próprios dados

3. Clica no seletor 👥
   → Dropdown abre com lista:
      ✓ Carlos Silva (Você)
        Ana Paula Ferreira
        Maria Santos
        João Pedro

4. Seleciona "Ana Paula Ferreira"
   → Header muda: "Consultando: Ana Paula Ferreira"
   → Chat recarrega

5. Pergunta: "Como está o progresso dela em Segurança da Informação?"
   → Tutor: "Ana está com 45% concluído, no módulo Autenticação..."

6. Pergunta: "Quais tópicos ela domina?"
   → Tutor: "Baseado nas avaliações, Ana domina Criptografia Básica..."

7. Pergunta: "Onde ela tem dificuldades?"
   → Tutor: "Ela teve notas mais baixas em OAuth e JWT..."

8. Seleciona outro colaborador ou volta para si mesmo
```

---

**🎉 Pronto! Agora gestores podem acompanhar o progresso de todo o time via Tutor Virtual!**

Teste agora:
1. Login como gestor: `carlos.silva@empresa.com` / `123456`
2. Clique no balão 💬
3. Selecione um colaborador 👥
4. Faça perguntas sobre ele!
