import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, Lightbulb, BookOpen, MessageCircle } from 'lucide-react';
import { talentBoostApi } from '@/services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface CourseAssistantChatProps {
  cursoId: string;
  cursoTitulo: string;
  employeeId: number;
  employeeName: string;
  progressoCurso: number;
  moduloAtual?: string;
}

export function CourseAssistantChat({
  cursoId,
  cursoTitulo,
  employeeId,
  employeeName,
  progressoCurso,
  moduloAtual,
}: CourseAssistantChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll para última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Inicia sessão e carrega sugestões
  useEffect(() => {
    async function initSession() {
      try {
        const response = await talentBoostApi.startCourseAssistant({
          session_id: sessionId,
          curso_id: cursoId,
          employee_id: employeeId,
          employee_name: employeeName,
          progresso_curso: progressoCurso,
          modulo_atual: moduloAtual,
        });

        setMessages([
          {
            role: 'assistant',
            content: response.message.content,
            timestamp: response.message.timestamp,
          },
        ]);

        // Carrega sugestões
        const suggestionsResponse = await talentBoostApi.getCourseAssistantSuggestions({
          session_id: sessionId,
          curso_id: cursoId,
          employee_id: employeeId,
          employee_name: employeeName,
          progresso_curso: progressoCurso,
          modulo_atual: moduloAtual,
        });

        setSuggestions(suggestionsResponse.suggestions || []);
      } catch (error) {
        console.error('Erro ao iniciar sessão:', error);
      }
    }

    initSession();
  }, [cursoId, employeeId, employeeName, progressoCurso, moduloAtual, sessionId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await talentBoostApi.askCourseAssistant({
        session_id: sessionId,
        curso_id: cursoId,
        employee_id: employeeId,
        employee_name: employeeName,
        question: inputValue,
        progresso_curso: progressoCurso,
        modulo_atual: moduloAtual,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response.content,
        timestamp: response.response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Erro ao enviar pergunta:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content:
          'Desculpe, tive um problema ao processar sua pergunta. Pode tentar novamente?',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const _handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white p-4 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="bg-white bg-opacity-20 rounded-full p-2">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">Tutor Virtual</h3>
            <p className="text-sm text-primary-100">{cursoTitulo}</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
          <span>Seu Progresso</span>
          <span className="font-semibold">{progressoCurso.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all"
            style={{ width: `${progressoCurso}%` }}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`flex items-start space-x-2 max-w-[80%] ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5" />
                ) : (
                  <Bot className="w-5 h-5" />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="text-sm prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
                <p
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
                  }`}
                >
                  {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="w-5 h-5 text-gray-600" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.4s' }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && messages.length === 1 && (
        <div className="px-4 py-3 bg-blue-50 border-t border-blue-200">
          <div className="flex items-center space-x-2 text-sm text-blue-900 mb-2">
            <Lightbulb className="w-4 h-4" />
            <span className="font-semibold">Próximos Passos:</span>
          </div>
          <div className="space-y-1">
            {suggestions.map((suggestion, idx) => (
              <div key={idx} className="text-sm text-blue-800 flex items-start space-x-2">
                <span className="text-blue-600">•</span>
                <span>{suggestion}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
          <p className="text-xs text-gray-600 mb-2">Perguntas rápidas:</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setInputValue('O que vou aprender neste curso?')}
              className="px-3 py-1 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-100 transition-colors flex items-center space-x-1"
            >
              <BookOpen className="w-3 h-3" />
              <span>O que vou aprender?</span>
            </button>
            <button
              onClick={() => setInputValue('Como posso aplicar isso no meu trabalho?')}
              className="px-3 py-1 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-100 transition-colors flex items-center space-x-1"
            >
              <MessageCircle className="w-3 h-3" />
              <span>Como aplicar?</span>
            </button>
            <button
              onClick={() => setInputValue('Tem exercícios práticos?')}
              className="px-3 py-1 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Exercícios práticos?
            </button>
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Digite sua dúvida..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || loading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send className="w-5 h-5" />
            <span>Enviar</span>
          </button>
        </div>
      </form>
    </div>
  );
}
