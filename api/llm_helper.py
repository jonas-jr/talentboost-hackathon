"""
Helper para inicializar LLM para o Course Assistant.

Tenta Azure OpenAI primeiro, depois OpenAI direto, fallback para modo simulado.
"""

import os
import logging

logger = logging.getLogger(__name__)


def create_llm_for_course_assistant():
    """
    Cria LLM para Course Assistant.

    Ordem de tentativa:
    1. Azure OpenAI direto (vars AZURE_OPENAI_*)
    2. OpenAI direto (vars OPENAI_*)
    3. None (modo simulado)

    Returns:
        LLM instance ou None
    """

    # Tentativa 1: Azure OpenAI direto
    try:
        from langchain_openai import AzureChatOpenAI

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")

        if not endpoint or not api_key:
            raise ValueError("Configuração Azure OpenAI incompleta")

        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
            api_key=api_key,
            temperature=float(os.getenv("COURSE_ASSISTANT_TEMPERATURE", "0.4")),
            streaming=False,
        )

        logger.info(f"LLM inicializada via Azure OpenAI (deployment: {deployment})")
        return llm

    except Exception as e:
        logger.warning(f"Azure OpenAI falhou: {e}")

    # Tentativa 2: OpenAI direto
    try:
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        base_url = os.getenv("OPENAI_BASE_URL")

        if not api_key:
            raise ValueError("Configuração OpenAI incompleta")

        kwargs = {
            "api_key": api_key,
            "model": model,
            "temperature": float(os.getenv("COURSE_ASSISTANT_TEMPERATURE", "0.4")),
            "streaming": False,
        }
        if base_url:
            kwargs["base_url"] = base_url

        llm = ChatOpenAI(**kwargs)
        logger.info(f"LLM inicializada via OpenAI (model: {model})")
        return llm

    except Exception as e:
        logger.warning(f"OpenAI falhou: {e}")

    # Fallback: modo simulado
    logger.info("Nenhuma LLM disponível. Course Assistant rodará em modo simulado.")
    return None
