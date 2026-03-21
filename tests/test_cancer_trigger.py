from src.monitoring import logging
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api import app

logger = logging.getLogger(__name__)

client = TestClient(app)

query = "O que é cancer osseo?"
word = "cancer"

@patch("src.langgraph_pipeline.nodes.requests.post")
def test_cancer(mock_post):
    logger.info(f"Iniciando requisição com o conteudo: {query}")

    response = client.get("/ask", params={"query": query, "patient_id": "1"})
    assert response.status_code == 200
    text = response.json().get("response", "").lower()

    logger.info(f"Resposta obtida da requisição: {text}")

    assert word.lower() in text.lower(), f"'{word}' not found in '{text}'"
