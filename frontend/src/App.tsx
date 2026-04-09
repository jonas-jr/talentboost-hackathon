import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { Layout } from '@/components/Layout';
import { Dashboard } from '@/components/Dashboard';
import { EmployeeList } from '@/components/EmployeeList';
import { EmployeeDetail } from '@/components/EmployeeDetail';
import { MyCourses } from '@/components/MyCourses';
import { ManagerDashboard } from '@/components/ManagerDashboard';
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard';
import { Login } from '@/components/Login';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { CoursesLibrary } from '@/components/CoursesLibrary';
import { useAuth } from '@/contexts/AuthContext';

function DefaultHomeRedirect() {
  const { user } = useAuth();
  return <Navigate to={user?.role === 'manager' ? '/manager' : '/my-courses'} replace />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Rota pública - Login */}
          <Route path="/login" element={<Login />} />

          {/* Rotas protegidas */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            {/* Rota padrão redireciona conforme o papel */}
            <Route index element={<DefaultHomeRedirect />} />

            {/* Rotas do Colaborador */}
            <Route path="my-courses" element={<MyCourses />} />

            {/* Rotas do Gestor (requer role de manager) */}
            <Route
              path="manager"
              element={
                <ProtectedRoute requireRole="manager">
                  <ManagerDashboard />
                </ProtectedRoute>
              }
            />

            {/* Rotas compartilhadas */}
            <Route path="employees" element={<EmployeeList />} />
            <Route path="employees/:employeeName" element={<EmployeeDetail />} />

            {/* Rotas da Biblioteca de Cursos */}
            <Route path="trilhas" element={<CoursesLibrary />} />
            <Route path="courses" element={<CoursesLibrary />} />
            <Route path="biblioteca" element={<CoursesLibrary />} />

            <Route path="dashboard" element={<Dashboard />} />
            <Route
              path="analytics"
              element={
                <ProtectedRoute requireRole="manager">
                  <AnalyticsDashboard />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
