import { X, Check, Clock, Award, BookOpen } from 'lucide-react';

interface Course {
  cursoID: string;
  titulo: string;
  categoria: string;
  modalidade: string;
  cargaHoraria: number;
  obrigatorio: boolean;
  notaMinima?: number;
  relevance_score?: number;
  addresses_gaps?: string[];
}

interface CourseComparisonProps {
  courses: Course[];
  onClose: () => void;
}

export function CourseComparison({ courses, onClose }: CourseComparisonProps) {
  if (courses.length === 0) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Comparação de Cursos
            </h2>
            <p className="text-gray-600 mt-1">
              Comparando {courses.length} {courses.length === 1 ? 'curso' : 'cursos'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Comparison Table */}
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700 w-40">
                    Característica
                  </th>
                  {courses.map((course) => (
                    <th key={course.cursoID} className="text-left p-4 w-64">
                      <div className="flex items-start space-x-2">
                        <BookOpen className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="font-semibold text-gray-900 line-clamp-2">
                            {course.titulo}
                          </div>
                          {course.obrigatorio && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mt-1">
                              <Award className="w-3 h-3 mr-1" />
                              Obrigatório
                            </span>
                          )}
                        </div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-200">
                {/* Categoria */}
                <tr className="hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-700">Categoria</td>
                  {courses.map((course) => (
                    <td key={course.cursoID} className="p-4">
                      <span className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm font-medium">
                        {course.categoria}
                      </span>
                    </td>
                  ))}
                </tr>

                {/* Modalidade */}
                <tr className="hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-700">Modalidade</td>
                  {courses.map((course) => (
                    <td key={course.cursoID} className="p-4">
                      <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                        {course.modalidade}
                      </span>
                    </td>
                  ))}
                </tr>

                {/* Carga Horária */}
                <tr className="hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-700">
                    Carga Horária
                  </td>
                  {courses.map((course) => (
                    <td key={course.cursoID} className="p-4">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="font-semibold text-gray-900">
                          {course.cargaHoraria}h
                        </span>
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Nota Mínima */}
                {courses.some((c) => c.notaMinima !== undefined) && (
                  <tr className="hover:bg-gray-50">
                    <td className="p-4 font-medium text-gray-700">
                      Nota Mínima
                    </td>
                    {courses.map((course) => (
                      <td key={course.cursoID} className="p-4">
                        <span className="font-semibold text-gray-900">
                          {course.notaMinima || 'N/A'}
                        </span>
                      </td>
                    ))}
                  </tr>
                )}

                {/* Relevância (se houver) */}
                {courses.some((c) => c.relevance_score !== undefined) && (
                  <tr className="hover:bg-gray-50">
                    <td className="p-4 font-medium text-gray-700">
                      Relevância
                    </td>
                    {courses.map((course) => (
                      <td key={course.cursoID} className="p-4">
                        {course.relevance_score !== undefined ? (
                          <div className="flex items-center space-x-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-primary-600 h-2 rounded-full"
                                style={{
                                  width: `${course.relevance_score * 100}%`,
                                }}
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                              {(course.relevance_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        ) : (
                          <span className="text-gray-500">N/A</span>
                        )}
                      </td>
                    ))}
                  </tr>
                )}

                {/* Competências Endereçadas */}
                {courses.some((c) => c.addresses_gaps && c.addresses_gaps.length > 0) && (
                  <tr className="hover:bg-gray-50">
                    <td className="p-4 font-medium text-gray-700">
                      Competências
                    </td>
                    {courses.map((course) => (
                      <td key={course.cursoID} className="p-4">
                        {course.addresses_gaps && course.addresses_gaps.length > 0 ? (
                          <div className="space-y-1">
                            {course.addresses_gaps.map((gap, idx) => (
                              <div
                                key={idx}
                                className="flex items-center space-x-1 text-sm"
                              >
                                <Check className="w-4 h-4 text-green-600" />
                                <span className="text-gray-700">{gap}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </td>
                    ))}
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Fechar Comparação
          </button>
        </div>
      </div>
    </div>
  );
}
