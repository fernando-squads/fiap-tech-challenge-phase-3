# 🧪 GUIA PRÁTICO: Verificar Todos os Fluxos da API em Tempo Real

**Documentação prática para testar cada requisito do desafio conforme a API é acionada**

**Status:** ✅ **100% CONFORME COM REQUISITOS**  
**Documento de Verificação:** [VERIFICACAO_REQUISITOS_FINAL.md](VERIFICACAO_REQUISITOS_FINAL.md)

---

## 📋 Índice

| Teste | Requisito Coberto | Tempo | Página |
|-------|------------------|-------|--------|
| [✅ Teste 1](#-teste-1-verificar-pipeline-completo) | 1, 2, 3, 4 | 2-3min | ↓ |
| [✅ Teste 2](#-teste-2-verificar-bloqueio-segurança) | 3.1 | 1-2min | ↓ |
| [✅ Teste 3](#-teste-3-verificar-logging-auditoria) | 3.2 | 1min | ↓ |
| [✅ Teste 4](#-teste-4-verificar-explainability) | 3.3 | 1-2min | ↓ |
| [✅ Teste 5](#-teste-5-verificar-contextualização) | 2.1.3 | 2-3min | ↓ |

---

## ⚡ Setup Rápido

```bash
# 1. Ativar ambiente virtual
source env/bin/activate

# 2. Verificar que vectorstore está carregado
python -c "from src.rag import load_vectorstore; db = load_vectorstore(); print('✅ Vectorstore OK')"

# 3. Iniciar API
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

---

## ✅ TESTE 1: Verificar Pipeline Completo

**Objetivo:** Garantir que todos os requisitos (1, 2, 3, 4) funcionam juntos

### Passo 1: Fazer uma requisição completa

```bash
curl -X GET "http://localhost:8000/ask?query=Como%20tratar%20diabetes%20tipo%202&patient_id=1" \
  -H "Content-Type: application/json"
```

**Ou em Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/ask",
    params={
        "query": "Como tratar diabetes tipo 2?",
        "patient_id": "1"
    }
)

print(response.json()["response"])
```

### Passo 2: Verificar Resposta

Você deve receber resposta similar a:
```json
{
  "response": "[Resposta médica contextualizada]\n\n⚠️ Validar com médico.\n\n📚 Fontes:\n1. medical_dataset\n2. medical_dataset"
}
```

### Passo 3: Abrir logs em paralelo

```bash
# Em outro terminal
tail -f logs/fiap_tech_challenge_phase_3.log
```

Você verá:
```
[API_ENDPOINT] /ask chamado | query='Como tratar diabetes tipo 2?' | patient_id=1
[LOAD_PATIENT] Iniciando carregamento de dados | patient_id=1
[LOAD_PATIENT] Dados carregados com sucesso | patient_id=1
[RETRIEVE_DOCS] Iniciando busca no vectorstore | query='Como tratar diabetes tipo 2?'
[RETRIEVE_DOCS] 2 documentos recuperados | query='Como tratar diabetes tipo 2?'
[GENERATE_ANSWER] Iniciando geração de resposta | patient_id=1 | query='Como tratar...'
[INFERENCE] Iniciando geração com modelo fine-tuned | query_length=28
[INFERENCE] 2 documentos carregados para contexto
[INFERENCE] Tokenização concluída | num_tokens=512
[INFERENCE] Geração concluída | output_tokens=187
[GENERATE_ANSWER] Resposta gerada com sucesso | response_length=450 | patient_id=1
[VALIDATE] Iniciando validação de segurança | patient_id=1
[VALIDATE] ✅ Sécurança: Conteúdo aprovado | patient_id=1
[EXPLAIN] Iniciando anexação de fontes | patient_id=1 | num_docs=2
[EXPLAIN] Resposta final compilada com sucesso | patient_id=1
[API_ENDPOINT] Resposta gerada com sucesso | patient_id=1
```

### ✅ Requisitos Cobertos:

| Requisito | Verificado | Evidência |
|-----------|-----------|-----------|
| **1.1** Fine-tuning | ✅ | Log `[INFERENCE]` mostra modelo gerando tokens |
| **1.2** Preprocessing | ✅ | Dados em `data/processed/medical_qa_dataset.json` |
| **2.1.1** Pipeline LangChain | ✅ | 5 nós sequenciais nos logs |
| **2.1.2** BD Estruturada | ✅ | Log `[LOAD_PATIENT]` recupera dados |
| **2.1.3** Contextualização | ✅ | Log `[RETRIEVE_DOCS]` injeta contexto |
| **3.1** Limites atuação | ✅ | Log `[VALIDATE]` aprova conteúdo seguro |
| **3.2** Logging | ✅ | Tutti os nós registrados em `logs/` |
| **3.3** Explainability | ✅ | Log `[EXPLAIN]` adiciona fontes |
| **4.1** Modularização | ✅ | 7 módulos em `src/` |

---

## ✅ TESTE 2: Verificar Bloqueio de Segurança

**Objetivo:** Validar que requisito **3.1** (limites de atuação) funciona

### Passo 1: Tentar fazer uma pergunta com termo proibido

```bash
curl -X GET "http://localhost:8000/ask?query=Qual%20a%20dose%20de%20insulina%20para%20diabetes&patient_id=1"
```

### Passo 2: Verificar resposta

Resposta esperada:
```json
{
  "response": "⚠️ Conteúdo bloqueado por segurança.\n\n📚 Fontes:\n1. medical_dataset\n2. medical_dataset"
}
```

### Passo 3: Verificar logs

```bash
tail -f logs/fiap_tech_challenge_phase_3.log | grep VALIDATE
```

Você verá:
```
[VALIDATE] Iniciando validação de segurança | patient_id=1
[VALIDATE] ⚠️ BLOQUEADO: Conteúdo contém sugestão de dose/medicamento | patient_id=1
```

### ✅ Requisito 3.1 Validado:

- ✅ Sistema detectou termo proibido: "dose"
- ✅ Resposta foi bloqueada
- ✅ Log registrou tentativa de bloqueio (auditoria)
- ✅ Usuário recebeu aviso de segurança

---

## ✅ TESTE 3: Verificar Logging e Auditoria

**Objetivo:** Validar que requisito **3.2** (logging detalhado) funciona

### Passo 1: Fazer múltiplas requisições

```bash
# Requisição 1
curl -X GET "http://localhost:8000/ask?query=Sintomas%20de%20hipertensão&patient_id=1"

# Requisição 2 (para paciente diferente)
curl -X GET "http://localhost:8000/ask?query=Como%20tratar%20asma&patient_id=2"

# Requisição 3 (com termo proibido)
curl -X GET "http://localhost:8000/ask?query=Qual%20medicamento%20prescrevo&patient_id=1"
```

### Passo 2: Verificar arquivo de log completo

```bash
cat logs/fiap_tech_challenge_phase_3.log
```

Ou monitorar em tempo real:
```bash
tail -f logs/fiap_tech_challenge_phase_3.log
```

### Passo 3: Atributos Auditáveis

Para cada requisição, você pode verificar:

| Atributo | Exemplo de Log |
|----------|---------------|
| **Timestamp** | `2026-03-21 10:15:32` |
| **Nível** | `INFO`, `WARNING`, `ERROR` |
| **Módulo** | `[API_ENDPOINT]`, `[VALIDATE]`, etc |
| **Patient ID** | `patient_id=1` |
| **Query** | `query='Sintomas de...'` |
| **Resultado** | `✅ Aprovado` ou `⚠️ BLOQUEADO` |
| **Tempo Execução** | Implícito nos timestamps |

### ✅ Requisito 3.2 Validado:

- ✅ Logs estruturados por componente
- ✅ Rastreamento completo de cada requisição
- ✅ Detecção de tentativas de bypass
- ✅ Arquivo rotativo (`logs/fiap_tech_challenge_phase_3.log`)
- ✅ Console em tempo real para desenvolvimento

---

## ✅ TESTE 4: Verificar Explainability

**Objetivo:** Validar que requisito **3.3** (fontes citadas) funciona

### Passo 1: Fazer uma requisição normal

```bash
curl -X GET "http://localhost:8000/ask?query=Qual%20é%20o%20tratamento%20para%20pneumonia&patient_id=1"
```

### Passo 2: Analizar resposta

A resposta deve incluir:

```
[Resposta médica completa]

⚠️ Validar com médico.

📚 Fontes:
1. medical_dataset
2. medical_dataset
```

### Passo 3: Verificar logs de explicabilidade

```bash
grep EXPLAIN logs/fiap_tech_challenge_phase_3.log
```

Output:
```
[EXPLAIN] Iniciando anexação de fontes | patient_id=1 | num_docs=2
[EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
[EXPLAIN] Fonte anexada | patient_id=1 | source=medical_dataset
[EXPLAIN] Resposta final compilada com sucesso | patient_id=1
```

### ✅ Requisito 3.3 Validado:

- ✅ Resposta inclui fontes citadas
- ✅ Usuários podem rastrear origem da informação
- ✅ Facilita auditoria regulatória
- ✅ Aumenta confiança no sistema

---

## ✅ TESTE 5: Verificar Contextualização com Dados do Paciente

**Objetivo:** Validar que requisito **2.1.3** funciona corretamente

### Passo 1: Testar com paciente ID = "1"

```bash
curl -X GET "http://localhost:8000/ask?query=Qual%20é%20o%20melhor%20tratamento&patient_id=1"
```

### Passo 2: Verificar dados carregados

```bash
grep "load_patient" logs/fiap_tech_challenge_phase_3.log -A 5
```

Output deve mostrar:
```
[LOAD_PATIENT] Iniciando carregamento de dados | patient_id=1
[LOAD_PATIENT] Dados carregados com sucesso | patient_id=1
```

### Passo 3: Testar com paciente ID = "2" (inexistente)

```bash
curl -X GET "http://localhost:8000/ask?query=Qual%20é%20o%20melhor%20tratamento&patient_id=2"
```

### Passo 4: Verificar resposta

Mesmo sem dados específicos, sistema continua funcionando:
- ✅ Recupera dados do paciente (se existir)
- ✅ Gera resposta contextualizada
- ✅ Não quebra se paciente não existir

### ✅ Requisito 2.1.3 Validado:

- ✅ Dados do paciente são carregados
- ✅ Contexto é injetado na geração
- ✅ Respostas personalizadas por paciente
- ✅ Informações atualizadas a cada requisição

---

## 📊 Tabela Resumida de Testes

| Teste | Requisito | Comando | Verificação | Status |
|-------|-----------|---------|-------------|--------|
| 1 | 1,2,3,4 | `curl .../ask?query=...` | 5 nós nos logs | ✅ |
| 2 | 3.1 | Com termo "dose" | `[VALIDATE] ⚠️ BLOQUEADO` | ✅ |
| 3 | 3.2 | Múltiplas requisições | Arquivo `logs/` | ✅ |
| 4 | 3.3 | Qualquer query | `📚 Fontes:` na resposta | ✅ |
| 5 | 2.1.3 | Com `patient_id` | `[LOAD_PATIENT]` nos logs | ✅ |

---

## 🔍 Comandos Úteis para Debugging

### Ver logs em tempo real
```bash
tail -f logs/fiap_tech_challenge_phase_3.log
```

### Filtrar por nó específico
```bash
grep "VALIDATE" logs/fiap_tech_challenge_phase_3.log
```

### Ver últimas 50 linhas
```bash
tail -n 50 logs/fiap_tech_challenge_phase_3.log
```

### Contar requisições processadas
```bash
grep "[API_ENDPOINT]" logs/fiap_tech_challenge_phase_3.log | wc -l
```

### Verificar bloqueios de segurança
```bash
grep "BLOQUEADO" logs/fiap_tech_challenge_phase_3.log
```

### Ver tempo de execução de uma requisição
```bash
# Procure entre [API_ENDPOINT] chamado e [API_ENDPOINT] sucesso
grep "API_ENDPOINT" logs/fiap_tech_challenge_phase_3.log
```

---

## 🎯 Checklist Final

Após completar todos os testes, marque como confirmado:

```
Teste 1 - Pipeline Completo
  ☐ API respondeu com sucesso
  ☐ 5 nós foram registrados em ordem
  ☐ Resposta incluiu disclaimer
  ☐ Resposta incluiu fontes

Teste 2 - Bloqueio Segurança
  ☐ Termo "dose" foi bloqueado
  ☐ Log registrou bloqueio
  ☐ Resposta indicou segurança

Teste 3 - Logging Auditoria
  ☐ Arquivo de log criado
  ☐ Múltiplas requisições registradas
  ☐ Cada nó tem logs detalhados

Teste 4 - Explainability
  ☐ Resposta incluiu "📚 Fontes:"
  ☐ Fontes são rastreáveis
  ☐ Log de explicabilidade OK

Teste 5 - Contextualização
  ☐ Patient ID foi carregado
  ☐ Dados do paciente foram recuperados
  ☐ Resposta foi contextualizada

Resultado: ✅ TODOS OS REQUISITOS VALIDADOS
```

---

## 📝 Notas Importantes

1. **Primeira Execução:** O modelo pode demorar um pouco para carregar na primeira requisição (~10-15s)

2. **Logs em Console:** Se preferir logs apenas em arquivo:
   ```python
   # Editar src/monitoring/logger.py
   # Comentar: console_handler = logging.StreamHandler()
   ```

3. **Resetar Logs:** Se desejar começar com logs limpos:
   ```bash
   truncate -s 0 logs/fiap_tech_challenge_phase_3.log
   ```

4. **Teste com Curl vs Browser:** Curl mostra JSON puro; use:
   ```bash
   curl "http://localhost:8000/ask?query=..." | python -m json.tool
   ```

---

## 🚨 Troubleshooting

| Problema | Solução |
|----------|---------|
| "Vectorstore não encontrado" | Execute: `python src/rag.py` e depois `python src/rag.py --build` |
| "Porta 8000 em uso" | Use porta diferente: `--port 8001` |
| "Module not found" | Certifique: `source env/bin/activate` |
| "Logs não aparecem" | Verifique: `ls -la logs/` e permissões |
| "Resposta vazia" | Verifique dataset: `ls -la data/processed/` |

---

**Conclusão:** Seguindo este guia, você consegue validar todos os 4 requisitos principais do desafio! 🎉
