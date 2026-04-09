import { CheckCircle, Circle, Lock, BookOpen, Award, TrendingUp } from 'lucide-react';

interface Course {
  cursoID: string;
  titulo: string;
  categoria: string;
  cargaHoraria: number;
  status?: 'completed' | 'in_progress' | 'locked' | 'available';
}

interface PathStage {
  level: string;
  description: string;
  courses: Course[];
  status: 'completed' | 'in_progress' | 'locked';
  requiredPrevious?: boolean;
}

interface LearningPathProps {
  employeeName: string;
  cargo: string;
  nivel: string;
}

export function LearningPath({ employeeName, cargo, nivel }: LearningPathProps) {
  // Simula trilha de aprendizado baseada no cargo e nível
  // Em produção, isso viria da API
  const path: PathStage[] = [
    {
      level: 'Fundação',
      description: 'Conhecimentos essenciais e obrigatórios',
      status: 'completed',
      courses: [
        {
          cursoID: 'C001',
          titulo: 'Segurança da Informação',
          categoria: 'Compliance',
          cargaHoraria: 4,
          status: 'completed',
        },
        {
          cursoID: 'C002',
          titulo: 'LGPD e Privacidade de Dados',
          categoria: 'Compliance',
          cargaHoraria: 3,
          status: 'completed',
        },
      ],
    },
    {
      level: 'Intermediário',
      description: 'Desenvolvimento de competências técnicas',
      status: 'in_progress',
      courses: [
        {
          cursoID: 'C015',
          titulo: 'Gestão de Projetos Ágeis',
          categoria: 'Gestao',
          cargaHoraria: 16,
          status: 'in_progress',
        },
        {
          cursoID: 'C008',
          titulo: 'Comunicação Assertiva',
          categoria: 'Soft Skills',
          cargaHoraria: 8,
          status: 'available',
        },
      ],
    },
    {
      level: 'Avançado',
      description: 'Especialização e liderança',
      status: 'locked',
      requiredPrevious: true,
      courses: [
        {
          cursoID: 'C010',
          titulo: 'Gestão de Pessoas e Liderança',
          categoria: 'Lideranca',
          cargaHoraria: 16,
          status: 'locked',
        },
        {
          cursoID: 'C014',
          titulo: 'Estratégia e Inovação',
          categoria: 'Negocios',
          cargaHoraria: 20,
          status: 'locked',
        },
      ],
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'in_progress':
        return <Circle className="w-6 h-6 text-blue-600 animate-pulse" />;
      case 'locked':
        return <Lock className="w-6 h-6 text-gray-400" />;
      default:
        return <Circle className="w-6 h-6 text-gray-300" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 border-green-300 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 border-blue-300 text-blue-800';
      case 'locked':
        return 'bg-gray-100 border-gray-300 text-gray-600';
      default:
        return 'bg-white border-gray-300 text-gray-800';
    }
  };

  const totalCourses = path.reduce((sum, stage) => sum + stage.courses.length, 0);
  const completedCourses = path.reduce(
    (sum, stage) =>
      sum + stage.courses.filter((c) => c.status === 'completed').length,
    0
  );
  const progressPercentage = (completedCourses / totalCourses) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">Trilha de Aprendizado</h1>
            <p className="mt-2 text-primary-100">
              {employeeName} • {cargo} • {nivel}
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{completedCourses}/{totalCourses}</div>
            <div className="text-sm text-primary-100">Cursos Concluídos</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span>Progresso Geral</span>
            <span className="font-semibold">{progressPercentage.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-primary-900 bg-opacity-30 rounded-full h-3">
            <div
              className="bg-white h-3 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Learning Path Stages */}
      <div className="space-y-8">
        {path.map((stage, stageIdx) => (
          <div key={stage.level} className="relative">
            {/* Connector Line */}
            {stageIdx < path.length - 1 && (
              <div className="absolute left-8 top-20 bottom-0 w-0.5 bg-gray-300 -mb-8" />
            )}

            {/* Stage Card */}
            <div className={`rounded-lg border-2 ${getStatusColor(stage.status)} p-6`}>
              {/* Stage Header */}
              <div className="flex items-start space-x-4 mb-6">
                <div className="relative z-10 bg-white rounded-full p-2 shadow-md">
                  {getStatusIcon(stage.status)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-2xl font-bold">{stage.level}</h2>
                    {stage.status === 'completed' && (
                      <span className="px-3 py-1 bg-green-600 text-white rounded-full text-xs font-medium flex items-center space-x-1">
                        <Award className="w-3 h-3" />
                        <span>Completo</span>
                      </span>
                    )}
                    {stage.status === 'in_progress' && (
                      <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-xs font-medium flex items-center space-x-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>Em Progresso</span>
                      </span>
                    )}
                  </div>
                  <p className="text-sm mt-1 opacity-80">{stage.description}</p>
                  {stage.requiredPrevious && stage.status === 'locked' && (
                    <p className="text-sm mt-2 flex items-center space-x-1">
                      <Lock className="w-4 h-4" />
                      <span>Complete o nível anterior para desbloquear</span>
                    </p>
                  )}
                </div>
              </div>

              {/* Courses in Stage */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-14">
                {stage.courses.map((course) => (
                  <div
                    key={course.cursoID}
                    className={`bg-white rounded-lg border p-4 ${
                      course.status === 'locked' ? 'opacity-60' : 'hover:shadow-md'
                    } transition-shadow`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {course.status === 'completed' ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : course.status === 'in_progress' ? (
                          <div className="relative">
                            <Circle className="w-5 h-5 text-blue-600" />
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                            </div>
                          </div>
                        ) : course.status === 'locked' ? (
                          <Lock className="w-5 h-5 text-gray-400" />
                        ) : (
                          <BookOpen className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">
                          {course.titulo}
                        </h3>
                        <div className="flex items-center space-x-3 mt-2 text-xs text-gray-600">
                          <span className="px-2 py-0.5 bg-gray-100 rounded">
                            {course.categoria}
                          </span>
                          <span>{course.cargaHoraria}h</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5" />
          <span>Próximos Passos</span>
        </h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">1.</span>
            <span>Complete os cursos em progresso do nível Intermediário</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">2.</span>
            <span>Desbloqueie o nível Avançado finalizando todos os cursos intermediários</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 font-bold">3.</span>
            <span>Foque em cursos de Liderança para preparação ao próximo nível de carreira</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
