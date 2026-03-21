from src.monitoring import logging
from src.inference import generate_response

logger = logging.getLogger(__name__)
query = "Qual o tratamento para sepse?"

logger.info("Iniciando pesquisa")
logger.info(f"Enviando questionamento para o LLM: {query}")
response = generate_response(query)
logger.info(f"Resposta obtida do LLM: {response}")
logger.info("Finalizando pesquisa")