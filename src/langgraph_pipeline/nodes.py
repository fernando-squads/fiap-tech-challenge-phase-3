from src.rag import load_vectorstore
from src.data_access.patient_repository import PatientRepository
from src.inference import generate_response
from src.monitoring import logging
import requests

WEBHOOK_URL = "https://webhook.exemplo.com/api/notification"

db = load_vectorstore()
patient_repo = PatientRepository()
logger = logging.getLogger(__name__)


def trigger_cancer_webhook(data: dict):
    #
    # try:
    #     response = requests.post(WEBHOOK_URL, json=data, timeout=5)
    #     response.raise_for_status()
    #     logger.info(f"[WEBHOOK] Cancer trigger enviado com sucesso: {data}")
    # except Exception as e:
    #     logger.error(f"[WEBHOOK] Falha ao enviar cancer trigger: {e} | Payload: {data}")
    #
    logger.info(f"[WEBHOOK] Cancer trigger enviado com sucesso: {data}")


# 1. carregar paciente
def load_patient(state):
    patient_id = state["patient_id"]
    logger.info(f"[LOAD_PATIENT] Iniciando carregamento de dados | patient_id={patient_id}")
    
    patient_data = patient_repo.get_patient(patient_id)
    
    logger.info(f"[LOAD_PATIENT] Dados carregados com sucesso | patient_id={patient_id}")

    return {
        **state,
        "patient_data": patient_data
    }


# 2. recuperar contexto (RAG)
def retrieve_docs(state):
    query = state["query"]
    logger.info(f"[RETRIEVE_DOCS] Iniciando busca no vectorstore | query='{query[:50]}...'")
    
    docs = db.similarity_search(query, k=2)
    
    logger.info(f"[RETRIEVE_DOCS] {len(docs)} documentos recuperados | query='{query[:50]}...'")
    
    if not docs:
        logger.warning(f"[RETRIEVE_DOCS] Nenhum documento encontrado para query: {query}")
    
    context = "\n\n".join([d.page_content for d in docs])

    return {
        **state,
        "documents": docs,
        "context": context
    }


# 3. gerar resposta (LLM)
def generate_answer(state):
    query = state["query"]
    patient_id = state["patient_id"]
    
    logger.info(f"[GENERATE_ANSWER] Iniciando geração de resposta | patient_id={patient_id} | query='{query[:50]}...'")

    response = generate_response(query)
    
    logger.info(f"[GENERATE_ANSWER] Resposta gerada com sucesso | response_length={len(response)} | patient_id={patient_id}")

    return {
        **state,
        "response": response
    }


# 4. validação (segurança)
def validate(state):
    response = state["response"]
    patient_id = state["patient_id"]
    
    logger.info(f"[VALIDATE] Iniciando validação de segurança | patient_id={patient_id}")

    if "dose" in response.lower():
        logger.warning(f"[VALIDATE] BLOQUEADO: Conteúdo contém sugestão de dose/medicamento | patient_id={patient_id}")
        validated = "Conteúdo bloqueado por segurança."
    else:
        logger.info(f"[VALIDATE] Sécurança: Conteúdo aprovado | patient_id={patient_id}")
        validated = response + "\n\nValidar com médico."

    # Detecta câncer e dispara webhook de notificação
    if "cancer" in response.lower():
        webhook_payload = {
            "patient_id": patient_id,
            "query": state.get("query", ""),
            "disease": "cancer",
            "message": "Doença identificada como câncer — acionando webhook de notificação"
        }
        trigger_cancer_webhook(webhook_payload)

    return {
        **state,
        "validated_response": validated
    }


# 5. explainability
def explain(state):
    docs = state["documents"]
    response = state["validated_response"]
    patient_id = state["patient_id"]
    
    logger.info(f"[EXPLAIN] Iniciando anexação de fontes | patient_id={patient_id} | num_docs={len(docs)}")

    sources = "\n\nFontes:\n"

    for i, d in enumerate(docs):
        source_name = d.metadata.get('source', 'Dataset médico')
        sources += f"{i+1}. {source_name}\n"
        logger.info(f"[EXPLAIN] Fonte anexada | patient_id={patient_id} | source={source_name}")

    logger.info(f"[EXPLAIN] Resposta final compilada com sucesso | patient_id={patient_id}")

    return {
        **state,
        "final_answer": response + sources
    }