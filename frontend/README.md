# TalentBoost Frontend

Interface web moderna para o sistema LG TalentBoost de recomendação de treinamentos.

## 🛠️ Stack Tecnológica

- **React 18** - Framework UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool (rápido e moderno)
- **Tailwind CSS** - Estilização
- **React Router** - Navegação
- **Recharts** - Gráficos interativos
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ instalado
- Backend API rodando na porta 8001

### Instalação

```bash
cd frontend
npm install
```

### Desenvolvimento

```bash
# Inicia servidor de desenvolvimento (porta 5173)
npm run dev
```

Acesse: http://localhost:5173

### Build para Produção

```bash
npm run build
```

Os arquivos otimizados serão gerados em `dist/`.

## 📂 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/        # Componentes React
│   │   ├── Dashboard.tsx  # Dashboard com estatísticas
│   │   ├── EmployeeList.tsx # Lista de colaboradores
│   │   ├── EmployeeDetail.tsx # Detalhes + recomendações
│   │   └── Layout.tsx     # Layout principal
│   ├── services/          # Serviços de API
│   │   └── api.ts         # Client HTTP (axios)
│   ├── types/             # Types TypeScript
│   │   └── index.ts       # Interfaces e tipos
│   ├── App.tsx            # Componente raiz
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globais (Tailwind)
├── index.html             # HTML principal
├── package.json           # Dependências
├── vite.config.ts         # Configuração Vite
├── tailwind.config.js     # Configuração Tailwind
└── tsconfig.json          # Configuração TypeScript
```

## 🎨 Funcionalidades

### Dashboard
- **Estatísticas gerais**: total de colaboradores, cursos, categorias
- **Gráfico de barras**: cursos por categoria
- **Gráfico de pizza**: distribuição de cursos

### Lista de Colaboradores
- **Busca** por nome, cargo ou departamento
- **Grid responsivo** com cards de colaboradores
- **Navegação** para detalhes do colaborador

### Detalhes do Colaborador
- **Resumo do perfil**: cargo, nível, nota média, gaps, pontos fortes
- **Tab de Gaps**:
  - Gráfico de notas por competência
  - Lista detalhada de gaps com severidade e urgência
  - Consenso entre avaliadores
  - Hints de desenvolvimento
- **Tab de Recomendações**:
  - Top 5 cursos personalizados
  - Relevância e prioridade
  - Justificativa de cada recomendação
  - Gaps endereçados por cada curso

## 🔌 Integração com Backend

O frontend consome a API REST em `http://localhost:8001/api`.

### Endpoints utilizados:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/employees` | GET | Lista todos os colaboradores |
| `/api/employees/{name}/profile` | GET | Dados cadastrais |
| `/api/employees/{name}/gaps` | GET | Análise de gaps |
| `/api/employees/{name}/recommendations` | POST | Recomendações personalizadas |
| `/api/stats/overview` | GET | Estatísticas gerais |

## 🎨 Design System

### Cores

- **Primary**: Blue (#0ea5e9)
- **Secondary**: Purple (#8b5cf6)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Error**: Red (#ef4444)

### Prioridades (cores)

- 🔴 **Critical**: Vermelho
- 🟠 **High**: Laranja
- 🟡 **Medium**: Amarelo
- 🟢 **Low**: Verde

## 🧪 Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Lint
npm run lint
```

## 📝 Notas

- O frontend usa **proxy** para chamadas à API (configurado em `vite.config.ts`)
- Todas as requisições para `/api` são redirecionadas para `http://localhost:8001`
- TypeScript strict mode habilitado para máxima segurança de tipos
- Tailwind JIT mode para classes CSS sob demanda

## 🚀 Próximas Funcionalidades

- [ ] Catálogo de cursos com filtros
- [ ] Comparação entre colaboradores
- [ ] Exportação de relatórios PDF
- [ ] Dashboard para gestores (visão de equipe)
- [ ] Trilhas de aprendizado personalizadas
- [ ] Notificações de novos cursos

---

**Desenvolvido para o Hackathon LG TalentBoost** | Janeiro 2026
