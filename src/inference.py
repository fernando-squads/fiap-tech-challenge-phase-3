import os
from src.monitoring import logging
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.rag import load_vectorstore
import torch

load_dotenv()

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
model_path = "./models/llama-medical-sft"
access_token = os.getenv("META_LLAMA_TOKEN")

logger = logging.getLogger(__name__)


tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    token=access_token,
    padding_side="right"
)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="mps",
    dtype=torch.float16
)

model.config.pad_token_id = tokenizer.pad_token_id

db = load_vectorstore()

def clean_context(docs):
    cleaned = []

    for d in docs:
        text = d.page_content

        # remove ruído de dataset Q&A
        text = text.replace("Pergunta:", "")
        text = text.replace("Resposta:", "")

        cleaned.append(text.strip())

    # limita tamanho (evita bagunça no modelo)
    final_context = "\n\n".join(cleaned)
    return final_context[:1500]

def build_prompt(context, query):
    return f"""
Você é um médico especialista.

Use APENAS o contexto abaixo para responder.

Se o contexto estiver em inglês, traduza mentalmente e responda em português.

Se não houver informação suficiente, diga claramente que não sabe.

Contexto clínico:
{context}

Pergunta do médico:
{query}

Resposta clara, objetiva e em português:
"""

def generate_response(query: str):
    logger.info(f"[INFERENCE] Iniciando geração com modelo fine-tuned | query_length={len(query)}")
    
    docs = db.similarity_search(query, k=2)

    if not docs:
        logger.warning(f"[INFERENCE] Nenhum documento encontrado para query: {query}")
        return "Não encontrei informações relevantes para responder."

    logger.info(f"[INFERENCE] {len(docs)} documentos carregados para contexto")
    
    context = clean_context(docs)

    prompt = build_prompt(context, query)

    # 🔐 tokenização segura
    logger.info(f"[INFERENCE] Iniciando tokenização segura")
    inputs = tokenizer(prompt, return_tensors="pt").to("mps")

    # proteção contra NaN
    for k, v in inputs.items():
        if torch.isnan(v).any():
            logger.error(f"[INFERENCE] ❌ Erro: Input contém NaN no campo {k}")
            raise ValueError("Input contém NaN")

    logger.info(f"[INFERENCE] Tokenização concluída | num_tokens={inputs['input_ids'].shape[-1]}")

    # 🧠 geração estável
    logger.info(f"[INFERENCE] Iniciando geração de tokens (max=300, temperature=0.1)")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.1,         # 🔥 menos alucinação
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    logger.info(f"[INFERENCE] Geração concluída | output_tokens={outputs.shape[-1]}")
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 🔥 pós-processamento (remove prompt da resposta)
    if "Resposta clara" in response:
        response = response.split("Resposta clara")[-1]

    logger.info(f"[INFERENCE] Resposta pós-processada | response_length={len(response)}")
    
    return response.strip()