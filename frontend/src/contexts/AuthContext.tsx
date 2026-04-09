import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: number;
  name: string;
  email: string;
  cargo: string;
  departamento: string;
  nivel: string;
  role: 'employee' | 'manager' | 'admin';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock de usuários - em produção, isso viria do backend
const MOCK_USERS: (User & { password: string })[] = [
  {
    id: 2001,
    name: "Ana Paula Ferreira",
    email: "ana.ferreira@empresa.com",
    password: "123456",
    cargo: "Desenvolvedora Backend",
    departamento: "Tecnologia",
    nivel: "Junior",
    role: "employee",
  },
  {
    id: 2002,
    name: "Bruno Henrique Costa",
    email: "bruno.costa@empresa.com",
    password: "123456",
    cargo: "Engenheiro de Dados",
    departamento: "Dados e Inteligência",
    nivel: "Pleno",
    role: "employee",
  },
  {
    id: 2005,
    name: "Elaine Rodrigues Martins",
    email: "elaine.martins@empresa.com",
    password: "123456",
    cargo: "Tech Lead",
    departamento: "Tecnologia",
    nivel: "Senior",
    role: "manager",
  },
  {
    id: 2010,
    name: "João Pedro Almeida Vieira",
    email: "joao.pedro@empresa.com",
    password: "123456",
    cargo: "Arquiteto de Software",
    departamento: "Tecnologia",
    nivel: "Senior",
    role: "employee",
  },
  {
    id: 2014,
    name: "Nelson Cardoso Barbosa",
    email: "nelson.barbosa@empresa.com",
    password: "123456",
    cargo: "Gerente de Produto",
    departamento: "Produto",
    nivel: "Senior",
    role: "manager",
  },
  {
    id: 2020,
    name: "Tatiana Luz Fontenele",
    email: "tatiana.fontenele@empresa.com",
    password: "123456",
    cargo: "Diretora de Tecnologia",
    departamento: "Diretoria",
    nivel: "Senior",
    role: "manager",
  },
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verifica se há um usuário salvo no localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Simula chamada à API
      await new Promise(resolve => setTimeout(resolve, 800));

      const foundUser = MOCK_USERS.find(
        u => u.email.toLowerCase() === email.toLowerCase() && u.password === password
      );

      if (!foundUser) {
        throw new Error('Email ou senha incorretos');
      }

      // Remove a senha antes de salvar
      const { password: _, ...userWithoutPassword } = foundUser;

      setUser(userWithoutPassword);
      localStorage.setItem('user', JSON.stringify(userWithoutPassword));
      return userWithoutPassword;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Exportar lista de usuários para a tela de login mostrar os emails disponíveis
export const availableUsers = MOCK_USERS.map(u => ({
  email: u.email,
  name: u.name,
  role: u.role,
}));
