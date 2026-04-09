# 👥 TalentBoost - Guia de Interfaces de Usuário

## 🎯 Visão Geral

O TalentBoost agora possui **interfaces personalizadas** para cada tipo de usuário:

| Perfil | Interface Principal | Funcionalidades |
|---|---|---|
| 👤 **Colaborador** | Meus Cursos | Ver cursos recomendados, em andamento, concluídos |
| 👔 **Gestor** | Dashboard do Time | Acompanhar desenvolvimento do time, analytics |

---

## 👤 Interface do Colaborador

### Página: **Meus Cursos** (`/my-courses`)

#### 📊 Cards de Estatísticas

No topo da página, o colaborador vê:
- **Concluídos** - Quantos cursos completou
- **Em Andamento** - Cursos atualmente fazendo
- **Recomendados** - Novos cursos sugeridos
- **Nota Média** - Desempenho geral nos cursos

#### 📑 Abas de Cursos

**1. Recomendados para Você** ⭐
- Cursos personalizados baseados nos gaps identificados
- Explicação do porquê cada curso foi recomendado
- Badge "Recomendado" em destaque
- Botão "Matricular-se"

**2. Em Andamento** 📚
- Cursos que o colaborador está cursando
- Barra de progresso (ex: 45%)
- Badge com percentual de conclusão
- Botões:
  - **"Continuar Curso"** - Acessar o conteúdo
  - **"Tutor Virtual"** - Abrir chat com assistente IA

**3. Concluídos** ✅
- Cursos que já foram finalizados
- Nota obtida (ex: 9.5/10)
- Badge "Concluído" verde
- Botão "Ver Certificado"

**4. Todos os Cursos** 🗂️
- Catálogo completo disponível
- Botão "Matricular-se" para os não iniciados

#### 🤖 Tutor Virtual Integrado

Ao clicar em **"Tutor Virtual"** (cursos em andamento):
- Modal fullscreen com chat
- Histórico de conversas
- Perguntas rápidas sugeridas
- Barra de progresso do curso
- Assistente contextualizado ao seu cargo e nível

**Exemplo de perguntas:**
- "O que vou aprender neste curso?"
- "Como posso aplicar isso no meu trabalho?"
- "Tem exercícios práticos?"

---

## 👔 Interface do Gestor

### Página: **Dashboard do Time** (`/manager`)

#### 📊 KPIs do Time

Cards com métricas principais:
- **Total de Colaboradores** - Tamanho do time
- **Desempenho Médio** - Nota média do time (ex: 7.2/10)
- **Gaps Identificados** - Total de competências a desenvolver
- **Cursos Concluídos** - Total de cursos completados no ano

#### 📈 Progresso de Desenvolvimento

Gráficos visuais mostrando:
- **Cursos Concluídos** - Progresso vs meta
- **Gaps Endereçados** - Quantos gaps já têm plano de ação

#### 👥 Tabela de Colaboradores

Visão detalhada de cada membro do time:

| Coluna | Descrição |
|---|---|
| **Colaborador** | Nome + Avatar |
| **Cargo** | Função atual |
| **Desempenho** | Nota média (verde ≥8, amarelo ≥6, vermelho <6) |
| **Gaps** | Quantidade de competências a desenvolver |
| **Concluídos** | Cursos finalizados |
| **Em Andamento** | Cursos atuais |
| **Status** | Ótimo / Atenção / Crítico |

**Status do Colaborador:**
- 🟢 **Ótimo** - Nenhum gap identificado
- 🟡 **Atenção** - 1-2 gaps
- 🔴 **Crítico** - 3+ gaps (necessita plano urgente)

#### 💡 Insights e Recomendações

**Insights Positivos** (azul):
- Colaboradores com desempenho excelente
- Cursos concluídos no trimestre
- Taxa de conclusão

**Pontos de Atenção** (laranja):
- Colaboradores com muitos gaps
- Gaps totais não endereçados
- Colaboradores sem cursos em andamento

---

## 🔄 Navegação por Perfil

### Menu do Colaborador 👤

```
┌─────────────────────────────────────┐
│ 📚 Meus Cursos                       │
│ 🏠 Explorar Catálogo                 │
└─────────────────────────────────────┘
```

### Menu do Gestor 👔

```
┌─────────────────────────────────────┐
│ 🎯 Meu Time                          │
│ 👥 Todos os Colaboradores            │
│ 📚 Catálogo                          │
│ 📊 Analytics                         │
└─────────────────────────────────────┘
```

---

## 🔀 Trocar Perfil (Demo)

Para demonstração, há um botão no canto superior direito:

**"Trocar para Gestor"** / **"Trocar para Colaborador"**

Isso permite testar ambas as interfaces sem fazer login/logout.

---

## 🎨 Detalhes Visuais

### Cores por Status

| Status | Cor | Uso |
|---|---|---|
| Concluído | Verde | Cursos finalizados, colaboradores sem gaps |
| Em Andamento | Azul | Cursos em progresso |
| Recomendado | Roxo | Cursos sugeridos pelo sistema |
| Atenção | Amarelo | Desempenho médio, poucos gaps |
| Crítico | Vermelho | Muitos gaps, ação urgente |

### Badges e Ícones

- ✅ **CheckCircle** - Concluído
- ▶️ **PlayCircle** - Em andamento
- ⭐ **Award** - Nota/certificado
- 📚 **BookOpen** - Cursos
- 🎯 **Target** - Gaps/objetivos
- 💬 **MessageCircle** - Tutor virtual

---

## 🚀 Fluxo de Uso

### Colaborador:

1. **Acessa "Meus Cursos"**
2. Vê cursos **recomendados** baseados em seus gaps
3. Clica em **"Matricular-se"**
4. Curso aparece em **"Em Andamento"**
5. Durante o curso, pode usar **Tutor Virtual**
6. Ao concluir, vai para **"Concluídos"** com nota

### Gestor:

1. **Acessa "Meu Time"**
2. Vê **KPIs do time** (desempenho, gaps, conclusões)
3. Analisa **tabela de colaboradores**
4. Identifica quem está em **status crítico**
5. Verifica **insights e pontos de atenção**
6. Toma ações de desenvolvimento

---

## 📱 Responsividade

Ambas as interfaces são **totalmente responsivas**:

- **Desktop** - Grid 3-4 colunas
- **Tablet** - Grid 2 colunas
- **Mobile** - Grid 1 coluna

---

## 🔐 Autenticação (Produção)

Na versão de produção, adicionar:

```typescript
// Hook de autenticação
const { user, role } = useAuth();

// Redirecionar baseado no role
if (role === 'manager') {
  navigate('/manager');
} else {
  navigate('/my-courses');
}

// Proteger rotas
<ProtectedRoute role="manager">
  <ManagerDashboard />
</ProtectedRoute>
```

---

## 📊 Dados Mockados

Atualmente usa dados mock para demonstração:

**Colaborador:**
```typescript
{
  id: 2001,
  name: "Ana Paula Ferreira",
  cargo: "Desenvolvedora Backend",
  nivel: "Junior"
}
```

**Matrículas (mock):**
- C001 - Concluído (nota 9.5)
- C002 - Concluído (nota 8.0)
- C008 - Em andamento (45%)

**Gestor:**
```typescript
{
  name: "Roberto Silva",
  cargo: "Gerente de Tecnologia",
  team: "Tecnologia"
}
```

---

## 🎯 Próximos Passos

### Implementar:
- [ ] Autenticação real (JWT)
- [ ] Endpoint de matrículas (`POST /api/enrollments`)
- [ ] Persistência de progresso de curso
- [ ] Upload de certificados
- [ ] Notificações push
- [ ] Exportar relatórios (PDF)
- [ ] Filtros avançados na tabela do gestor
- [ ] Gráficos interativos (Recharts)

---

## 🧪 Como Testar

### 1. Iniciar o sistema:
```bash
# Backend
python api/main.py

# Frontend
cd frontend
npm run dev
```

### 2. Acessar as páginas:

**Colaborador:**
```
http://localhost:5173/my-courses
```

**Gestor:**
```
http://localhost:5173/manager
```

### 3. Testar funcionalidades:

✅ Navegar entre abas (Recomendados, Em Andamento, Concluídos, Todos)  
✅ Ver cards de estatísticas  
✅ Clicar em "Tutor Virtual" (cursos em andamento)  
✅ Conversar com o tutor  
✅ Trocar perfil (botão no header)  
✅ Ver dashboard do gestor  
✅ Analisar tabela de colaboradores  

---

## 📚 Arquivos Criados

```
frontend/src/components/
├── MyCourses.tsx           ← Interface do colaborador
├── ManagerDashboard.tsx    ← Interface do gestor
├── Layout.tsx              ← Navegação por perfil (atualizado)
└── App.tsx                 ← Rotas (atualizado)
```

---

**Status:** ✅ Interfaces implementadas e funcionais  
**Versão:** 2.1.0  
**Última atualização:** 2026-04-06
