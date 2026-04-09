import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Home, Users, BookOpen, BarChart, Target, User, LogOut } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { FloatingTutorChat } from './FloatingTutorChat';

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isManager = user?.role === 'manager';

  // Esconde o tutor durante avaliação
  const isEvaluationPage = location.pathname.includes('/evaluation') ||
                           location.pathname.includes('/avaliacao') ||
                           location.pathname.includes('/exam');

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-primary-500 to-purple-600 rounded-lg p-2">
                <BarChart className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">LG TalentBoost</h1>
                <p className="text-xs text-gray-500">Sistema Inteligente de Recomendação</p>
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                <p className="text-xs text-gray-500">
                  {isManager ? '👔 Gestor' : '👤 Colaborador'} · {user.cargo}
                </p>
              </div>
              <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="w-6 h-6 text-primary-600" />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex space-x-8">
              {isManager ? (
                <>
                  {/* Menu do Gestor */}
                  <Link
                    to="/manager"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/manager')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Target className="w-4 h-4" />
                    <span>Meu Time</span>
                  </Link>

                  <Link
                    to="/employees"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/employees')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Users className="w-4 h-4" />
                    <span>Todos os Colaboradores</span>
                  </Link>

                  <Link
                    to="/courses"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/courses')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <BookOpen className="w-4 h-4" />
                    <span>Catálogo</span>
                  </Link>

                  <Link
                    to="/analytics"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/analytics')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <BarChart className="w-4 h-4" />
                    <span>Analytics</span>
                  </Link>
                </>
              ) : (
                <>
                  {/* Menu do Colaborador */}
                  <Link
                    to="/my-courses"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/my-courses')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <BookOpen className="w-4 h-4" />
                    <span>Meus Cursos</span>
                  </Link>

                  <Link
                    to="/courses"
                    className={`flex items-center space-x-2 px-3 py-4 border-b-2 text-sm font-medium transition-colors ${
                      isActive('/courses')
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Home className="w-4 h-4" />
                    <span>Explorar Catálogo</span>
                  </Link>
                </>
              )}
            </div>

            {/* Logout */}
            <button
              onClick={handleLogout}
              className="text-xs px-3 py-2 bg-red-100 hover:bg-red-200 rounded-lg text-red-700 transition-colors flex items-center space-x-2"
            >
              <LogOut className="w-3 h-3" />
              <span>Sair</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            LG TalentBoost © 2026 · Hackathon LG · Desenvolvido com ❤️ usando IA
          </p>
        </div>
      </footer>

      {/* Chat Flutuante do Tutor Virtual - Aparece em todas as páginas exceto avaliação */}
      {!isEvaluationPage && <FloatingTutorChat />}
    </div>
  );
}
