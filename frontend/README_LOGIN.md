# 🔐 Sistema de Autenticação - TalentBoost

## Visão Geral

Sistema completo de autenticação implementado para o TalentBoost, permitindo que cada usuário acesse sua conta personalizada.

## 📋 Funcionalidades Implementadas

### 1. **Tela de Login** (`/login`)
- Design moderno e responsivo com layout em duas colunas
- Formulário de login com validação
- Campo de email e senha com toggle de visibilidade
- Lista expansível com usuários disponíveis para teste
- Loading state durante autenticação
- Mensagens de erro claras

### 2. **Gerenciamento de Autenticação** (`AuthContext`)
- Context API do React para estado global de autenticação
- Persistência de sessão no localStorage
- Suporte a múltiplos perfis de usuário:
  - **Colaborador** (employee)
  - **Gestor** (manager)
  - **Admin** (admin)

### 3. **Proteção de Rotas** (`ProtectedRoute`)
- Redirecionamento automático para login se não autenticado
- Verificação de permissões por role
- Loading state durante verificação

### 4. **Integração com Componentes**
- **Layout**: Exibe dados do usuário logado e botão de logout
- **MyCourses**: Usa dados do usuário autenticado para recomendações
- **App**: Roteamento completo com proteção de rotas

## 👥 Usuários Disponíveis para Teste

### Colaboradores
| Nome | Email | Cargo | Senha |
|------|-------|-------|-------|
| Ana Paula Ferreira | ana.ferreira@empresa.com | Desenvolvedora Backend | 123456 |
| Maria Santos | maria.santos@empresa.com | Analista de Dados | 123456 |
| João Pedro | joao.pedro@empresa.com | Desenvolvedor Frontend | 123456 |

### Gestores
| Nome | Email | Cargo | Senha |
|------|-------|-------|-------|
| Carlos Silva | carlos.silva@empresa.com | Gerente de TI | 123456 |
| Fernanda Costa | fernanda.costa@empresa.com | Tech Lead | 123456 |

**Senha padrão:** `123456`

## 🚀 Como Usar

### 1. Acessar a aplicação
```bash
# Navegar para o diretório frontend
cd lg_ia_hub/app/modules/deep_agent/test_htn/frontend

# Instalar dependências (se necessário)
npm install

# Iniciar o servidor de desenvolvimento
npm run dev
```

### 2. Fazer Login
1. Acesse `http://localhost:5173/login`
2. Escolha um usuário da lista ou digite manualmente:
   - Email: `ana.ferreira@empresa.com`
   - Senha: `123456`
3. Clique em "Entrar"

### 3. Navegar pela aplicação
Após o login, você será redirecionado para:
- **Colaboradores**: `/my-courses` (Meus Cursos)
- **Gestores**: `/manager` (Dashboard do Gestor)

### 4. Fazer Logout
Clique no botão "Sair" no canto superior direito da navegação.

## 🔒 Recursos de Segurança

1. **Validação de Credenciais**: Verifica email e senha antes de autenticar
2. **Proteção de Rotas**: Rotas privadas só acessíveis após login
3. **Controle de Acesso por Role**: Gestores têm acesso a rotas exclusivas
4. **Persistência de Sessão**: Sessão mantida após refresh da página
5. **Logout Seguro**: Limpa todas as informações de sessão

## 📁 Arquivos Criados/Modificados

### Novos Arquivos
- `src/contexts/AuthContext.tsx` - Context de autenticação
- `src/components/Login.tsx` - Tela de login
- `src/components/ProtectedRoute.tsx` - Componente de proteção de rotas

### Arquivos Modificados
- `src/App.tsx` - Integração com AuthProvider e rotas protegidas
- `src/components/Layout.tsx` - Uso do usuário autenticado e logout
- `src/components/MyCourses.tsx` - Uso do usuário autenticado

## 🎨 Design da Tela de Login

### Lado Esquerdo - Informações
- Logo e nome da aplicação
- Descrição da plataforma
- Cards com features principais:
  - 📚 Cursos Personalizados
  - 🏆 Acompanhamento de Progresso
  - 👥 Tutor Virtual

### Lado Direito - Formulário
- Título de boas-vindas
- Campo de email
- Campo de senha com toggle de visibilidade
- Botão de login com loading state
- Lista expansível de usuários para teste rápido

## 🔄 Fluxo de Autenticação

```
1. Usuário acessa /login
   ↓
2. Preenche credenciais
   ↓
3. AuthContext valida credenciais
   ↓
4. Se válido: salva no localStorage
   ↓
5. Redireciona para rota apropriada
   ↓
6. Layout carrega dados do usuário
   ↓
7. Componentes usam useAuth() para acessar dados
```

## 🛡️ Controle de Acesso por Role

| Rota | Colaborador | Gestor | Admin |
|------|-------------|--------|-------|
| `/login` | ✅ Público | ✅ Público | ✅ Público |
| `/my-courses` | ✅ | ✅ | ✅ |
| `/courses` | ✅ | ✅ | ✅ |
| `/manager` | ❌ | ✅ | ✅ |
| `/employees` | ✅ | ✅ | ✅ |
| `/dashboard` | ✅ | ✅ | ✅ |

## 💡 Próximas Melhorias (Opcional)

1. **Backend Real**
   - Integrar com API de autenticação
   - JWT tokens
   - Refresh tokens

2. **Recuperação de Senha**
   - Funcionalidade "Esqueci minha senha"
   - Email de recuperação

3. **Perfil do Usuário**
   - Página de perfil
   - Edição de dados
   - Upload de foto

4. **2FA (Autenticação de Dois Fatores)**
   - Código via email/SMS
   - Autenticação por aplicativo

5. **Logs de Auditoria**
   - Rastrear login/logout
   - Histórico de acessos

## 📝 Notas Técnicas

- **Estado Global**: Gerenciado via React Context API
- **Persistência**: localStorage para sessão do usuário
- **Roteamento**: React Router v6 com proteção de rotas
- **Validação**: Validação básica de formulário
- **UX**: Loading states e feedback visual em todas as ações

## 🐛 Troubleshooting

### Usuário não consegue fazer login
- Verifique se o email está correto (case-insensitive)
- Verifique se a senha é `123456`
- Limpe o localStorage: `localStorage.clear()`

### Redirecionamento não funciona
- Verifique se o `BrowserRouter` está envolvendo a aplicação
- Verifique as rotas no `App.tsx`

### Sessão não persiste
- Verifique se o localStorage está habilitado no navegador
- Verifique o console para erros de JSON parse

---

**Desenvolvido para o Hackathon LG TalentBoost** 🚀
