# 🛠️ TalentBoost - API Tools & Endpoints

## 📋 Visão Geral

O TalentBoost expõe **19 endpoints REST** organizados em 6 categorias:

| Categoria | Endpoints | Descrição |
|---|---|---|
| 🏥 **Health** | 1 | Status do sistema |
| 👥 **Employees** | 5 | Dados de colaboradores |
| 📚 **Courses** | 1 | Catálogo de cursos |
| 📊 **Stats** | 1 | Estatísticas gerais |
| 💬 **Feedback** | 2 | Rastreamento de interações |
| 📈 **Analytics** | 4 | Métricas e performance |
| 🤖 **Course Assistant** | 4 | Tutor virtual com LLM |

---

## 🏥 Health Check

### `GET /`
**Descrição:** Verifica se a API está rodando

**Resposta:**
```json
{
  "status": "ok",
  "service": "TalentBoost API",
  "version": "1.0.0"
}
```

**Exemplo:**
```bash
curl http://localhost:8001/
```

---

## 👥 Employees (Colaboradores)

### 1. `GET /api/employees`
**Descrição:** Lista todos os colaboradores disponíveis

**Resposta:**
```json
[
  {
    "name": "Ana Paula Ferreira",
    "cargo": "Desenvolvedora Backend",
    "departamento": "Tecnologia",
    "nivel": null
  }
]
```

**Exemplo:**
```bash
curl http://localhost:8001/api/employees
```

---

### 2. `GET /api/employees/{employee_name}/profile`
**Descrição:** Retorna dados cadastrais completos de um colaborador

**Parâmetros:**
- `employee_name` (path) - Nome do colaborador

**Resposta:**
```json
{
  "COLABORADOR_ID": 2001,
  "NOME": "Ana Paula Ferreira",
  "CARGO_NOME": "Desenvolvedora Backend",
  "DEPARTAMENTO": "Tecnologia",
  "TEMPO_DE_CASA_EM_MESES": 12
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/profile
```

---

### 3. `GET /api/employees/{employee_name}/evaluation`
**Descrição:** Retorna avaliação de desempenho completa

**Parâmetros:**
- `employee_name` (path) - Nome do colaborador

**Resposta:**
```json
{
  "nome": "Ana Paula Ferreira",
  "cargo": "Desenvolvedora Backend",
  "ciclo": "2025",
  "valores": {
    "jogamosJuntosPelaCompanhia": {
      "auto": { "nota": 7, "observacao": "..." },
      "par": { "nota": 7, "observacao": "..." },
      "gestor": { "nota": 6, "observacao": "..." }
    }
  }
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/evaluation
```

---

### 4. `GET /api/employees/{employee_name}/gaps`
**Descrição:** Analisa gaps de competências identificados na avaliação

**Parâmetros:**
- `employee_name` (path) - Nome do colaborador

**Resposta:**
```json
{
  "employee_name": "Ana Paula Ferreira",
  "total_gaps": 2,
  "gaps": [
    {
      "competency_name": "Inovação com Foco no Cliente",
      "competency_key": "inovacaoComFocoNoCliente",
      "average_score": 5.3,
      "gap_severity": "high",
      "urgency": "high",
      "context": "Gap identificado com consenso entre avaliadores",
      "evaluator_consensus": 0.85,
      "development_hints": ["Gestao", "Soft Skills"],
      "key_observations": ["precisa desenvolver visão de produto"]
    }
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/gaps
```

---

### 5. `POST /api/employees/{employee_name}/recommendations`
**Descrição:** Gera recomendações personalizadas de treinamentos baseado nos gaps

**Parâmetros:**
- `employee_name` (path) - Nome do colaborador

**Body:**
```json
{
  "employee_name": "Ana Paula Ferreira",
  "top_n": 5,
  "exclude_completed": true
}
```

**Resposta:**
```json
{
  "employee_name": "Ana Paula Ferreira",
  "profile_summary": {
    "cargo": "Desenvolvedora Backend",
    "nivel": "Junior",
    "nota_media_geral": 6.8,
    "total_gaps": 2
  },
  "recommendations": [
    {
      "curso_id": "C008",
      "titulo": "Visão de Produto para Desenvolvedores",
      "categoria": "Gestao",
      "relevance_score": 0.87,
      "match_reason": "Altamente recomendado para 'Inovação com Foco no Cliente'",
      "addresses_gaps": ["Inovação com Foco no Cliente"],
      "priority": "high",
      "explanation": {
        "primary_reason": "gap_match",
        "gap_addressed": "Inovação com Foco no Cliente",
        "secondary_reasons": ["Alto alinhamento...", "15 similares..."],
        "confidence": 0.87,
        "similar_employees_count": 15,
        "avg_satisfaction": 8.8
      }
    }
  ],
  "summary": {
    "total": 5,
    "by_priority": { "high": 2, "medium": 3 },
    "average_relevance": 0.78
  },
  "metadata": {
    "cold_start_used": false,
    "generation_time_ms": 47.32
  }
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "employee_name": "Ana Paula Ferreira",
    "top_n": 5,
    "exclude_completed": true
  }'
```

---

### 6. `GET /api/employees/{employee_name}/sentiment-analysis`
**Descrição:** Análise de sentimentos das observações da avaliação

**Parâmetros:**
- `employee_name` (path) - Nome do colaborador

**Resposta:**
```json
{
  "employee_name": "Ana Paula Ferreira",
  "sentiment_analysis": {
    "inovacaoComFocoNoCliente": [
      {
        "evaluator": "gestor",
        "tone": "constructive",
        "urgency": "high",
        "key_phrases": ["precisa desenvolver"],
        "development_hints": ["Gestao"]
      }
    ]
  }
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/employees/Ana%20Paula%20Ferreira/sentiment-analysis
```

---

## 📚 Courses (Cursos)

### `GET /api/courses`
**Descrição:** Lista todos os cursos disponíveis no LMS

**Query Params (opcional):**
- `category` - Filtrar por categoria

**Resposta:**
```json
{
  "courses": [
    {
      "cursoID": "C001",
      "titulo": "Segurança da Informação",
      "categoria": "Compliance",
      "modalidade": "EAD",
      "cargaHoraria": 4,
      "obrigatorio": true,
      "notaMinima": 7
    }
  ]
}
```

**Exemplo:**
```bash
# Todos os cursos
curl http://localhost:8001/api/courses

# Filtrar por categoria
curl http://localhost:8001/api/courses?category=Compliance
```

---

## 📊 Stats (Estatísticas)

### `GET /api/stats/overview`
**Descrição:** Estatísticas gerais do sistema

**Resposta:**
```json
{
  "total_employees": 6,
  "total_courses": 15,
  "total_gaps_detected": 12,
  "average_recommendations_per_employee": 5.2,
  "cache_hit_rate": 0.85
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/stats/overview
```

---

## 💬 Feedback (Rastreamento de Interações)

### 1. `POST /api/feedback/track`
**Descrição:** Registra uma interação do usuário com as recomendações

**Body:**
```json
{
  "employee_id": 2001,
  "employee_name": "Ana Paula Ferreira",
  "curso_id": "C008",
  "curso_titulo": "Comunicação Assertiva",
  "action": "clicked",
  "rating": null,
  "metadata": {
    "source": "recommendations_page",
    "position": 1
  }
}
```

**Actions válidas:**
- `viewed` - Recomendação exibida
- `clicked` - Usuário clicou para ver detalhes
- `enrolled` - Usuário se matriculou
- `dismissed` - Usuário marcou "não tenho interesse"
- `rated` - Usuário avaliou após concluir (0-10)

**Resposta:**
```json
{
  "status": "success",
  "feedback_id": "fb-12345",
  "timestamp": "2026-04-06T15:30:00Z"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8001/api/feedback/track \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "curso_id": "C008",
    "curso_titulo": "Comunicação Assertiva",
    "action": "clicked"
  }'
```

---

### 2. `GET /api/feedback/employee/{employee_id}`
**Descrição:** Histórico de interações de um colaborador

**Parâmetros:**
- `employee_id` (path) - ID do colaborador

**Resposta:**
```json
{
  "employee_id": 2001,
  "total_interactions": 15,
  "interactions": [
    {
      "timestamp": "2026-04-06T15:30:00Z",
      "curso_id": "C008",
      "action": "clicked"
    }
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/feedback/employee/2001
```

---

## 📈 Analytics (Métricas)

### 1. `GET /api/analytics/summary`
**Descrição:** Resumo geral de analytics do sistema

**Resposta:**
```json
{
  "total_interactions": 1523,
  "total_views": 892,
  "total_clicks": 304,
  "total_enrollments": 89,
  "total_dismissals": 45,
  "overall_ctr": 0.341,
  "overall_enrollment_rate": 0.293,
  "unique_employees": 127,
  "unique_courses": 42
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/analytics/summary
```

---

### 2. `GET /api/analytics/course/{curso_id}`
**Descrição:** Analytics de um curso específico

**Parâmetros:**
- `curso_id` (path) - ID do curso

**Resposta:**
```json
{
  "curso_id": "C008",
  "click_through_rate": 0.385,
  "enrollment_rate": 0.312,
  "dismissal_rate": 0.052,
  "average_rating": 8.7
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/analytics/course/C008
```

---

### 3. `GET /api/analytics/popular-courses`
**Descrição:** Ranking de cursos mais populares

**Query Params:**
- `top_n` - Número de cursos a retornar (default: 10)

**Resposta:**
```json
{
  "top_n": 10,
  "popular_courses": [
    {
      "curso_id": "C001",
      "titulo": "Segurança da Informação",
      "clicks": 234,
      "enrollments": 89,
      "views": 567
    }
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/analytics/popular-courses?top_n=5
```

---

### 4. `GET /api/analytics/recommendations-performance`
**Descrição:** Performance do sistema de recomendação

**Resposta:**
```json
{
  "recommendation_stats": {
    "total_interactions": 1523,
    "overall_ctr": 0.341
  },
  "cache_stats": {
    "cache_size": 42,
    "cache_enabled": true,
    "cache_ttl_seconds": 3600
  },
  "system_info": {
    "total_courses_indexed": 15,
    "recommendation_strategies": [
      "content_based",
      "cold_start_fallback",
      "diversity_filter",
      "temporal_decay"
    ]
  }
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/analytics/recommendations-performance
```

---

## 🤖 Course Assistant (Tutor Virtual)

### 1. `POST /api/course-assistant/start`
**Descrição:** Inicia uma sessão com o tutor virtual do curso

**Body:**
```json
{
  "session_id": "session-12345",
  "curso_id": "C008",
  "employee_id": 2001,
  "employee_name": "Ana Paula Ferreira",
  "progresso_curso": 45.0,
  "modulo_atual": "Técnicas de escuta ativa"
}
```

**Resposta:**
```json
{
  "session_id": "session-12345",
  "message": {
    "role": "assistant",
    "content": "Olá, Ana Paula! 👋\n\nSou seu assistente virtual...",
    "timestamp": "2026-04-06T15:30:00Z"
  }
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8001/api/course-assistant/start \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-12345",
    "curso_id": "C008",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "progresso_curso": 45.0
  }'
```

---

### 2. `POST /api/course-assistant/ask`
**Descrição:** Envia uma pergunta ao tutor virtual

**Body:**
```json
{
  "session_id": "session-12345",
  "curso_id": "C008",
  "employee_id": 2001,
  "employee_name": "Ana Paula Ferreira",
  "question": "O que é comunicação assertiva?",
  "progresso_curso": 45.0,
  "modulo_atual": "Técnicas de escuta ativa"
}
```

**Resposta:**
```json
{
  "session_id": "session-12345",
  "response": {
    "role": "assistant",
    "content": "Ótima pergunta! Vou explicar...",
    "timestamp": "2026-04-06T15:31:00Z"
  },
  "question_type": "definition"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8001/api/course-assistant/ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-12345",
    "curso_id": "C008",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "question": "O que é comunicação assertiva?",
    "progresso_curso": 45.0
  }'
```

---

### 3. `GET /api/course-assistant/history/{session_id}`
**Descrição:** Busca histórico completo de uma sessão

**Parâmetros:**
- `session_id` (path) - ID da sessão

**Resposta:**
```json
{
  "session_id": "session-12345",
  "messages": [
    {
      "role": "assistant",
      "content": "Olá, Ana Paula!...",
      "timestamp": "2026-04-06T15:30:00Z"
    },
    {
      "role": "user",
      "content": "O que é comunicação assertiva?",
      "timestamp": "2026-04-06T15:30:30Z"
    },
    {
      "role": "assistant",
      "content": "Ótima pergunta!...",
      "timestamp": "2026-04-06T15:31:00Z"
    }
  ]
}
```

**Exemplo:**
```bash
curl http://localhost:8001/api/course-assistant/history/session-12345
```

---

### 4. `POST /api/course-assistant/suggestions`
**Descrição:** Obtém sugestões de próximos passos baseado no progresso

**Body:**
```json
{
  "session_id": "session-12345",
  "curso_id": "C008",
  "employee_id": 2001,
  "employee_name": "Ana Paula Ferreira",
  "progresso_curso": 45.0,
  "modulo_atual": "Técnicas de escuta ativa"
}
```

**Resposta:**
```json
{
  "suggestions": [
    "Você já está na metade! Que tal revisar os conceitos principais?",
    "Pratique com exercícios para fixar o conteúdo.",
    "Lembre-se: não tenha pressa. É melhor entender bem cada conceito."
  ]
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8001/api/course-assistant/suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-12345",
    "curso_id": "C008",
    "employee_id": 2001,
    "employee_name": "Ana Paula Ferreira",
    "progresso_curso": 45.0
  }'
```

---

## 🔐 Autenticação

**Atualmente:** Sem autenticação (desenvolvimento)

**Produção:** Adicionar Bearer token ou API key:
```bash
curl -H "Authorization: Bearer seu-token" http://api.talentboost.com/api/employees
```

---

## 📊 Rate Limits

**Desenvolvimento:** Sem limites

**Produção recomendada:**
- Recomendações: 100 req/min por usuário
- Course Assistant: 20 req/min por sessão
- Analytics: 1000 req/min global

---

## 🌐 Base URL

| Ambiente | URL |
|---|---|
| Local | `http://localhost:8001` |
| Dev | `https://dev-talentboost.azurecontainerapps.io` |
| Prod | `https://talentboost.azurecontainerapps.io` |

---

## 🧪 Collection Postman

**Importe esta collection** para testar todos os endpoints:

```bash
# Gerar collection automaticamente
curl http://localhost:8001/openapi.json > talentboost-openapi.json
```

---

## 📚 Documentação Interativa

Acesse a documentação Swagger automática:

```
http://localhost:8001/docs
```

Ou ReDoc:

```
http://localhost:8001/redoc
```

---

**Total:** 19 endpoints REST + Swagger/ReDoc automáticos  
**Versão:** 2.0.0  
**Última atualização:** 2026-04-06
