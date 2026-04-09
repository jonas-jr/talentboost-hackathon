import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle, BookOpen, TrendingUp, Award } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { talentBoostApi } from '@/services/api';
import type { CompetencyGap, RecommendationResponse } from '@/types';

const PRIORITY_COLORS = {
  critical: 'bg-red-100 text-red-800 border-red-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  low: 'bg-green-100 text-green-800 border-green-300',
};

const PRIORITY_ICONS = {
  critical: '🔴',
  high: '🟠',
  medium: '🟡',
  low: '🟢',
};

export function EmployeeDetail() {
  const { employeeName } = useParams<{ employeeName: string }>();
  const [gaps, setGaps] = useState<CompetencyGap[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'gaps' | 'recommendations'>('gaps');

  useEffect(() => {
    async function loadData() {
      if (!employeeName) return;

      try {
        setLoading(true);
        const [gapsData, recsData] = await Promise.all([
          talentBoostApi.analyzeGaps(employeeName),
          talentBoostApi.getRecommendations(employeeName, 5),
        ]);
        setGaps(gapsData.gaps);
        setRecommendations(recsData);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [employeeName]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!recommendations) {
    return <div className="text-center text-gray-500">Erro ao carregar dados</div>;
  }

  const { profile_summary } = recommendations;

  // Prepara dados para gráfico de gaps
  const gapsChartData = gaps.map((gap) => ({
    name: gap.competency_name.split(' ').slice(0, 3).join(' '),
    nota: gap.average_score,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/employees"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{employeeName}</h1>
            <p className="text-gray-600">
              {profile_summary.cargo} · {profile_summary.nivel}
            </p>
          </div>
        </div>
      </div>

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Nota Média</p>
              <p className="text-2xl font-bold text-gray-900">{profile_summary.nota_media_geral.toFixed(1)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-8 h-8 text-orange-600" />
            <div>
              <p className="text-sm text-gray-600">Gaps</p>
              <p className="text-2xl font-bold text-gray-900">{profile_summary.total_gaps}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-3">
            <Award className="w-8 h-8 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Pontos Fortes</p>
              <p className="text-2xl font-bold text-gray-900">{profile_summary.pontos_fortes.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-3">
            <BookOpen className="w-8 h-8 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Recomendações</p>
              <p className="text-2xl font-bold text-gray-900">{recommendations.recommendations.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pontos Fortes */}
      {profile_summary.pontos_fortes.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center space-x-2 mb-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-green-900">Pontos Fortes</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {profile_summary.pontos_fortes.map((forte) => (
              <span key={forte} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                {forte}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('gaps')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'gaps'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Gaps de Competências
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'recommendations'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Recomendações de Treinamento
          </button>
        </nav>
      </div>

      {/* Tab Content: Gaps */}
      {activeTab === 'gaps' && (
        <div className="space-y-6">
          {/* Gráfico de Gaps */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Notas por Competência</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={gapsChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="nota" fill="#0ea5e9" name="Nota" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Lista de Gaps */}
          <div className="space-y-4">
            {gaps.map((gap, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900">{gap.competency_name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{gap.context}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-2 ml-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${PRIORITY_COLORS[gap.gap_severity]}`}>
                      {PRIORITY_ICONS[gap.gap_severity]} {gap.gap_severity.toUpperCase()}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">{gap.average_score.toFixed(1)}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200">
                  <div>
                    <p className="text-sm text-gray-600">Urgência</p>
                    <p className="text-sm font-medium text-gray-900">{gap.urgency.toUpperCase()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Consenso</p>
                    <p className="text-sm font-medium text-gray-900">{(gap.evaluator_consensus * 100).toFixed(0)}%</p>
                  </div>
                </div>

                {gap.development_hints.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-600 mb-2">Áreas de Desenvolvimento:</p>
                    <div className="flex flex-wrap gap-2">
                      {gap.development_hints.map((hint) => (
                        <span key={hint} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                          {hint}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Content: Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {/* Resumo */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Resumo das Recomendações</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-blue-600">Total</p>
                <p className="text-2xl font-bold text-blue-900">{recommendations.summary.total}</p>
              </div>
              <div>
                <p className="text-blue-600">Relevância Média</p>
                <p className="text-2xl font-bold text-blue-900">
                  {(recommendations.summary.average_relevance * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>

          {/* Lista de Recomendações */}
          <div className="space-y-4">
            {recommendations.recommendations.map((rec, index) => (
              <div key={rec.curso_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                      <h4 className="text-xl font-semibold text-gray-900">{rec.titulo}</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{rec.match_reason}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ml-4 ${PRIORITY_COLORS[rec.priority]}`}>
                    {PRIORITY_ICONS[rec.priority]} {rec.priority.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Categoria</p>
                    <p className="text-sm font-medium text-gray-900">{rec.categoria}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Modalidade</p>
                    <p className="text-sm font-medium text-gray-900">{rec.modalidade}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Carga Horária</p>
                    <p className="text-sm font-medium text-gray-900">{rec.carga_horaria}h</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Relevância</p>
                    <p className="text-sm font-medium text-gray-900">{(rec.relevance_score * 100).toFixed(0)}%</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600 mb-2">Endereça os gaps:</p>
                  <div className="flex flex-wrap gap-2">
                    {rec.addresses_gaps.map((gap) => (
                      <span key={gap} className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm">
                        {gap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
