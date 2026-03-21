from fastapi import FastAPI
from src.langgraph_pipeline.graph import build_graph
from src.monitoring import logging

app = FastAPI()
logger = logging.getLogger(__name__)

graph = build_graph()


@app.get("/ask")
def ask(query: str, patient_id: str = "1"):
    logger.info(f"[API_ENDPOINT] /ask chamado | query='{query[:50]}...' | patient_id={patient_id}")
    
    try:
        result = graph.invoke({
            "query": query,
            "patient_id": patient_id
        })
        
        logger.info(f"[API_ENDPOINT] Resposta gerada com sucesso | patient_id={patient_id}")
        
        return {
            "response": result["final_answer"]
        }
    except Exception as e:
        logger.error(f"[API_ENDPOINT] ❌ Erro durante processamento | patient_id={patient_id} | erro={str(e)}")
        raise