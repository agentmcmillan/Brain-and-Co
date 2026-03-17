# nanochat Reference

Source: https://github.com/karpathy/nanochat

## What It Is

nanochat is Andrej Karpathy's minimal, from-scratch implementation of the full LLM pipeline: tokenization, pretraining, supervised finetuning, RLHF, evaluation, and chat inference. It is designed for educational clarity and as a practical baseline for training small language models on custom data.

Unlike inference-only tools, nanochat covers the entire lifecycle of building a chat model from raw text to interactive conversation.

## What It Can Do

- **Train a tokenizer** (BPE) on custom corpora
- **Pretrain** a transformer language model from scratch on any text dataset
- **Finetune** a pretrained model on instruction/chat data (SFT)
- **RLHF** alignment with reward modeling and PPO
- **Evaluate** against standard benchmarks
- **Chat** interactively with the trained model
- **Tool use** via the `execution.py` module (code execution, function calling)

## Hardware Requirements

nanochat's training pipeline requires substantial GPU resources. Pretraining at meaningful scale needs **8xH100** (or equivalent) GPUs. This is not deployable on the container host for training.

Suitable environments for training:
- Cloud burst on Lambda Labs, RunPod, or AWS p5 instances
- University/research cluster allocations
- Rented GPU time on vast.ai or similar

Inference of the trained model is much lighter and can run on a single GPU or even CPU for small models.

## Architecture: The Full Pipeline

### 1. Tokenization (`tokenize.py`)

Trains a BPE tokenizer on the target corpus. Produces a vocabulary file and merge rules.

```bash
python tokenize.py --input data/corpus.txt --vocab_size 32000
```

### 2. Pretraining (`pretrain.py`)

Standard autoregressive language model training. Supports:
- Multi-GPU via DDP/FSDP
- Mixed precision (bf16)
- Gradient accumulation
- Cosine learning rate schedule with warmup

```bash
torchrun --nproc_per_node=8 pretrain.py \
  --data_dir data/tokenized \
  --out_dir out/pretrained \
  --n_layer 32 --n_head 32 --n_embd 2048 \
  --batch_size 64 --max_iters 100000
```

### 3. Supervised Finetuning (`finetune.py`)

Finetunes the pretrained model on instruction-following data (e.g., ShareGPT, OpenAssistant format).

```bash
torchrun --nproc_per_node=8 finetune.py \
  --init_from out/pretrained \
  --data_dir data/sft \
  --out_dir out/sft
```

### 4. RLHF (`rlhf.py`)

Reward model training and PPO alignment. Requires preference data (chosen/rejected pairs).

### 5. Evaluation (`eval.py`)

Runs the model against standard benchmarks (HellaSwag, MMLU, etc.) to measure capability.

### 6. Chat (`chat.py`)

Interactive chat loop with the trained model. Supports system prompts, conversation history, and temperature control.

```bash
python chat.py --model out/sft/model.pt --temperature 0.7
```

## The `execution.py` Tool-Use Pattern

`execution.py` implements a tool-use / function-calling pattern that is directly relevant to agent design in Brain-and-Co:

- The model generates structured tool-call tokens (e.g., `<tool_call>{"name": "python", "code": "..."}`)
- The execution runtime intercepts these tokens, runs the tool, and injects the result back into the context
- The model then continues generation with the tool output available
- This creates an agentic loop: **think -> call tool -> observe result -> think again**

This pattern maps directly to how MCP tools work in Claude Code. The key design insight is that tool use is implemented as a special token sequence that the model learns during finetuning, not a separate system bolted on after training. Models trained this way have tool use as a native capability rather than a prompted behavior.

Relevant to Brain-and-Co agent design:
- The structured tool-call format could inform custom MCP tool schemas
- The observe-then-continue loop mirrors the Symphony task execution model
- Training data that includes tool-use examples produces models that naturally integrate with tool infrastructure

## Deploying Trained Models via Ollama

Once a model is trained with nanochat, it can be served on the container host through Ollama:

### 1. Export to GGUF

Convert the PyTorch checkpoint to GGUF format for Ollama compatibility:

```bash
# Use llama.cpp's conversion script
python convert_hf_to_gguf.py out/sft/ --outfile nanochat-model.gguf --outtype q4_K_M
```

### 2. Create an Ollama Modelfile

```
FROM ./nanochat-model.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|end|>"

SYSTEM "You are a helpful assistant."

TEMPLATE "{{ .System }}\n\n{{ .Prompt }}"
```

### 3. Register with Ollama on the container host

```bash
ssh ${DEPLOY_USER}@${CONTAINER_HOST_IP} "cd /path/to/model && ollama create nanochat -f Modelfile"
```

### 4. Query via the Ollama MCP wrapper

Once registered, the model is available through Brain-and-Co's existing Ollama MCP wrapper:

```
Ollama MCP endpoint: http://${CONTAINER_HOST_IP}:11434
Model name: nanochat
```

This means any Brain-and-Co agent or skill can call the custom-trained model through the same MCP infrastructure used for other Ollama models.

## Key Takeaways for Brain-and-Co

1. **Training is not container-host-viable** -- requires cloud GPU burst for any meaningful pretraining
2. **Inference is container-host-viable** -- small trained models can run on Ollama after GGUF conversion
3. **The tool-use pattern in `execution.py` is the most immediately useful component** -- it demonstrates how to train models that natively understand tool calling, which could improve custom agent behavior
4. **The full pipeline serves as a reference** for understanding what happens inside the models Brain-and-Co orchestrates via API calls
