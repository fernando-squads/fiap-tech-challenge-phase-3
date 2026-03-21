from src.monitoring import logging
from dotenv import load_dotenv
import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

logger = logging.getLogger(__name__)

MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
DATASET_PATH = "data/processed/medical_qa_dataset.json"

access_token = os.getenv("META_LLAMA_TOKEN")

def train():
    logger.info(f"Iniciando treinamento do modelo")

    logger.info(f"Carregando tokenizador e modelo...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=access_token, padding_side="right")
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="mps",  # Mac
        dtype=torch.float16
    )

    logger.info(f"Carregando tokenizador e modelo...(OK)")

    logger.info(f"Carregando dataset...")

    dataset = load_dataset("json", data_files=DATASET_PATH)["train"]

    logger.info(f"Carregando dataset...(OK)")

    logger.info(f"Reduzindo datase para ganho de velocidade...")

    dataset = dataset.shuffle(seed=42).select(range(5000))

    logger.info(f"Reduzindo datase para ganho de velocidade...(OK)")

    # =====================================================
    # Formatador
    # =====================================================
    def formatting_func(example):
        messages = [
            {"role": "system", "content": "Você é um assistente médico. Seja preciso e não invente informações."},
            {"role": "user", "content": example["instruction"]},
            {"role": "assistant", "content": example["output"]}
        ]

        return tokenizer.apply_chat_template(
            messages,
            tokenize=False
        )

    # =====================================================
    # Configurações do LoRA
    # =====================================================
    peft_config = LoraConfig(
        r=4,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        task_type="CAUSAL_LM"
    )

    # =====================================================
    # Configurações de treinamento
    # =====================================================
    training_args = SFTConfig(
        output_dir="./models",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        num_train_epochs=1,
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="epoch",
        max_length=256,
        packing=False,
        dataloader_pin_memory=False
    )

    logger.info(f"Criando o treinador...")

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        peft_config=peft_config,
        formatting_func=formatting_func,
    )

    logger.info(f"Criando o treinador... (OK)")

    logger.info(f"Treinanado...")

    trainer.train()

    logger.info(f"Treinanado...(OK)")

    logger.info(f"Salvando o modelo treinado...")

    trainer.save_model("./models/llama-medical-sft")

    logger.info(f"Salvando o modelo treinado... (OK)")