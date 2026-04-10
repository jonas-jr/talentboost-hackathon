"""
Course Assistant - Tutor Virtual com LLM para auxiliar alunos durante o curso.

Fornece suporte contextual em tempo real baseado no conteúdo do curso.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class CourseContext:
    """Contexto do curso para a LLM."""
    curso_id: str
    titulo: str
    categoria: str
    modalidade: str
    carga_horaria: int
    descricao: str | None = None
    objetivos: list[str] | None = None
    topicos: list[str] | None = None
    nivel: Literal["Básico", "Intermediário", "Avançado"] = "Intermediário"
    prerequisitos: list[str] | None = None


@dataclass
class StudentContext:
    """Contexto do aluno para personalização."""
    employee_id: int
    nome: str
    cargo: str
    nivel: Literal["Junior", "Pleno", "Senior", "Especialista"]
    progresso_curso: float  # 0-100%
    modulo_atual: str | None = None
    dificuldades_reportadas: list[str] | None = None


@dataclass
class AssistantMessage:
    """Mensagem do chat com o assistant."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str
    metadata: dict | None = None


class CourseAssistant:
    """
    Assistente Virtual baseado em LLM para suporte durante o curso.

    Funcionalidades:
    1. Responde dúvidas sobre o conteúdo do curso
    2. Explica conceitos de forma adaptada ao nível do aluno
    3. Sugere materiais complementares
    4. Oferece exercícios práticos
    5. Identifica dificuldades e ajusta abordagem
    """

    def __init__(self, llm_provider=None):
        """
        Inicializa o Course Assistant.

        Args:
            llm_provider: Provedor de LLM (OpenAI, Azure, etc.)
                         Se None, usa modo simulado
        """
        self.llm_provider = llm_provider
        self.conversation_history = {}  # {session_id: [messages]}

    def start_session(
        self,
        session_id: str,
        course_context: CourseContext,
        student_context: StudentContext,
    ) -> AssistantMessage:
        """
        Inicia uma sessão de assistência para um curso.

        Args:
            session_id: ID único da sessão
            course_context: Contexto do curso
            student_context: Contexto do aluno

        Returns:
            Mensagem de boas-vindas personalizada
        """
        # Inicializa histórico da sessão
        self.conversation_history[session_id] = []

        # Cria system prompt personalizado
        system_prompt = self._build_system_prompt(course_context, student_context)

        system_msg = AssistantMessage(
            role="system",
            content=system_prompt,
            timestamp=datetime.now().isoformat(),
            metadata={
                "curso_id": course_context.curso_id,
                "employee_id": student_context.employee_id,
            },
        )
        self.conversation_history[session_id].append(system_msg)

        # Mensagem de boas-vindas
        welcome = self._generate_welcome_message(course_context, student_context)

        assistant_msg = AssistantMessage(
            role="assistant",
            content=welcome,
            timestamp=datetime.now().isoformat(),
        )
        self.conversation_history[session_id].append(assistant_msg)

        return assistant_msg

    def ask(
        self,
        session_id: str,
        question: str,
        course_context: CourseContext,
        student_context: StudentContext,
    ) -> AssistantMessage:
        """
        Processa uma pergunta do aluno.

        Args:
            session_id: ID da sessão
            question: Pergunta do aluno
            course_context: Contexto do curso
            student_context: Contexto do aluno

        Returns:
            Resposta do assistente
        """
        # Adiciona pergunta ao histórico
        user_msg = AssistantMessage(
            role="user",
            content=question,
            timestamp=datetime.now().isoformat(),
        )

        if session_id not in self.conversation_history:
            # Se sessão não existe, cria
            self.start_session(session_id, course_context, student_context)

        self.conversation_history[session_id].append(user_msg)

        # Gera resposta
        if self.llm_provider:
            response = self._generate_llm_response(
                session_id, question, course_context, student_context
            )
        else:
            response = self._generate_simulated_response(
                question, course_context, student_context
            )

        assistant_msg = AssistantMessage(
            role="assistant",
            content=response,
            timestamp=datetime.now().isoformat(),
            metadata={
                "question_type": self._classify_question(question),
                "curso_id": course_context.curso_id,
            },
        )

        self.conversation_history[session_id].append(assistant_msg)

        return assistant_msg

    def get_conversation_history(self, session_id: str) -> list[AssistantMessage]:
        """Retorna histórico da conversa."""
        return self.conversation_history.get(session_id, [])

    def suggest_next_steps(
        self,
        course_context: CourseContext,
        student_context: StudentContext,
    ) -> list[str]:
        """
        Sugere próximos passos baseado no progresso do aluno.

        Returns:
            Lista de sugestões personalizadas
        """
        suggestions = []

        # Baseado no progresso
        if student_context.progresso_curso < 25:
            suggestions.append(
                f"Continue com o módulo '{student_context.modulo_atual or 'inicial'}' - você está no começo!"
            )
        elif student_context.progresso_curso < 50:
            suggestions.append(
                "Você já está na metade! Que tal revisar os conceitos principais antes de continuar?"
            )
        elif student_context.progresso_curso < 75:
            suggestions.append(
                "Está quase lá! Pratique com exercícios para fixar o conteúdo."
            )
        else:
            suggestions.append(
                "Você está quase finalizando! Prepare-se para a avaliação final."
            )

        # Baseado em dificuldades
        if student_context.dificuldades_reportadas:
            suggestions.append(
                f"Revisão recomendada: {', '.join(student_context.dificuldades_reportadas[:2])}"
            )

        # Baseado no nível
        if student_context.nivel == "Junior":
            suggestions.append(
                "Lembre-se: não tenha pressa. É melhor entender bem cada conceito."
            )
        elif student_context.nivel == "Senior":
            suggestions.append(
                "Aproveite para explorar casos avançados e aplicações práticas do conteúdo."
            )

        return suggestions

    def _build_system_prompt(
        self, course: CourseContext, student: StudentContext
    ) -> str:
        """Constrói o system prompt personalizado."""
        is_general = course.curso_id == "general"

        if is_general:
            prompt = f"""Você é um assistente virtual de desenvolvimento profissional da plataforma TalentBoost.
Você ajuda colaboradores com dúvidas sobre treinamentos, recomendações de cursos, desenvolvimento de carreira e competências profissionais.

CONTEXTO DO COLABORADOR:
- Nome: {student.nome}
- Cargo: {student.cargo}
- Nível Profissional: {student.nivel}

DIRETRIZES:
- Responda perguntas sobre desenvolvimento profissional, cursos disponíveis e competências
- Se perguntarem sobre cursos específicos, recomende buscar na aba "Explorar Catálogo" ou "Meus Cursos"
- Se perguntarem sobre equipe ou gestão, explique que essas informações estão no "Dashboard do Gestor"
- Seja útil, conciso e profissional
- Use linguagem simples e direta
"""
        else:
            prompt = f"""Você é um tutor virtual especializado que auxilia alunos durante cursos online.

CONTEXTO DO CURSO:
- Título: {course.titulo}
- Categoria: {course.categoria}
- Nível: {course.nivel}
- Carga Horária: {course.carga_horaria}h
- Modalidade: {course.modalidade}

CONTEXTO DO ALUNO:
- Nome: {student.nome}
- Cargo: {student.cargo}
- Nível Profissional: {student.nivel}
- Progresso no Curso: {student.progresso_curso:.0f}%
"""

        if course.objetivos:
            prompt += f"\nOBJETIVOS DO CURSO:\n"
            for obj in course.objetivos:
                prompt += f"- {obj}\n"

        if course.topicos:
            prompt += f"\nTÓPICOS PRINCIPAIS:\n"
            for topic in course.topicos:
                prompt += f"- {topic}\n"

        prompt += """
SUA MISSÃO:
1. Responder dúvidas de forma clara e adaptada ao nível do aluno
2. Explicar conceitos usando exemplos práticos do dia a dia profissional
3. Encorajar o aluno e celebrar seu progresso
4. Identificar dificuldades e sugerir materiais complementares
5. Ser paciente e empático

DIRETRIZES:
- Use linguagem simples e direta
- Evite jargões técnicos excessivos (ou explique-os)
- Dê exemplos práticos relacionados ao cargo do aluno
- Seja conciso mas completo
- Sempre que possível, conecte o conteúdo com a prática profissional

Lembre-se: seu objetivo é fazer o aluno ENTENDER, não apenas memorizar.
"""

        return prompt

    def _generate_welcome_message(
        self, course: CourseContext, student: StudentContext
    ) -> str:
        """Gera mensagem de boas-vindas personalizada."""
        is_general = course.curso_id == "general"

        if is_general:
            return f"""Olá, {student.nome}! 👋

Sou o assistente virtual do **TalentBoost**.

Posso te ajudar com:
• Dúvidas sobre treinamentos e cursos disponíveis
• Recomendações de desenvolvimento profissional
• Informações sobre competências e carreira
• Orientações sobre a plataforma

Como posso te ajudar hoje?
"""
        return f"""Olá, {student.nome}! 👋

Sou seu tutor virtual para o curso **{course.titulo}**.

Vejo que você é {student.cargo} com nível {student.nivel} - vou adaptar minhas explicações ao seu contexto profissional.

Você está com {student.progresso_curso:.0f}% do curso concluído.

**Como posso te ajudar?**

Você pode me perguntar sobre:
• Conceitos e termos do curso
• Exemplos práticos de aplicação
• Dúvidas sobre exercícios
• Sugestões de materiais complementares

Estou aqui para te ajudar! 🚀
"""

    def _generate_llm_response(
        self,
        session_id: str,
        question: str,
        course: CourseContext,
        student: StudentContext,
    ) -> str:
        """Gera resposta usando LLM real."""
        # Pega histórico da conversa
        history = self.conversation_history[session_id]

        # Prepara mensagens para a LLM
        messages = []
        for msg in history:
            if msg.role in ["system", "user", "assistant"]:
                messages.append({"role": msg.role, "content": msg.content})

        # Chama LLM
        try:
            response = self.llm_provider.invoke(messages)
            return response.content
        except Exception as e:
            return self._generate_fallback_response(question, course, student)

    def _generate_simulated_response(
        self, question: str, course: CourseContext, student: StudentContext
    ) -> str:
        """Gera resposta simulada (sem LLM)."""
        question_lower = question.lower()

        # Respostas baseadas em padrões
        if any(kw in question_lower for kw in ["o que é", "o que significa", "defin"]):
            return f"""Ótima pergunta! Vou explicar de forma prática.

No contexto de **{course.categoria}**, esse conceito é fundamental para {student.cargo}s como você.

[Aqui entraria a explicação detalhada do conceito usando a LLM real]

**Exemplo prático no seu dia a dia:**
Como {student.cargo}, você provavelmente já se deparou com situações onde isso se aplica...

Isso ficou claro? Posso detalhar algum ponto específico?
"""

        elif any(kw in question_lower for kw in ["como", "fazer", "aplicar"]):
            return f"""Excelente! Vamos para a prática. 💪

Para aplicar isso no seu contexto como {student.cargo}:

**Passo 1:** [Explicação do primeiro passo]
**Passo 2:** [Explicação do segundo passo]
**Passo 3:** [Explicação do terceiro passo]

**Dica profissional:**
Na sua área ({course.categoria}), a melhor prática é...

Quer que eu elabore algum desses passos?
"""

        elif any(kw in question_lower for kw in ["dúvida", "não entendi", "confuso"]):
            return f"""Sem problemas! Vamos simplificar isso. 😊

Deixa eu explicar de outra forma, mais voltada para {student.cargo}:

[Aqui entraria uma explicação mais simples e prática]

Pensa assim: [analogia ou exemplo do dia a dia]

Melhorou? Se ainda estiver confuso, podemos tentar outro ângulo!
"""

        elif any(kw in question_lower for kw in ["exercício", "prática", "exemplo"]):
            return f"""Boa iniciativa! A prática é essencial. 🎯

Vou sugerir um exercício prático relacionado ao conteúdo de **{course.titulo}**:

**Exercício:**
[Descrição do exercício adaptado ao nível {student.nivel}]

**Objetivo:** Fixar o conceito na prática
**Tempo estimado:** 15-20 minutos

Tente fazer e depois me conta como foi! Se tiver dificuldade em algum ponto, estou aqui para ajudar.
"""

        else:
            # Resposta genérica
            return f"""Entendo sua dúvida sobre o conteúdo de **{course.titulo}**.

Como {student.cargo} com nível {student.nivel}, acredito que esse ponto é importante para você.

[Aqui entraria a resposta contextualizada usando a LLM real]

Isso responde sua pergunta? Posso aprofundar em algum aspecto específico?
"""

    def _generate_fallback_response(
        self, question: str, course: CourseContext, student: StudentContext
    ) -> str:
        """Resposta de fallback em caso de erro."""
        return f"""Desculpe, tive um problema técnico ao processar sua pergunta.

Mas não se preocupe! Aqui estão algumas alternativas:

1. **Consulte o material do curso** - seção relevante: {course.topicos[0] if course.topicos else 'material principal'}
2. **Fórum de discussão** - outros alunos podem ter a mesma dúvida
3. **Tente reformular** - às vezes uma pergunta diferente me ajuda a entender melhor

Ou simplesmente tente perguntar novamente de outra forma!
"""

    def _classify_question(self, question: str) -> str:
        """Classifica o tipo de pergunta."""
        question_lower = question.lower()

        if any(kw in question_lower for kw in ["o que é", "o que significa", "defin"]):
            return "definition"
        elif any(kw in question_lower for kw in ["como", "fazer", "aplicar"]):
            return "how_to"
        elif any(kw in question_lower for kw in ["por que", "motivo", "razão"]):
            return "why"
        elif any(kw in question_lower for kw in ["exemplo", "prática", "exercício"]):
            return "example"
        elif any(kw in question_lower for kw in ["dúvida", "não entendi", "confuso"]):
            return "clarification"
        else:
            return "general"


# Exemplo de uso
"""
from course_assistant import CourseAssistant, CourseContext, StudentContext

# Inicializa
assistant = CourseAssistant(llm_provider=your_llm)

# Contexto do curso
course = CourseContext(
    curso_id="C008",
    titulo="Comunicação Assertiva",
    categoria="Soft Skills",
    modalidade="EAD",
    carga_horaria=8,
    nivel="Intermediário",
    objetivos=[
        "Desenvolver habilidades de comunicação clara",
        "Aprender técnicas de feedback construtivo",
        "Melhorar comunicação em equipe"
    ],
    topicos=[
        "Fundamentos da comunicação assertiva",
        "Técnicas de escuta ativa",
        "Feedback construtivo",
        "Comunicação não-violenta"
    ]
)

# Contexto do aluno
student = StudentContext(
    employee_id=123,
    nome="Ana Paula",
    cargo="Desenvolvedora Backend",
    nivel="Junior",
    progresso_curso=45.0,
    modulo_atual="Técnicas de escuta ativa"
)

# Inicia sessão
welcome = assistant.start_session("session-001", course, student)
print(welcome.content)

# Aluno faz pergunta
response = assistant.ask(
    "session-001",
    "O que é comunicação assertiva?",
    course,
    student
)
print(response.content)

# Outra pergunta
response = assistant.ask(
    "session-001",
    "Como posso aplicar isso no meu dia a dia?",
    course,
    student
)
print(response.content)

# Sugestões de próximos passos
suggestions = assistant.suggest_next_steps(course, student)
for suggestion in suggestions:
    print(f"• {suggestion}")
"""
