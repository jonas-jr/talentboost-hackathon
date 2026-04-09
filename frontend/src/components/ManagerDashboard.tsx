import { useEffect, useState } from 'react';
import { Users, TrendingUp, Target, Award, BookOpen, AlertCircle, CheckCircle } from 'lucide-react';
import { talentBoostApi } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

interface TeamMember {
  name: string;
  cargo: string;
  departamento: string;
  gaps_count: number;
  courses_completed: number;
  courses_in_progress: number;
  avg_performance: number;
}

export function ManagerDashboard() {
  const { user } = useAuth();
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      if (!user) return;

      try {
        const employees = await talentBoostApi.listEmployees();

        const visibleEmployees = employees.filter((employee) => {
          if (employee.name === user.name) return false;
          if (user.departamento === 'Diretoria') return true;
          return employee.departamento === user.departamento;
        });

        const teamData = await Promise.all(
          visibleEmployees.map(async (employee) => {
            const [gaps, recommendations, enrollments] = await Promise.all([
              talentBoostApi.analyzeGaps(employee.name).catch(() => ({ total_gaps: 0, gaps: [] })),
              talentBoostApi.getRecommendations(employee.name, 5, true).catch(() => null),
              talentBoostApi.getEmployeeEnrollments(employee.name).catch(() => ({
                summary: {
                  completed_courses: 0,
                  in_progress_courses: 0,
                  enrolled_courses: 0,
                },
              })),
            ]);

            return {
              name: employee.name,
              cargo: employee.cargo,
              departamento: employee.departamento,
              gaps_count: gaps.total_gaps || 0,
              courses_completed: enrollments.summary?.completed_courses || 0,
              courses_in_progress:
                (enrollments.summary?.in_progress_courses || 0) + (enrollments.summary?.enrolled_courses || 0),
              avg_performance: recommendations?.profile_summary?.nota_media_geral || 0,
            };
          })
        );

        setTeamMembers(teamData);
      } catch (error) {
        console.error('Erro ao carregar dados do gestor:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [user]);

  if (!user) return null;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const totalGaps = teamMembers.reduce((sum, member) => sum + member.gaps_count, 0);
  const avgPerformance = teamMembers.length
    ? teamMembers.reduce((sum, member) => sum + member.avg_performance, 0) / teamMembers.length
    : 0;
  const totalCoursesCompleted = teamMembers.reduce((sum, member) => sum + member.courses_completed, 0);
  const totalCoursesInProgress = teamMembers.reduce((sum, member) => sum + member.courses_in_progress, 0);
  const completionGoal = Math.max(teamMembers.length * 5, 1);
  const scopeLabel = user.departamento === 'Diretoria' ? 'empresa' : user.departamento;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard do Gestor</h1>
        <p className="text-gray-600 mt-1">
          Olá, {user.name}! Acompanhe o desenvolvimento do time {scopeLabel}.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Colaboradores</p>
              <p className="text-3xl font-bold text-gray-900">{teamMembers.length}</p>
            </div>
            <Users className="w-10 h-10 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Desempenho Médio</p>
              <p className="text-3xl font-bold text-green-600">{avgPerformance.toFixed(1)}</p>
              <p className="text-xs text-gray-500 mt-1">de 10</p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Gaps Identificados</p>
              <p className="text-3xl font-bold text-orange-600">{totalGaps}</p>
              <p className="text-xs text-gray-500 mt-1">total do time</p>
            </div>
            <Target className="w-10 h-10 text-orange-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Cursos Concluídos</p>
              <p className="text-3xl font-bold text-purple-600">{totalCoursesCompleted}</p>
              <p className="text-xs text-gray-500 mt-1">histórico consolidado</p>
            </div>
            <Award className="w-10 h-10 text-purple-600 opacity-20" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Progresso de Desenvolvimento</h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{teamMembers.length}</p>
            <p className="text-sm text-gray-600">Colaboradores</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{totalCoursesCompleted}</p>
            <p className="text-sm text-gray-600">Concluídos</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">{totalCoursesInProgress}</p>
            <p className="text-sm text-gray-600">Em Andamento</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-red-600">{totalGaps}</p>
            <p className="text-sm text-gray-600">Gaps a Endereçar</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Cursos Concluídos</span>
              <span>{totalCoursesCompleted} de {completionGoal} meta</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-green-600 h-3 rounded-full transition-all"
                style={{ width: `${Math.min((totalCoursesCompleted / completionGoal) * 100, 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Gaps Endereçados</span>
              <span>{Math.max(totalCoursesCompleted, 0)} de {Math.max(totalGaps, 1)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all"
                style={{ width: `${totalGaps > 0 ? Math.min((totalCoursesCompleted / totalGaps) * 100, 100) : 0}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Time - Visão Detalhada</h2>
        </div>

        {teamMembers.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Colaborador
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cargo
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Desempenho
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gaps
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Concluídos
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Em Andamento
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {teamMembers.map((member) => {
                  const performanceColor =
                    member.avg_performance >= 8
                      ? 'text-green-600'
                      : member.avg_performance >= 6
                      ? 'text-yellow-600'
                      : 'text-red-600';

                  const statusColor =
                    member.gaps_count === 0
                      ? 'bg-green-100 text-green-800'
                      : member.gaps_count <= 2
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800';

                  const statusText =
                    member.gaps_count === 0
                      ? 'Ótimo'
                      : member.gaps_count <= 2
                      ? 'Atenção'
                      : 'Crítico';

                  const statusIcon =
                    member.gaps_count === 0 ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />;

                  return (
                    <tr key={member.name} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <span className="text-primary-600 font-semibold">
                              {member.name.split(' ').map((part) => part[0]).join('')}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{member.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{member.cargo}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-lg font-semibold ${performanceColor}`}>
                          {member.avg_performance.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          member.gaps_count === 0
                            ? 'bg-green-100 text-green-800'
                            : member.gaps_count <= 2
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {member.gaps_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex items-center justify-center space-x-1">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-sm font-medium text-gray-900">{member.courses_completed}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex items-center justify-center space-x-1">
                          <BookOpen className="w-4 h-4 text-blue-600" />
                          <span className="text-sm font-medium text-gray-900">{member.courses_in_progress}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`px-3 py-1 inline-flex items-center space-x-1 text-xs leading-5 font-semibold rounded-full ${statusColor}`}>
                          {statusIcon}
                          <span>{statusText}</span>
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-10 text-center text-gray-500">
            Nenhum colaborador encontrado para o escopo atual.
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Insights Positivos</span>
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• {teamMembers.filter((member) => member.avg_performance >= 8).length} colaboradores com desempenho excelente (≥ 8.0)</li>
            <li>• {totalCoursesCompleted} cursos concluídos no histórico consolidado do time</li>
            <li>• Média de desempenho do time em {avgPerformance.toFixed(1)} pontos</li>
          </ul>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <h3 className="font-semibold text-orange-900 mb-3 flex items-center space-x-2">
            <AlertCircle className="w-5 h-5" />
            <span>Pontos de Atenção</span>
          </h3>
          <ul className="space-y-2 text-sm text-orange-800">
            <li>• {teamMembers.filter((member) => member.gaps_count > 2).length} colaboradores com 3+ gaps identificados</li>
            <li>• {totalGaps} gaps totais precisam de plano de desenvolvimento</li>
            <li>• {teamMembers.filter((member) => member.courses_in_progress === 0).length} colaboradores sem cursos em andamento</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
