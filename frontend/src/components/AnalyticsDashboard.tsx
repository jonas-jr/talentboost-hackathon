import { useEffect, useState } from 'react';
import { TrendingUp, Users, BookOpen, Award, Eye, MousePointer, UserCheck } from 'lucide-react';
import { talentBoostApi } from '@/services/api';

interface AnalyticsSummary {
  total_interactions: number;
  total_views: number;
  total_clicks: number;
  total_enrollments: number;
  total_dismissals: number;
  overall_ctr: number;
  overall_enrollment_rate: number;
  unique_employees: number;
  unique_courses: number;
}

interface PopularCourse {
  curso_id: string;
  titulo: string;
  clicks: number;
  enrollments: number;
  views: number;
}

const COLOR_CLASSES = {
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
  },
  purple: {
    bg: 'bg-purple-100',
    text: 'text-purple-600',
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
  },
  indigo: {
    bg: 'bg-indigo-100',
    text: 'text-indigo-600',
  },
} as const;

type StatColor = keyof typeof COLOR_CLASSES;

export function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [popularCourses, setPopularCourses] = useState<PopularCourse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        // Carrega resumo de analytics
        const summaryData = await talentBoostApi.getAnalyticsSummary();
        setSummary(summaryData);

        // Carrega cursos populares
        const popularData = await talentBoostApi.getPopularCourses(5);
        setPopularCourses(popularData.popular_courses || []);
      } catch (error) {
        console.error('Erro ao carregar analytics:', error);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center p-12">
        <p className="text-gray-600">Nenhum dado de analytics disponível ainda.</p>
      </div>
    );
  }

  const stats = [
    {
      label: 'Total de Interações',
      value: summary.total_interactions.toLocaleString(),
      icon: MousePointer,
      color: 'blue' as StatColor,
    },
    {
      label: 'Visualizações',
      value: summary.total_views.toLocaleString(),
      icon: Eye,
      color: 'purple' as StatColor,
    },
    {
      label: 'Cliques',
      value: summary.total_clicks.toLocaleString(),
      icon: MousePointer,
      color: 'green' as StatColor,
    },
    {
      label: 'Matrículas',
      value: summary.total_enrollments.toLocaleString(),
      icon: UserCheck,
      color: 'indigo' as StatColor,
    },
  ];

  const metrics = [
    {
      label: 'Taxa de Cliques (CTR)',
      value: `${(summary.overall_ctr * 100).toFixed(1)}%`,
      description: 'Cliques / Visualizações',
      icon: TrendingUp,
    },
    {
      label: 'Taxa de Matrícula',
      value: `${(summary.overall_enrollment_rate * 100).toFixed(1)}%`,
      description: 'Matrículas / Cliques',
      icon: Award,
    },
    {
      label: 'Colaboradores Ativos',
      value: summary.unique_employees.toString(),
      description: 'Colaboradores únicos',
      icon: Users,
    },
    {
      label: 'Cursos Visualizados',
      value: summary.unique_courses.toString(),
      description: 'Cursos únicos',
      icon: BookOpen,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Métricas de performance do sistema de recomendação
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stat.value}
                </p>
              </div>
              <div className={`${COLOR_CLASSES[stat.color].bg} rounded-full p-3`}>
                <stat.icon className={`w-6 h-6 ${COLOR_CLASSES[stat.color].text}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg shadow-md p-6"
          >
            <div className="flex items-center space-x-3 mb-3">
              <metric.icon className="w-5 h-5 text-primary-600" />
              <h3 className="font-semibold text-gray-900">{metric.label}</h3>
            </div>
            <p className="text-3xl font-bold text-primary-900">{metric.value}</p>
            <p className="text-sm text-primary-700 mt-1">{metric.description}</p>
          </div>
        ))}
      </div>

      {/* Popular Courses */}
      {popularCourses.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-primary-600" />
            <span>Cursos Mais Populares</span>
          </h2>

          <div className="space-y-4">
            {popularCourses.map((course, idx) => (
              <div
                key={course.curso_id}
                className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-shrink-0 w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900">{course.titulo}</h3>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                    <span className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{course.views} views</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <MousePointer className="w-4 h-4" />
                      <span>{course.clicks} cliques</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <UserCheck className="w-4 h-4 text-green-600" />
                      <span>{course.enrollments} matrículas</span>
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-600">
                    {course.clicks > 0
                      ? ((course.enrollments / course.clicks) * 100).toFixed(0)
                      : 0}
                    %
                  </div>
                  <div className="text-xs text-gray-600">conversão</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">Insights de Performance</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>
              CTR de {(summary.overall_ctr * 100).toFixed(1)}% está{' '}
              {summary.overall_ctr > 0.3 ? 'acima' : 'abaixo'} da média do setor (30%)
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>
              Taxa de matrícula de {(summary.overall_enrollment_rate * 100).toFixed(1)}% indica{' '}
              {summary.overall_enrollment_rate > 0.15 ? 'boa' : 'baixa'} conversão após clique
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600">•</span>
            <span>
              {summary.unique_employees} colaboradores ativos de{' '}
              {summary.unique_employees > 50 ? 'grande' : 'pequeno'} volume de dados
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
