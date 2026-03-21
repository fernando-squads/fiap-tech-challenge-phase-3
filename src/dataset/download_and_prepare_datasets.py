from src.monitoring import logging
import os
import json
import requests
import zipfile
import xml.etree.ElementTree as ET
from tqdm import tqdm

logger = logging.getLogger(__name__)

logger.info("Iniciando geração de dataset")

logger.info("Carregando configurações...")

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

logger.info("Carregando configurações...(OK)")

logger.info("Criando diretórios...")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

logger.info("Criando diretórios...(OK)")


# =========================================================
# 1. DOWNLOAD PUBMEDQA
# =========================================================
def download_pubmedqa():
    logger.info("Baixando dataset PubMedQA...")
    url = "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/ori_pqal.json"
    output_path = os.path.join(RAW_DIR, "pubmedqa.json")

    
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

    logger.info("Baixando dataset PubMedQA...(OK)")

# =========================================================
# 2. PROCESS PUBMEDQA
# =========================================================
def process_pubmedqa():
    logger.info("Processando dataset PubMedQA...")

    input_path = os.path.join(RAW_DIR, "pubmedqa.json")
    output_data = []

    with open(input_path) as f:
        data = json.load(f)

    for key, item in data.items():
        question = item.get("QUESTION", "")
        context = " ".join(item.get("CONTEXTS", []))
        answer = item.get("LONG_ANSWER", "")

        instruction = f"{question}\nContexto: {context}"

        output_data.append({
            "instruction": instruction,
            "output": answer
        })

    logger.info("Processando dataset PubMedQA...(OK)")
    return output_data

# =========================================================
# 3. DOWNLOAD MEDQUAD
# =========================================================
def download_medquad():
    logger.info("Baixando dataset MedQuAD...")
    url = "https://github.com/abachaa/MedQuAD/archive/refs/heads/master.zip"
    zip_path = os.path.join(RAW_DIR, "medquad.zip")

    
    response = requests.get(url)

    with open(zip_path, "wb") as f:
        f.write(response.content)

    logger.info("Extraindo MedQuAD...")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(RAW_DIR)

    logger.info("Extraindo MedQuAD...(OK)")

    logger.info("Baixando dataset MedQuAD...(OK)")

# =========================================================
# 4. PROCESS MEDQUAD (XML)
# =========================================================

def process_medquad():
    logger.info("Processando dataset MedQuAD...")
    medquad_dir = os.path.join(RAW_DIR, "MedQuAD-master")
    output_data = []

    for root, dirs, files in os.walk(medquad_dir):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)

                try:
                    tree = ET.parse(file_path)
                    root_xml = tree.getroot()

                    for qa in root_xml.findall(".//QAPair"):
                        question = qa.findtext("Question")
                        answer = qa.findtext("Answer")

                        if question and answer:
                            output_data.append({
                                "instruction": question.strip(),
                                "output": answer.strip()
                            })
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")

    logger.info("Processando dataset MedQuAD...(OK)")
    return output_data

# =========================================================
# 5. UNIFICAR DATASETS
# =========================================================
def unify_datasets(pubmedqa_data, medquad_data):
    logger.info("Unificando datasets...")

    combined = pubmedqa_data + medquad_data

    logger.info(f"Total de exemplos: {len(combined)}")

    output_path = os.path.join(PROCESSED_DIR, "medical_qa_dataset.json")

    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    logger.info(f"Dataset salvo em: {output_path}")
    logger.info("Unificando datasets...(OK)")

# =========================================================
# MAIN
# =========================================================
# if __name__ == "__main__":
#     download_pubmedqa()
#     pubmedqa_data = process_pubmedqa()
# 
#     download_medquad()
#     medquad_data = process_medquad()
# 
#     unify_datasets(pubmedqa_data, medquad_data)
# 
#     logger.info(f"Finalizando geração de dataset")