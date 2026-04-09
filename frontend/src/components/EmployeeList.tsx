import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, User } from 'lucide-react';
import { talentBoostApi } from '@/services/api';
import type { Employee } from '@/types';

export function EmployeeList() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function loadEmployees() {
      try {
        const data = await talentBoostApi.listEmployees();
        setEmployees(data);
        setFilteredEmployees(data);
      } catch (error) {
        console.error('Erro ao carregar colaboradores:', error);
      } finally {
        setLoading(false);
      }
    }
    loadEmployees();
  }, []);

  useEffect(() => {
    const filtered = employees.filter(
      (emp) =>
        emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.cargo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.departamento.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredEmployees(filtered);
  }, [searchTerm, employees]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Barra de busca */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar colaborador por nome, cargo ou departamento..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Grid de colaboradores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEmployees.map((employee) => (
          <Link
            key={employee.name}
            to={`/employees/${encodeURIComponent(employee.name)}`}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start space-x-4">
              <div className="bg-primary-100 rounded-full p-3">
                <User className="w-6 h-6 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 truncate">{employee.name}</h3>
                <p className="text-sm text-gray-600 truncate">{employee.cargo}</p>
                <p className="text-sm text-gray-500 truncate">{employee.departamento}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filteredEmployees.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Nenhum colaborador encontrado</p>
        </div>
      )}
    </div>
  );
}
