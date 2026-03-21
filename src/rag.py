from src.monitoring import logging
import os
import json
from typing import List
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

OUTPUT_PATH = "vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATASET_PATH = "data/processed/medical_qa_dataset.json"
MAX_RECORDS = 10000

def load_dataset() -> List[dict]:
    logger.info("Carregando dataset...")
    
    with open(DATASET_PATH, "r") as f:
        data = json.load(f)

        if MAX_RECORDS:
            data = data[:MAX_RECORDS]

        logger.info(f"{len(data)} registros carregados")
        logger.info("Carregando dataset... (OK)")
        return data

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

def transform(data: List[dict]) -> List[str]:
    logger.info("Transformando dados em documentos...")

    documents = []

    for item in tqdm(data):
        instruction = clean_text(item.get("instruction", ""))
        output = clean_text(item.get("output", ""))

        if not instruction or not output:
            continue

        content = f"""
Pergunta: {instruction}

Resposta: {output}
""".strip()

        metadata = {
            "source": "medical_dataset",
            "type": "qa_pair"
        }

        doc = Document(
            page_content=content,
            metadata=metadata
        )

        documents.append(doc)

    logger.info("Transformando dados em documentos... (OK)")
    return documents

def build_vectorstore():
    logger.info(f"Iniciando geração de vectorstore")
    data = load_dataset()
    documents = transform(data)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
    logger.info("Criando embeddings e index FAISS...")
    db = FAISS.from_documents(
            documents,
            embeddings
        )
    logger.info("Criando embeddings e index FAISS... (OK)")
    logger.info("Savando Vectorstore...")
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    db.save_local(OUTPUT_PATH)
    logger.info(f"Vectorstore salvo em: {OUTPUT_PATH}")
    logger.info("Finalizando geração de vectorstore")

def load_vectorstore():
    logger.info("Carregando vectorstore...")
    if not os.path.exists(os.path.join(OUTPUT_PATH, "index.faiss")):
        logger.error("Vectorstore não encontrado. Execute build() primeiro.")
        raise FileNotFoundError(
            "Vectorstore não encontrado. Execute build() primeiro."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    faiss = FAISS.load_local(
        OUTPUT_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("Carregando vectorstore... (OK)")
    return faiss;

def search(query: str, k: int = 5):
    db = load_vectorstore()

    logger.info(f"🔎 Buscando por: {query}")
    results = db.similarity_search(query, k=k)

    for i, doc in enumerate(results):
        logger.info(f"\n--- Resultado {i+1} ---")
        logger.info(doc.page_content[:500])