import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Filter, ChevronDown, Home, BookOpen, Library, Info, MessageCircle, CheckCircle, PlayCircle } from 'lucide-react';
import { talentBoostApi } from '@/services/api';
import { CourseAssistantChat } from './CourseAssistantChat';
import { useAuth } from '@/contexts/AuthContext';

interface Course {
  cursoID: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  cargaHoraria: number;
  obrigatorio: boolean;
  notaMinima: number;
}

interface Recommendation {
  curso_id: string;
  titulo: string;
  relevance_score: number;
  match_reason: string;
  priority: string;
}

interface Enrollment {
  curso_id: string;
  status: 'completed' | 'in_progress' | 'enrolled';
  progress: number;
  titulo: string;
  categoria: string;
  modalidade: string;
}

interface CategoryFilter {
  name: string;
  count: number;
  checked: boolean;
}

export function CoursesLibrary() {
  const location = useLocation();
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState<'todos' | 'meus'>('todos');
  const [selectedCourseForChat, setSelectedCourseForChat] = useState<Course | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModality, setSelectedModality] = useState<'all' | 'presencial' | 'online'>('all');
  const [sortBy, setSortBy] = useState<'publication' | 'alphabetical'>('publication');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [categories, setCategories] = useState<CategoryFilter[]>([]);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const getActiveTab = () => {
    if (location.pathname.includes('/trilhas')) return 'trilhas';
    if (location.pathname.includes('/biblioteca')) return 'biblioteca';
    return 'cursos';
  };

  const activeTab = getActiveTab();

  useEffect(() => {
    async function loadData() {
      if (!user) return;

      try {
        const [coursesData, recsData, enrollmentsData] = await Promise.all([
          talentBoostApi.listCourses(),
          talentBoostApi.getRecommendations(user.name, 10, true).catch(() => ({ recommendations: [] })),
          talentBoostApi.getEmployeeEnrollments(user.name),
        ]);

        const coursesList: Course[] = coursesData.courses || [];
        setCourses(coursesList);
        setRecommendations(recsData.recommendations || []);
        setEnrollments(enrollmentsData.enrollments || []);

        const categoriesCount = coursesList.reduce<Record<string, number>>((accumulator, course) => {
            accumulator[course.categoria] = (accumulator[course.categoria] || 0) + 1;
            return accumulator;
          }, {});

        const nextCategories: CategoryFilter[] = Object.entries(categoriesCount)
          .sort((left, right) => left[0].localeCompare(right[0]))
          .map(([name, count]) => ({ name, count, checked: false }));

        setCategories((current) =>
          nextCategories.map((category) => ({
            ...category,
            checked: current.find((item) => item.name === category.name)?.checked || false,
          }))
        );
      } catch (error) {
        console.error('Erro ao carregar cursos:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [user]);

  const recommendationMap = useMemo(
    () => new Map(recommendations.map((recommendation) => [recommendation.curso_id, recommendation])),
    [recommendations]
  );

  const enrollmentMap = useMemo(
    () => new Map(enrollments.map((enrollment) => [enrollment.curso_id, enrollment])),
    [enrollments]
  );

  const filteredCourses = useMemo(() => {
    let result = courses.slice();

    if (viewMode === 'meus') {
      result = result.filter((course) => enrollmentMap.has(course.cursoID));
    }

    if (searchTerm) {
      result = result.filter((course) => course.titulo.toLowerCase().includes(searchTerm.toLowerCase()));
    }

    if (selectedModality !== 'all') {
      result = result.filter((course) => course.modalidade.toLowerCase() === selectedModality);
    }

    const selectedCategories = categories.filter((category) => category.checked).map((category) => category.name);
    if (selectedCategories.length > 0) {
      result = result.filter((course) => selectedCategories.includes(course.categoria));
    }

    result.sort((left, right) => {
      const leftRecommendation = recommendationMap.get(left.cursoID);
      const rightRecommendation = recommendationMap.get(right.cursoID);

      if (leftRecommendation && !rightRecommendation) return -1;
      if (!leftRecommendation && rightRecommendation) return 1;
      if (leftRecommendation && rightRecommendation && leftRecommendation.relevance_score !== rightRecommendation.relevance_score) {
        return rightRecommendation.relevance_score - leftRecommendation.relevance_score;
      }

      let compareValue = 0;
      if (sortBy === 'alphabetical') {
        compareValue = left.titulo.localeCompare(right.titulo);
      } else {
        compareValue = Number(left.cursoID.replace(/\D/g, '')) - Number(right.cursoID.replace(/\D/g, ''));
      }

      return sortOrder === 'asc' ? compareValue : compareValue * -1;
    });

    return result;
  }, [categories, courses, enrollmentMap, recommendationMap, searchTerm, selectedModality, sortBy, sortOrder, viewMode]);

  const toggleCategory = (categoryName: string) => {
    setCategories((current) =>
      current.map((category) =>
        category.name === categoryName ? { ...category, checked: !category.checked } : category
      )
    );
  };

  const handleEnroll = async (course: Course) => {
    if (!user) return;

    try {
      setActionLoadingId(course.cursoID);
      await talentBoostApi.enrollInCourse({
        employee_id: user.id,
        employee_name: user.name,
        curso_id: course.cursoID,
        curso_titulo: course.titulo,
      });

      const enrollmentsData = await talentBoostApi.getEmployeeEnrollments(user.name);
      setEnrollments(enrollmentsData.enrollments || []);
      setViewMode('meus');
    } catch (error) {
      console.error('Erro ao matricular no curso:', error);
    } finally {
      setActionLoadingId(null);
    }
  };

  if (!user) return null;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Link
          to="/trilhas"
          className={`flex items-center space-x-2 px-6 py-3 font-semibold transition-colors ${
            activeTab === 'trilhas'
              ? 'bg-white text-gray-900 border-b-4 border-gray-300'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Home className="w-5 h-5" />
          <span>TRILHAS</span>
        </Link>

        <Link
          to="/courses"
          className={`flex items-center space-x-2 px-6 py-3 font-semibold transition-colors ${
            activeTab === 'cursos'
              ? 'bg-primary-600 text-white rounded-lg'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <BookOpen className="w-5 h-5" />
          <span>CURSOS</span>
        </Link>

        <Link
          to="/biblioteca"
          className={`flex items-center space-x-2 px-6 py-3 font-semibold transition-colors ${
            activeTab === 'biblioteca'
              ? 'bg-white text-gray-900 border-b-4 border-gray-300'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Library className="w-5 h-5" />
          <span>BIBLIOTECA</span>
        </Link>
      </div>

      <nav className="flex items-center space-x-2 text-sm text-gray-600">
        <span className="text-primary-600 hover:text-primary-700 cursor-pointer">Início</span>
        <span>/</span>
        <span>Cursos</span>
      </nav>

      <div className="bg-gray-800 text-white rounded-lg p-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="text-white hover:text-gray-300">
            <ChevronDown className="w-6 h-6 rotate-90" />
          </button>
          <h1 className="text-2xl font-bold flex items-center space-x-2">
            <span>Cursos</span>
            <Info className="w-5 h-5 text-gray-400" />
          </h1>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-3 space-y-4">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Filter className="w-5 h-5" />
              <span>Filtros</span>
            </h3>

            <div className="space-y-2">
              {categories.map((category) => (
                <label
                  key={category.name}
                  className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={category.checked}
                    onChange={() => toggleCategory(category.name)}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <div className="flex items-center justify-between flex-1">
                    <span className="text-sm text-gray-700">{category.name}</span>
                    <span className="text-xs text-gray-500">({category.count})</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-9 space-y-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Pesquisar por"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700 transition-colors">
              <Search className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('todos')}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                viewMode === 'todos'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Todos ({courses.length})
            </button>
            <button
              onClick={() => setViewMode('meus')}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                viewMode === 'meus'
                  ? 'bg-gray-700 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Meus Cursos ({enrollments.length})
            </button>
          </div>

          <div className="flex items-center justify-between bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Tipo:</span>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedModality === 'all' || selectedModality === 'presencial'}
                  onChange={() =>
                    setSelectedModality(selectedModality === 'presencial' ? 'all' : 'presencial')
                  }
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Presencial</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedModality === 'all' || selectedModality === 'online'}
                  onChange={() =>
                    setSelectedModality(selectedModality === 'online' ? 'all' : 'online')
                  }
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Online</span>
              </label>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">ordenar por</span>
              <select
                value={sortBy}
                onChange={(event) => setSortBy(event.target.value as 'publication' | 'alphabetical')}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              >
                <option value="publication">Data de Publicação</option>
                <option value="alphabetical">Alfabética</option>
              </select>
              <select
                value={sortOrder}
                onChange={(event) => setSortOrder(event.target.value as 'asc' | 'desc')}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              >
                <option value="desc">Decrescente</option>
                <option value="asc">Crescente</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Exibindo {filteredCourses.length} de {viewMode === 'meus' ? enrollments.length : courses.length} cursos
            </p>
          </div>

          {filteredCourses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course) => {
                const recommendation = recommendationMap.get(course.cursoID);
                const enrollment = enrollmentMap.get(course.cursoID);
                const progress = enrollment?.progress || 0;

                return (
                  <div
                    key={course.cursoID}
                    className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 ${
                      recommendation ? 'ring-2 ring-purple-300 ring-offset-1' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className={`rounded-full p-3 ${recommendation ? 'bg-purple-100' : 'bg-primary-100'}`}>
                        <BookOpen className={`w-6 h-6 ${recommendation ? 'text-purple-600' : 'text-primary-600'}`} />
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        {recommendation && (
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                            Recomendado para você
                          </span>
                        )}
                        {course.obrigatorio && (
                          <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                            Obrigatório
                          </span>
                        )}
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
                      </div>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 min-h-[3.5rem]">
                      {course.titulo}
                    </h3>

                    {recommendation?.match_reason && (
                      <p className="text-xs text-purple-600 mb-3 line-clamp-2">{recommendation.match_reason}</p>
                    )}

                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium">
                        {course.categoria}
                      </span>
                      <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                        {course.modalidade}
                      </span>
                    </div>

                    {enrollment && enrollment.status !== 'completed' && (
                      <div className="mb-4">
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

                    <div className="space-y-2 pt-4 border-t border-gray-200">
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>{course.cargaHoraria}h</span>
                      </div>

                      {!enrollment && (
                        <button
                          onClick={() => handleEnroll(course)}
                          disabled={actionLoadingId === course.cursoID}
                          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {actionLoadingId === course.cursoID ? 'Matriculando...' : 'Matricular-se'}
                        </button>
                      )}

                      {enrollment && enrollment.status !== 'completed' && (
                        <button
                          onClick={() => setSelectedCourseForChat(course)}
                          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                        >
                          Continuar curso
                        </button>
                      )}

                      <button
                        onClick={() => setSelectedCourseForChat(course)}
                        className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
                      >
                        <MessageCircle className="w-4 h-4" />
                        <span>Falar com Tutor Virtual</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum curso encontrado</h3>
              <p className="text-gray-600">Tente ajustar os filtros ou buscar por outros termos</p>
            </div>
          )}
        </div>
      </div>

      {selectedCourseForChat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl h-[90vh] flex flex-col relative">
            <button
              onClick={() => setSelectedCourseForChat(null)}
              className="absolute top-4 right-4 z-10 p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              aria-label="Fechar"
            >
              ✕
            </button>

            <div className="flex-1 overflow-hidden">
              <CourseAssistantChat
                cursoId={selectedCourseForChat.cursoID}
                cursoTitulo={selectedCourseForChat.titulo}
                employeeId={user.id}
                employeeName={user.name}
                progressoCurso={enrollmentMap.get(selectedCourseForChat.cursoID)?.progress || 0}
                moduloAtual="Introdução"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
