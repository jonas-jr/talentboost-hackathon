import { useEffect, useMemo, useState } from 'react';
import { BookOpen, Clock, CheckCircle, PlayCircle, Award, MessageCircle, TrendingUp } from 'lucide-react';
import { talentBoostApi } from '@/services/api';
import { CourseAssistantChat } from './CourseAssistantChat';
import { useAuth } from '@/contexts/AuthContext';

interface Course {
  cursoID?: string;
  curso_id?: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  cargaHoraria?: number;
  carga_horaria?: number;
  obrigatorio?: boolean;
  notaMinima?: number;
  match_reason?: string;
  relevance_score?: number;
}

interface Enrollment {
  curso_id: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  status: 'completed' | 'in_progress' | 'enrolled';
  progress: number;
  nota?: number;
  data_matricula: string;
  data_conclusao?: string | null;
}

interface Recommendation extends Course {
  curso_id: string;
  relevance_score: number;
  match_reason: string;
  priority: string;
  addresses_gaps: string[];
}

export function MyCourses() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'recommended' | 'in_progress' | 'completed'>('recommended');
  const [courses, setCourses] = useState<Course[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [certificateCourse, setCertificateCourse] = useState<{ course: Course; enrollment: Enrollment } | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  if (!user) return null;

  useEffect(() => {
    async function loadData() {
      const currentUser = user;
      if (!currentUser) return;

      try {
        const [coursesData, recsData, enrollmentsData] = await Promise.all([
          talentBoostApi.listCourses(),
          talentBoostApi.getRecommendations(currentUser.name, 10, true),
          talentBoostApi.getEmployeeEnrollments(currentUser.name),
        ]);

        setCourses(coursesData.courses || []);
        setRecommendations(recsData.recommendations || []);
        setEnrollments(enrollmentsData.enrollments || []);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [user?.name]);

  const courseMap = useMemo(
    () =>
      new Map(
        courses.map((course) => [
          course.cursoID || course.curso_id || '',
          course,
        ])
      ),
    [courses]
  );

  const getCourseId = (course: Course) => course.cursoID || course.curso_id || '';

  const getEnrollmentStatus = (cursoId: string) => {
    return enrollments.find((enrollment) => enrollment.curso_id === cursoId);
  };

  const averageScore = useMemo(() => {
    const ratedEnrollments = enrollments.filter((enrollment) => typeof enrollment.nota === 'number');
    if (ratedEnrollments.length === 0) return null;
    const total = ratedEnrollments.reduce((sum, enrollment) => sum + (enrollment.nota || 0), 0);
    return (total / ratedEnrollments.length).toFixed(1);
  }, [enrollments]);

  const mergedRecommendedCourses = useMemo(() => {
    return recommendations
      .map((recommendation) => {
        const linkedCourse = courseMap.get(recommendation.curso_id);
        return {
          ...(linkedCourse || {
            cursoID: recommendation.curso_id,
            titulo: recommendation.titulo,
            categoria: recommendation.categoria,
            modalidade: recommendation.modalidade,
            cargaHoraria: recommendation.carga_horaria,
            obrigatorio: recommendation.obrigatorio,
          }),
          ...recommendation,
        };
      })
      .filter((course) => {
        const enrollment = getEnrollmentStatus(course.curso_id || course.cursoID || '');
        return !enrollment || enrollment.status === 'enrolled';
      });
  }, [recommendations, courseMap, enrollments]);

  const getCoursesForTab = () => {
    switch (activeTab) {
      case 'recommended':
        return mergedRecommendedCourses;
      case 'in_progress':
        return enrollments
          .filter((enrollment) => enrollment.status === 'in_progress' || enrollment.status === 'enrolled')
          .map((enrollment) => ({
            ...(courseMap.get(enrollment.curso_id) || {}),
            ...enrollment,
            cursoID: enrollment.curso_id,
          }));
      case 'completed':
        return enrollments
          .filter((enrollment) => enrollment.status === 'completed')
          .map((enrollment) => ({
            ...(courseMap.get(enrollment.curso_id) || {}),
            ...enrollment,
            cursoID: enrollment.curso_id,
          }));
      default:
        return [];
    }
  };

  const filteredCourses = getCoursesForTab();

  const handleEnroll = async (course: Course) => {
    const courseId = getCourseId(course);
    if (!courseId) return;

    try {
      setActionLoadingId(courseId);
      await talentBoostApi.enrollInCourse({
        employee_id: user.id,
        employee_name: user.name,
        curso_id: courseId,
        curso_titulo: course.titulo,
      });

      const enrollmentsData = await talentBoostApi.getEmployeeEnrollments(user.name);
      setEnrollments(enrollmentsData.enrollments || []);
      setActiveTab('in_progress');
    } catch (error) {
      console.error('Erro ao matricular no curso:', error);
    } finally {
      setActionLoadingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Meus Cursos</h1>
        <p className="text-gray-600 mt-1">
          Olá, {user.name}! Acompanhe seu progresso de aprendizado.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-4">Seu Progresso</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Concluídos</p>
                <p className="text-2xl font-bold text-blue-900">
                  {enrollments.filter((enrollment) => enrollment.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="w-10 h-10 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Em Andamento</p>
                <p className="text-2xl font-bold text-blue-900">
                  {enrollments.filter((enrollment) => enrollment.status !== 'completed').length}
                </p>
              </div>
              <PlayCircle className="w-10 h-10 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Recomendados</p>
                <p className="text-2xl font-bold text-blue-900">{mergedRecommendedCourses.length}</p>
              </div>
              <TrendingUp className="w-10 h-10 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Nota Média</p>
                <p className="text-2xl font-bold text-blue-900">{averageScore || '--'}</p>
              </div>
              <Award className="w-10 h-10 text-blue-600 opacity-20" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('recommended')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'recommended'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Recomendados para Você
              <span className="ml-2 bg-primary-100 text-primary-800 py-0.5 px-2 rounded-full text-xs">
                {mergedRecommendedCourses.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('in_progress')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'in_progress'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Em Andamento
              <span className="ml-2 bg-blue-100 text-blue-800 py-0.5 px-2 rounded-full text-xs">
                {enrollments.filter((enrollment) => enrollment.status !== 'completed').length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('completed')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'completed'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Concluídos
              <span className="ml-2 bg-green-100 text-green-800 py-0.5 px-2 rounded-full text-xs">
                {enrollments.filter((enrollment) => enrollment.status === 'completed').length}
              </span>
            </button>
          </nav>
        </div>

        <div className="p-6">
          {filteredCourses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course) => {
                const courseId = getCourseId(course);
                const enrollment = getEnrollmentStatus(courseId);
                const isRecommended = activeTab === 'recommended';
                const progress = enrollment?.progress || 0;

                return (
                  <div
                    key={courseId}
                    className="bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow p-6"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="bg-primary-100 rounded-full p-3">
                        <BookOpen className="w-6 h-6 text-primary-600" />
                      </div>
                      {enrollment?.status === 'completed' && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium flex items-center space-x-1">
                          <CheckCircle className="w-3 h-3" />
                          <span>Concluído</span>
                        </span>
                      )}
                      {enrollment && enrollment.status !== 'completed' && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium flex items-center space-x-1">
                          <PlayCircle className="w-3 h-3" />
                          <span>{progress}%</span>
                        </span>
                      )}
                      {isRecommended && !enrollment && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                          Recomendado
                        </span>
                      )}
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 min-h-[3.5rem]">
                      {course.titulo}
                    </h3>

                    {isRecommended && course.match_reason && (
                      <p className="text-sm text-purple-600 mb-3 line-clamp-2">{course.match_reason}</p>
                    )}

                    {enrollment && enrollment.status !== 'completed' && (
                      <div className="mb-3">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>Progresso</span>
                          <span>{progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {enrollment?.status === 'completed' && typeof enrollment.nota === 'number' && (
                      <div className="mb-3 flex items-center space-x-2">
                        <Award className="w-4 h-4 text-yellow-600" />
                        <span className="text-sm font-semibold text-gray-900">
                          Nota: {enrollment.nota.toFixed(1)}/10
                        </span>
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium">
                        {course.categoria}
                      </span>
                      <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                        {course.modalidade}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{course.cargaHoraria || course.carga_horaria || 0}h</span>
                      </span>
                    </div>

                    <div className="space-y-2">
                      {enrollment && enrollment.status !== 'completed' && (
                        <>
                          <button
                            onClick={() => setSelectedCourse(course)}
                            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                          >
                            Continuar Curso
                          </button>
                          <button
                            onClick={() => setSelectedCourse(course)}
                            className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
                          >
                            <MessageCircle className="w-4 h-4" />
                            <span>Tutor Virtual</span>
                          </button>
                        </>
                      )}

                      {!enrollment && (
                        <button
                          onClick={() => handleEnroll(course)}
                          disabled={actionLoadingId === courseId}
                          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {actionLoadingId === courseId ? 'Matriculando...' : 'Matricular-se'}
                        </button>
                      )}

                      {enrollment?.status === 'completed' && (
                        <button
                          onClick={() => setCertificateCourse({ course, enrollment })}
                          className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          Ver Certificado
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum curso encontrado</h3>
              <p className="text-gray-600">
                {activeTab === 'recommended' && 'As recomendações disponíveis já foram convertidas em cursos ativos.'}
                {activeTab === 'in_progress' && 'Você não tem cursos em andamento no momento.'}
                {activeTab === 'completed' && 'Você ainda não concluiu nenhum curso.'}
              </p>
            </div>
          )}
        </div>
      </div>

      {selectedCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col relative">
            <button
              onClick={() => setSelectedCourse(null)}
              className="absolute top-4 right-4 z-10 p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            >
              ✕
            </button>

            <div className="flex-1 overflow-hidden">
              <CourseAssistantChat
                cursoId={getCourseId(selectedCourse)}
                cursoTitulo={selectedCourse.titulo}
                employeeId={user.id}
                employeeName={user.name}
                progressoCurso={getEnrollmentStatus(getCourseId(selectedCourse))?.progress || 0}
                moduloAtual="Módulo atual"
              />
            </div>
          </div>
        </div>
      )}

      {certificateCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 relative">
            <button
              onClick={() => setCertificateCourse(null)}
              className="absolute top-4 right-4 p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              aria-label="Fechar certificado"
            >
              ✕
            </button>

            <div className="border-4 border-primary-100 rounded-2xl p-8 text-center bg-gradient-to-br from-white to-blue-50">
              <p className="text-sm uppercase tracking-[0.3em] text-primary-600 font-semibold mb-3">
                Certificado de Conclusão
              </p>
              <h3 className="text-3xl font-bold text-gray-900 mb-4">{certificateCourse.course.titulo}</h3>
              <p className="text-gray-600 mb-6">
                Certificamos que <span className="font-semibold text-gray-900">{user.name}</span> concluiu este curso
                com aproveitamento de <span className="font-semibold text-gray-900">{certificateCourse.enrollment.nota?.toFixed(1) || 'N/A'}/10</span>.
              </p>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 max-w-md mx-auto">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Categoria</p>
                  <p className="font-semibold text-gray-900">{certificateCourse.course.categoria}</p>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Conclusão</p>
                  <p className="font-semibold text-gray-900">
                    {certificateCourse.enrollment.data_conclusao || certificateCourse.enrollment.data_matricula}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
