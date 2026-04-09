# 🎈 Tutor Virtual Flutuante

## 🎯 Visão Geral

O Tutor Virtual agora aparece como um **balão flutuante** no canto inferior direito da tela, **sempre disponível** em todas as páginas do TalentBoost.

---

## ✨ Funcionalidades

### **1. Sempre Disponível**
- ✅ Aparece em **todas as páginas** após login
- ✅ Botão flutuante no canto inferior direito
- ✅ Acompanha você em toda navegação

### **2. Estados do Chat**

| Estado | Visual | Comportamento |
|--------|--------|---------------|
| **Fechado** | Botão circular azul com ícone de mensagem | Hover mostra "Tutor Virtual" |
| **Aberto** | Janela de chat 400x600px | Chat funcional com histórico |
| **Minimizado** | Botão oval com texto | Clique para expandir novamente |

### **3. Controles**

- 🔘 **Abrir**: Clique no botão flutuante
- ➖ **Minimizar**: Clique no ícone de minimizar no header
- ❌ **Fechar**: Clique no X no header
- 🔄 **Expandir**: Clique no chat minimizado

---

## 🚫 Onde NÃO Aparece

O tutor é **automaticamente escondido** em:

- ❌ Páginas de avaliação (`/evaluation`, `/avaliacao`, `/exam`)
- ❌ Tela de login (`/login`)

**Motivo:** Durante avaliações, o usuário precisa focar sem distrações. Durante login, não há usuário autenticado.

---

## 🎨 Design

### **Botão Flutuante (Fechado)**
```
┌─────────────────────┐
│                     │
│                     │
│              [💬]   │  ← Botão azul circular
│                     │     Hover: "Tutor Virtual"
└─────────────────────┘
```

### **Chat Aberto**
```
┌──────────────────────────┐
│ 💬 Tutor Virtual    [_][X]│  ← Header azul
├──────────────────────────┤
│ Seu Progresso: 45%       │  ← Barra de progresso
├──────────────────────────┤
│ 🤖 Olá! Como posso...   │
│                          │  ← Área de mensagens
│ 👤 O que vou aprender?  │
│                          │
│ 🤖 Neste curso você...  │
├──────────────────────────┤
│ Perguntas rápidas:       │  ← Sugestões
│ • O que vou aprender?    │
├──────────────────────────┤
│ [Digite sua dúvida...] 📤│  ← Input
└──────────────────────────┘
```

### **Chat Minimizado**
```
┌─────────────────────────┐
│                         │
│              [💬 Tutor] │  ← Botão oval azul
│                         │     "Clique para expandir"
└─────────────────────────┘
```

---

## 🔧 Implementação Técnica

### **Estrutura de Componentes**

```
Layout.tsx
  └─ FloatingTutorChat.tsx (sempre renderizado)
       └─ CourseAssistantChat.tsx (quando aberto)
```

### **Estados React**

```typescript
const [isOpen, setIsOpen] = useState(false);         // Chat aberto/fechado
const [isMinimized, setIsMinimized] = useState(false); // Chat minimizado
```

### **Detecção de Página de Avaliação**

```typescript
const isEvaluationPage = location.pathname.includes('/evaluation') ||
                         location.pathname.includes('/avaliacao') ||
                         location.pathname.includes('/exam');

// No Layout:
{!isEvaluationPage && <FloatingTutorChat />}
```

---

## 🎯 Contexto do Curso

O tutor se adapta ao contexto:

### **1. Em "Meus Cursos" / "Catálogo"**
- Tutoria geral sobre a plataforma
- Pode responder sobre qualquer curso
- Uso do `cursoId = 'C001'` (curso padrão)

### **2. Dentro de um Curso Específico**
- Tutoria contextualizada ao curso aberto
- `currentCourseId` passado via props
- `currentProgress` reflete progresso real

**Futuro:** Detectar curso atual automaticamente via contexto global

---

## 📱 Responsividade

| Tela | Comportamento |
|------|---------------|
| Desktop (>1024px) | Chat 400x600px, canto direito |
| Tablet (768-1024px) | Chat 350x500px, ajustado |
| Mobile (<768px) | Chat fullscreen quando aberto |

---

## 🚀 Como Funciona

### **Fluxo de Uso**

```
1. Usuário faz login
   ↓
2. Layout renderiza FloatingTutorChat
   ↓
3. Botão flutuante aparece (canto direito)
   ↓
4. Usuário clica no botão
   ↓
5. Chat abre com mensagem de boas-vindas
   ↓
6. Usuário faz perguntas
   ↓
7. Azure OpenAI responde contextualizado
   ↓
8. Usuário pode minimizar ou fechar
   ↓
9. Chat persiste ao navegar entre páginas
```

### **Persistência da Sessão**

- ✅ Session ID gerado no componente
- ✅ Histórico mantido enquanto o chat não é fechado
- ✅ Ao fechar, próxima abertura inicia nova sessão

---

## 🔐 Segurança

- ✅ Só aparece após autenticação
- ✅ User ID e Name do usuário logado
- ✅ API Key nunca exposta ao frontend
- ✅ CORS configurado no backend

---

## 🎨 Customização

### **Cores** (em `FloatingTutorChat.tsx`)

```typescript
// Botão flutuante
bg-primary-600     // Azul padrão
hover:bg-primary-700

// Header do chat
from-primary-600 to-primary-800  // Gradiente azul

// Mensagens do bot
bg-gray-100 text-gray-900

// Mensagens do usuário
bg-primary-600 text-white
```

### **Tamanho do Chat**

```typescript
// Tamanho atual
w-96 h-[600px]

// Para ajustar:
w-[500px] h-[700px]  // Maior
w-80 h-[500px]       // Menor
```

### **Posição**

```typescript
// Posição atual
fixed bottom-6 right-6

// Para mover:
fixed bottom-6 left-6   // Canto esquerdo
fixed top-20 right-6    // Topo direito
```

---

## 🧪 Testando

### **1. Testar Visibilidade**
```
✅ Login → Botão aparece
✅ Meus Cursos → Botão aparece
✅ Catálogo → Botão aparece
✅ Dashboard → Botão aparece
❌ Login → Botão NÃO aparece
❌ /evaluation → Botão NÃO aparece (futuro)
```

### **2. Testar Funcionalidade**
```bash
# Backend rodando?
curl http://localhost:8001/docs

# Teste completo
./test_tutor.sh
```

### **3. Testar Estados**
```
1. Clique no botão → Chat abre
2. Faça uma pergunta → Resposta aparece
3. Clique em minimizar → Chat fica compacto
4. Clique no chat minimizado → Expande
5. Clique em fechar → Botão volta
6. Navegue entre páginas → Botão persiste
```

---

## 🐛 Troubleshooting

### ❌ **Botão não aparece**

**Causa:** Não está autenticado ou componente não renderizado

**Solução:**
1. Faça login
2. Verifique console (F12) por erros
3. Verifique se `FloatingTutorChat` está no `Layout.tsx`

---

### ❌ **Chat não responde**

**Causa:** Backend não está rodando

**Solução:**
```bash
cd lg_ia_hub/app/modules/deep_agent/test_htn
./start_backend.sh
```

---

### ❌ **Botão atrapalha conteúdo**

**Causa:** Posição fixa pode sobrepor elementos

**Solução:** Ajustar posição ou adicionar padding no conteúdo:
```typescript
// Em FloatingTutorChat.tsx
fixed bottom-6 right-6  → fixed bottom-20 right-6
```

---

### ❌ **Chat fica atrás de modais**

**Causa:** z-index baixo

**Solução:** Já configurado com `z-40` (botão) e `z-50` (chat aberto)

Se mesmo assim ficar atrás, aumente:
```typescript
z-40 → z-[100]
z-50 → z-[110]
```

---

## 📊 Diferenças: Antes vs Agora

| Aspecto | Antes | Agora |
|---------|-------|-------|
| **Acesso** | Botão em cada card de curso | Botão flutuante global |
| **Disponibilidade** | Só em Meus Cursos | Todas as páginas |
| **Modal** | Fullscreen | Chat compacto 400x600px |
| **Persistência** | Fecha ao navegar | Persiste entre páginas |
| **Estados** | Aberto/Fechado | Aberto/Minimizado/Fechado |
| **Contexto** | Sempre vinculado a um curso | Tutoria geral ou específica |

---

## 🎯 Próximas Melhorias (Opcional)

- [ ] Detectar curso atual automaticamente
- [ ] Notificação de nova mensagem quando minimizado
- [ ] Badge com contador de mensagens não lidas
- [ ] Arrastar e reposicionar o chat
- [ ] Histórico persistente (LocalStorage)
- [ ] Som de notificação
- [ ] Modo escuro
- [ ] Atalho de teclado (ex: Ctrl+Shift+T)

---

## ✅ Checklist de Funcionamento

- [ ] Botão flutuante aparece após login
- [ ] Clique no botão abre o chat
- [ ] Mensagem de boas-vindas aparece
- [ ] Perguntas são respondidas pela IA
- [ ] Minimizar funciona
- [ ] Fechar funciona
- [ ] Chat persiste ao navegar entre páginas
- [ ] NÃO aparece em páginas de avaliação
- [ ] NÃO aparece antes do login

---

**🎉 Tutor Virtual agora está sempre ao seu lado, em qualquer página!**

Clique, pergunte e aprenda com o poder da IA! 🤖✨
