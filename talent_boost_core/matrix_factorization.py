"""
Matrix Factorization - Decomposição de matriz para recomendações.

Usa SVD (Singular Value Decomposition) para encontrar padrões latentes
na matriz usuário-curso.

NOTA: Requer sklearn e volume de dados suficiente (~50+ colaboradores com histórico).
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class MatrixFactorizationConfig:
    """Configuração para matrix factorization."""
    n_factors: int = 20  # Número de fatores latentes
    min_interactions: int = 50  # Mínimo de interações para treinar


class MatrixFactorizationRecommender:
    """
    Recomendador baseado em Matrix Factorization (SVD).

    Requer:
    - numpy
    - scikit-learn (sklearn)

    Instalar com: pip install numpy scikit-learn
    """

    def __init__(self, config: MatrixFactorizationConfig | None = None):
        """
        Inicializa o recomendador MF.

        Args:
            config: Configuração de MF
        """
        self.config = config or MatrixFactorizationConfig()
        self.user_factors = None
        self.course_factors = None
        self.user_id_map = {}  # {employee_id: matrix_index}
        self.course_id_map = {}  # {curso_id: matrix_index}
        self.is_trained = False

        try:
            from sklearn.decomposition import TruncatedSVD
            self.svd = TruncatedSVD(n_components=self.config.n_factors, random_state=42)
        except ImportError:
            raise ImportError(
                "Matrix Factorization requer sklearn. "
                "Instale com: pip install scikit-learn"
            )

    def fit(self, interaction_matrix: np.ndarray, employee_ids: list[int], course_ids: list[str]):
        """
        Treina o modelo de matrix factorization.

        Args:
            interaction_matrix: Matriz N x M (usuários x cursos)
                Valores: 0 (não fez), 1 (nota < 7), 2 (nota 7-8), 3 (nota > 8)
            employee_ids: Lista de IDs de colaboradores (corresponde às linhas)
            course_ids: Lista de IDs de cursos (corresponde às colunas)
        """
        if interaction_matrix.shape[0] < self.config.min_interactions:
            raise ValueError(
                f"Dados insuficientes para treinar. "
                f"Mínimo: {self.config.min_interactions}, "
                f"Fornecido: {interaction_matrix.shape[0]}"
            )

        # Cria mapeamentos
        self.user_id_map = {emp_id: idx for idx, emp_id in enumerate(employee_ids)}
        self.course_id_map = {course_id: idx for idx, course_id in enumerate(course_ids)}

        # Decompõe a matriz
        self.user_factors = self.svd.fit_transform(interaction_matrix)
        self.course_factors = self.svd.components_.T

        self.is_trained = True

    def predict_score(self, employee_id: int, curso_id: str) -> float:
        """
        Prediz quão relevante um curso é para um usuário.

        Args:
            employee_id: ID do colaborador
            curso_id: ID do curso

        Returns:
            Score de relevância (0-3)
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado. Chame fit() primeiro.")

        if employee_id not in self.user_id_map:
            return 0.0  # Usuário novo (cold start)

        if curso_id not in self.course_id_map:
            return 0.0  # Curso novo

        user_idx = self.user_id_map[employee_id]
        course_idx = self.course_id_map[curso_id]

        # Produto escalar dos fatores
        score = self.user_factors[user_idx] @ self.course_factors[course_idx]

        return float(np.clip(score, 0, 3))

    def recommend_for_user(
        self,
        employee_id: int,
        top_n: int = 10,
        exclude_courses: set[str] | None = None,
    ) -> list[tuple[str, float]]:
        """
        Recomenda cursos para um usuário.

        Args:
            employee_id: ID do colaborador
            top_n: Número de recomendações
            exclude_courses: Cursos a excluir (já feitos)

        Returns:
            Lista de (curso_id, score) ordenada por relevância
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado. Chame fit() primeiro.")

        if employee_id not in self.user_id_map:
            return []  # Cold start

        exclude_courses = exclude_courses or set()
        user_idx = self.user_id_map[employee_id]

        # Calcula scores para todos os cursos
        recommendations = []
        for curso_id, course_idx in self.course_id_map.items():
            if curso_id in exclude_courses:
                continue

            score = self.user_factors[user_idx] @ self.course_factors[course_idx]
            recommendations.append((curso_id, float(score)))

        # Ordena por score
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:top_n]

    @staticmethod
    def build_interaction_matrix_from_data(
        employees_data: list[dict],
        all_courses: list[dict],
    ) -> tuple[np.ndarray, list[int], list[str]]:
        """
        Constrói matriz de interação a partir de dados brutos.

        Args:
            employees_data: Lista de colaboradores com training_history
            all_courses: Lista de todos os cursos disponíveis

        Returns:
            (interaction_matrix, employee_ids, course_ids)
        """
        # Cria mapeamentos
        employee_ids = [emp["colaborador_id"] for emp in employees_data]
        course_ids = [course["cursoID"] for course in all_courses]

        n_users = len(employee_ids)
        n_courses = len(course_ids)

        user_idx_map = {emp_id: idx for idx, emp_id in enumerate(employee_ids)}
        course_idx_map = {course_id: idx for idx, course_id in enumerate(course_ids)}

        # Inicializa matriz com zeros
        matrix = np.zeros((n_users, n_courses))

        # Preenche matriz baseado no histórico
        for emp in employees_data:
            emp_id = emp["colaborador_id"]
            user_idx = user_idx_map[emp_id]

            training_history = emp.get("training_history", {})
            recent_courses = training_history.get("recent_courses", [])

            for course in recent_courses:
                curso_id = course.get("cursoID")
                if curso_id not in course_idx_map:
                    continue

                course_idx = course_idx_map[curso_id]
                nota = course.get("nota", 0)
                status = course.get("status", "")

                # Mapeia nota para valor discreto
                if status != "Concluído":
                    value = 0  # Não completou
                elif nota < 7:
                    value = 1  # Completou mas nota baixa
                elif nota < 8.5:
                    value = 2  # Nota boa
                else:
                    value = 3  # Nota excelente

                matrix[user_idx, course_idx] = value

        return matrix, employee_ids, course_ids


# Exemplo de uso (comentado - requer dados reais):
"""
# 1. Constrói matriz de interação
interaction_matrix, employee_ids, course_ids = (
    MatrixFactorizationRecommender.build_interaction_matrix_from_data(
        employees_data=all_employees,
        all_courses=available_courses,
    )
)

# 2. Treina o modelo
mf_recommender = MatrixFactorizationRecommender()
try:
    mf_recommender.fit(interaction_matrix, employee_ids, course_ids)
    print("✓ Modelo MF treinado com sucesso!")
except ValueError as e:
    print(f"✗ Não foi possível treinar MF: {e}")

# 3. Faz recomendações
if mf_recommender.is_trained:
    recommendations = mf_recommender.recommend_for_user(
        employee_id=123,
        top_n=5,
        exclude_courses={"C001", "C002"}  # Já fez esses
    )
    for curso_id, score in recommendations:
        print(f"Curso {curso_id}: {score:.2f}")
"""
