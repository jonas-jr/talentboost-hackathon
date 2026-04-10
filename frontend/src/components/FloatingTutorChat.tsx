import { useState, useEffect } from 'react';
import { MessageCircle, X, Minimize2, Users, ChevronDown } from 'lucide-react';
import { CourseAssistantChat } from './CourseAssistantChat';
import { useAuth } from '@/contexts/AuthContext';
import { talentBoostApi } from '@/services/api';

interface FloatingTutorChatProps {
  currentCourseId?: string;
  currentCourseTitle?: string;
  currentProgress?: number;
}

interface Employee {
  name: string;
  cargo: string;
  departamento: string;
  nivel?: string;
}

export function FloatingTutorChat({
  currentCourseId,
  currentCourseTitle,
  currentProgress = 0,
}: FloatingTutorChatProps) {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [showEmployeeSelector, setShowEmployeeSelector] = useState(false);

  const isManager = user?.role === 'manager';

  // Carrega lista de colaboradores (só para gestores)
  useEffect(() => {
    async function loadEmployees() {
      if (isManager) {
        try {
          const data = await talentBoostApi.listEmployees();
          setEmployees(data || []);
        } catch (error) {
          console.error('Erro ao carregar colaboradores:', error);
        }
      }
    }
    loadEmployees();
  }, [isManager]);

  // Define o funcionário selecionado
  // Gestor: pode escolher qualquer um (padrão = ele mesmo)
  // Colaborador: sempre ele mesmo
  const targetEmployee = isManager && selectedEmployee ? selectedEmployee : {
    name: user?.name || '',
    cargo: user?.cargo || '',
    departamento: user?.departamento || '',
    nivel: user?.nivel || '',
  };

  if (!user) return null;

  // Se não tiver curso específico, usa modo geral
  const courseId = currentCourseId || 'general';
  const courseTitle = currentCourseTitle || 'Assistente TalentBoost';

  return (
    <>
      {/* Botão Flutuante */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 bg-primary-600 text-white rounded-full p-4 shadow-2xl hover:bg-primary-700 transition-all hover:scale-110 flex items-center space-x-3 group"
          aria-label="Abrir Tutor Virtual"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="hidden group-hover:inline-block text-sm font-medium pr-2">
            Tutor Virtual
          </span>
        </button>
      )}

      {/* Chat Expandido */}
      {isOpen && !isMinimized && (
        <div className="fixed bottom-6 right-6 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200">
          {/* Header com controles */}
          <div className="flex items-center justify-between bg-gradient-to-r from-primary-600 to-primary-800 text-white p-3">
            <div className="flex items-center space-x-2">
              <div className="bg-white bg-opacity-20 rounded-full p-1.5">
                <MessageCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold">Tutor Virtual</p>
                {isManager && selectedEmployee ? (
                  <p className="text-xs text-primary-100">Consultando: {selectedEmployee.name}</p>
                ) : (
                  <p className="text-xs text-primary-100">Sempre aqui para ajudar!</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setIsMinimized(true)}
                className="p-1.5 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                aria-label="Minimizar"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                aria-label="Fechar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Seletor de Colaborador (só para gestores) */}
          {isManager && (
            <div className="bg-blue-50 border-b border-blue-200 p-3">
              <button
                onClick={() => setShowEmployeeSelector(!showEmployeeSelector)}
                className="w-full flex items-center justify-between px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-gray-600" />
                  <span className="text-sm text-gray-700">
                    {selectedEmployee ? selectedEmployee.name : user.name + ' (Você)'}
                  </span>
                </div>
                <ChevronDown
                  className={`w-4 h-4 text-gray-600 transition-transform ${
                    showEmployeeSelector ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {showEmployeeSelector && (
                <div className="mt-2 max-h-48 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-lg">
                  {/* Opção: Eu mesmo */}
                  <button
                    onClick={() => {
                      setSelectedEmployee(null);
                      setShowEmployeeSelector(false);
                    }}
                    className="w-full text-left px-3 py-2 hover:bg-gray-100 transition-colors border-b border-gray-200"
                  >
                    <p className="text-sm font-medium text-gray-900">{user.name} (Você)</p>
                    <p className="text-xs text-gray-600">{user.cargo}</p>
                  </button>

                  {/* Lista de colaboradores */}
                  {employees.map((emp) => (
                    <button
                      key={emp.name}
                      onClick={() => {
                        setSelectedEmployee(emp);
                        setShowEmployeeSelector(false);
                      }}
                      className="w-full text-left px-3 py-2 hover:bg-gray-100 transition-colors border-b border-gray-200 last:border-b-0"
                    >
                      <p className="text-sm font-medium text-gray-900">{emp.name}</p>
                      <p className="text-xs text-gray-600">
                        {emp.cargo} · {emp.departamento}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Chat Component */}
          <div className="flex-1 overflow-hidden">
            <CourseAssistantChat
              cursoId={courseId}
              cursoTitulo={courseTitle}
              employeeId={user.id}
              employeeName={targetEmployee.name}
              progressoCurso={currentProgress}
              moduloAtual="Módulo Atual"
            />
          </div>
        </div>
      )}

      {/* Chat Minimizado */}
      {isOpen && isMinimized && (
        <button
          onClick={() => setIsMinimized(false)}
          className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-primary-600 to-primary-800 text-white rounded-full px-5 py-3 shadow-2xl hover:shadow-3xl transition-all flex items-center space-x-3"
        >
          <MessageCircle className="w-5 h-5" />
          <div className="text-left">
            <p className="text-sm font-semibold">Tutor Virtual</p>
            <p className="text-xs text-primary-100">Clique para expandir</p>
          </div>
        </button>
      )}
    </>
  );
}
