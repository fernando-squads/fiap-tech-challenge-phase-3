# 📋 Fluxo Completo da API com Auditoria

**Status de Conformidade:** ✅ **100% CONFORME** (Requisito 3.2 - Logging Detalhado)  
**Documento de Verificação:** [VERIFICACAO_REQUISITOS_FINAL.md](VERIFICACAO_REQUISITOS_FINAL.md)

## 🎯 Visão Geral

Quando a API `/ask` é chamada, o fluxo completo é rastreado com **logging granular** em cada etapa, garantindo conformidade com o requisito **3.2 - Logging detalhado para rastreamento e auditoria**. **Todos os 5 nós do pipeline registram suas ações em tempo real.**

---

## 🔄 Fluxo de Execução Completo

### **1️⃣ Entrada da API**
```
GET /ask?query="Qual o tratamento para diabetes?"&patient_id="1"
```

**Logs registrados:**
```
[API_ENDPOINT] /ask chamado | query='Qual o tratamento para...' | patient_id=1
```

---

### **2️⃣ Nó: load_patient** 
**Arquivo:** [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py)

**Objetivo:** Carregar dados estruturados do paciente (idade, sexo, condições, medicamentos)

**Logs registrados:**
```
[LOAD_PATIENT] Iniciando carregamento de dados | patient_id=1
[LOAD_PATIENT] Dados carregados com sucesso | patient_id=1
```

**Requisitos Atendidos:**
- ✅ **2.1.3** - Contextualização com dados do paciente
- ✅ **4.1** - Modularização (PatientRepository)

---

### **3️⃣ Nó: retrieve_docs**
**Arquivo:** [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py)

**Objetivo:** Buscar documentos relevantes no FAISS vectorstore via RAG

**Logs registrados:**
```
[RETRIEVE_DOCS] Iniciando busca no vectorstore | query='Qual o tratamento para...'
[RETRIEVE_DOCS] 2 documentos recuperados | query='Qual o tratamento para...'
[RETRIEVE_DOCS] Fonte anexada | source=medical_dataset
```

**Requisitos Atendidos:**
- ✅ **2.1.1** - Pipeline LangChain integrado
- ✅ **2.1.2** - Consultas a BD estruturadas (FAISS)

---

### **4️⃣ Nó: generate_answer**
**Arquivo:** [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py)  
**Inference:** [src/inference.py](src/inference.py)

**Objetivo:** Gerar resposta usando LLM fine-tuned (Llama-3-8B com LoRA)

**Logs registrados:**
```
[GENERATE_ANSWER] Iniciando geração de resposta | patient_id=1 | query='Qual o tratamento para...'
[INFERENCE] Iniciando geração com modelo fine-tuned | query_length=42
[INFERENCE] 2 documentos carregados para contexto
[INFERENCE] Iniciando tokenização segura
[INFERENCE] Tokenização concluída | num_tokens=512
[INFERENCE] Iniciando geração de tokens (max=300, temperature=0.1)
[INFERENCE] Geração concluída | output_tokens=187
[INFERENCE] Resposta pós-processada | response_length=450
[GENERATE_ANSWER] Resposta gerada com sucesso | response_length=450 | patient_id=1
```

**Requisitos Atendidos:**
- ✅ **1.1** - Fine-tuning de LLM com dados médicos (LoRA)
- ✅ **2.1.1** - LangChain pipeline
- ✅ **3.2** - Logging detalhado de geração

---

### **5️⃣ Nó: validate**
**Arquivo:** [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py)  
**Guards:** [src/langgraph_pipeline/guards.py](src/langgraph_pipeline/guards.py)

**Objetivo:** Validar se a resposta não contém prescrições diretas

**Cenário A - Resposta Aprovada:**
```
[VALIDATE] Iniciando validação de segurança | patient_id=1
[VALIDATE] ✅ Sécurança: Conteúdo aprovado | patient_id=1
```

**Cenário B - Resposta Bloqueada (contém "dose"):**
```
[VALIDATE] Iniciando validação de segurança | patient_id=1
[VALIDATE] ⚠️ BLOQUEADO: Conteúdo contém sugestão de dose/medicamento | patient_id=1
```

**Requisitos Atendidos:**
- ✅ **3.1** - Limites de atuação (bloqueia prescrições diretas)
- ✅ **3.2** - Logging de tentativas de bypass de segurança

---

### **6️⃣ Nó: explain**
**Arquivo:** [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py)  
**Explainability:** [src/langgraph_pipeline/explainability.py](src/langgraph_pipeline/explainability.py)

**Objetivo:** Anexar fontes citadas à resposta (rastreabilidade)

**Logs registrados:**
```
[EXPLAIN] Iniciando anexação de fontes | patient_id=1 | num_docs=2
[EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
[EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
[EXPLAIN] Resposta final compilada com sucesso | patient_id=1
```

**Requisitos Atendidos:**
- ✅ **3.3** - Explainability (fontes citadas)
- ✅ **2.1.3** - Contextualização com rastreabilidade

---

### **7️⃣ Saída da API**
**Arquivo:** [src/api.py](src/api.py)

**Response JSON:**
```json
{
  "response": "Resposta completa com disclaimer\n\n📚 Fontes:\n1. medical_dataset\n2. medical_dataset"
}
```

**Logs registrados:**
```
[API_ENDPOINT] Resposta gerada com sucesso | patient_id=1
```

---

## 📊 Exemplo Completo de Log End-to-End

```
2026-03-21 10:15:32 | root | INFO | [API_ENDPOINT] /ask chamado | query='Qual o tratamento para diabetes?' | patient_id=1
2026-03-21 10:15:32 | nodes | INFO | [LOAD_PATIENT] Iniciando carregamento de dados | patient_id=1
2026-03-21 10:15:32 | nodes | INFO | [LOAD_PATIENT] Dados carregados com sucesso | patient_id=1
2026-03-21 10:15:32 | nodes | INFO | [RETRIEVE_DOCS] Iniciando busca no vectorstore | query='Qual o tratamento para diabetes?'
2026-03-21 10:15:33 | nodes | INFO | [RETRIEVE_DOCS] 2 documentos recuperados | query='Qual o tratamento para diabetes?'
2026-03-21 10:15:33 | nodes | INFO | [GENERATE_ANSWER] Iniciando geração de resposta | patient_id=1 | query='Qual o tratamento para...'
2026-03-21 10:15:33 | inference | INFO | [INFERENCE] Iniciando geração com modelo fine-tuned | query_length=42
2026-03-21 10:15:33 | inference | INFO | [INFERENCE] 2 documentos carregados para contexto
2026-03-21 10:15:33 | inference | INFO | [INFERENCE] Iniciando tokenização segura
2026-03-21 10:15:33 | inference | INFO | [INFERENCE] Tokenização concluída | num_tokens=512
2026-03-21 10:15:33 | inference | INFO | [INFERENCE] Iniciando geração de tokens (max=300, temperature=0.1)
2026-03-21 10:15:37 | inference | INFO | [INFERENCE] Geração concluída | output_tokens=187
2026-03-21 10:15:37 | inference | INFO | [INFERENCE] Resposta pós-processada | response_length=450
2026-03-21 10:15:37 | nodes | INFO | [GENERATE_ANSWER] Resposta gerada com sucesso | response_length=450 | patient_id=1
2026-03-21 10:15:37 | nodes | INFO | [VALIDATE] Iniciando validação de segurança | patient_id=1
2026-03-21 10:15:37 | nodes | INFO | [VALIDATE] ✅ Sécurança: Conteúdo aprovado | patient_id=1
2026-03-21 10:15:37 | nodes | INFO | [EXPLAIN] Iniciando anexação de fontes | patient_id=1 | num_docs=2
2026-03-21 10:15:37 | nodes | INFO | [EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
2026-03-21 10:15:37 | nodes | INFO | [EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
2026-03-21 10:15:37 | nodes | INFO | [EXPLAIN] Resposta final compilada com sucesso | patient_id=1
2026-03-21 10:15:37 | api | INFO | [API_ENDPOINT] Resposta gerada com sucesso | patient_id=1
```

---

## ✅ Conformidade com Requisitos

| Requisito | Status | Evidência no Fluxo |
|-----------|--------|-------------------|
| **1.1** Fine-tuning LLM | ✅ | Nó `generate_answer` → `[INFERENCE]` logs |
| **1.2** Preprocessing/Anonimização | ✅ | Dados pré-processados antes de `/ask` |
| **2.1.1** Pipeline LangChain | ✅ | `graph.invoke()` com 5 nós sequenciais |
| **2.1.2** Consulta BD estruturada | ✅ | Nó `load_patient` + vectorstore FAISS |
| **2.1.3** Contextualizar respostas | ✅ | `patient_data` injetado no prompt |
| **3.1** Limites de atuação | ✅ | Nó `validate` bloqueia termos proibidos |
| **3.2** Logging detalhado | ✅ | **Novo:** Logs granulares em cada nó |
| **3.3** Explainability | ✅ | Nó `explain` adiciona fontes citadas |
| **4.1** Código modularizado | ✅ | 7 módulos separados (llm, dataset, langgraph_pipeline, etc) |

---

## 📁 Arquivos Modificados

- ✅ [src/langgraph_pipeline/nodes.py](src/langgraph_pipeline/nodes.py) - Adicionados logs em todos os 5 nós
- ✅ [src/api.py](src/api.py) - Adicionados logs de entrada/saída
- ✅ [src/inference.py](src/inference.py) - Adicionados logs detalhados de inferência
- ✅ [src/monitoring/logger.py](src/monitoring/logger.py) - Melhorado handler com arquivo rotativo

---

## 🚀 Como Testar

```bash
# Ativar ambiente
source env/bin/activate

# Iniciar API
uvicorn src.api:app --reload

# Em outro terminal, fazer requisição
curl "http://localhost:8000/ask?query=Qual%20o%20tratamento%20para%20diabetes&patient_id=1"

# Verificar logs
tail -f logs/fiap_tech_challenge_phase_3.log
```

---

## 📝 Localização dos Logs

- **Arquivo:** `logs/fiap_tech_challenge_phase_3.log`
- **Console:** Exibido em tempo real durante execução
- **Rotação:** Máximo 5MB por arquivo, com histórico de 5 arquivos

---

## 🔒 Segurança Auditável

O logging implementado permite:
- ✅ Rastreamento completo de cada requisição
- ✅ Detecção de tentativas de bypass de segurança
- ✅ Auditoria de dados de paciente acessados
- ✅ Histórico de bloqueios por segurança
- ✅ Performance monitoring (tempos de execução)
