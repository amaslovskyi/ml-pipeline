# 📁 Evaluation Directory Structure

This document outlines the organized structure of the evaluation directory for better maintainability and ease of use.

## 📂 Directory Overview

```
eval/
├── evaluation-scripts/     # Core evaluation and testing scripts
├── server-tools/          # FastAPI server and client tools
├── ollama-tools/          # Ollama model creation and testing
├── documentation/         # Evaluation summaries and guides
├── results/              # Evaluation results and performance data
└── README.md             # Main evaluation documentation
```

## 🔧 evaluation-scripts/

**Purpose**: Core evaluation and performance testing scripts

| **File**                         | **Purpose**                                   | **Usage**                               |
| -------------------------------- | --------------------------------------------- | --------------------------------------- |
| `devops_model_evaluation.py`     | Comprehensive 20-question DevOps evaluation   | `python devops_model_evaluation.py`     |
| `quick_devops_test.py`           | Quick 5-question evaluation test              | `python quick_devops_test.py`           |
| `model_comparison.py`            | Compare fine-tuned vs base model              | `python model_comparison.py`            |
| `performance_report.py`          | Generate detailed performance reports         | `python performance_report.py`          |
| `laptop_performance_analysis.py` | Analyze system resources for model deployment | `python laptop_performance_analysis.py` |
| `run_evaluation.py`              | Automated evaluation runner                   | `python run_evaluation.py`              |

## 🖥️ server-tools/

**Purpose**: FastAPI server and client interaction tools

| **File**                     | **Purpose**                          | **Usage**                           |
| ---------------------------- | ------------------------------------ | ----------------------------------- |
| `direct_inference_server.py` | FastAPI server for model inference   | `python direct_inference_server.py` |
| `run_direct_server.sh`       | Script to start the inference server | `./run_direct_server.sh`            |
| `chat_client.py`             | Interactive command-line chat client | `python chat_client.py`             |
| `quick_test.py`              | Server health and endpoint testing   | `python quick_test.py`              |

## 🦙 ollama-tools/

**Purpose**: Ollama model creation and testing utilities

| **File**                        | **Purpose**                            | **Usage**                              |
| ------------------------------- | -------------------------------------- | -------------------------------------- |
| `create_ollama_devops_model.py` | Create DevOps-optimized Ollama model   | `python create_ollama_devops_model.py` |
| `test_ollama_models.py`         | Compare base vs DevOps Ollama models   | `python test_ollama_models.py`         |
| `ollama_usage_guide.md`         | Complete guide for using Ollama models | Documentation                          |

## 📖 documentation/

**Purpose**: Evaluation summaries and user guides

| **File**                | **Purpose**                             |
| ----------------------- | --------------------------------------- |
| `EVALUATION_SUMMARY.md` | Executive summary of evaluation results |
| `QUICK_START.md`        | Quick start guide for evaluation tools  |

## 📊 results/

**Purpose**: Generated evaluation results and performance data

- `*.json` files containing evaluation results
- Performance metrics and comparison data
- Timestamped evaluation reports

## 🚀 Quick Start Commands

### Run Complete Evaluation
```bash
cd evaluation-scripts/
python run_evaluation.py
```

### Start Inference Server
```bash
cd server-tools/
./run_direct_server.sh
```

### Create Ollama DevOps Model
```bash
cd ollama-tools/
python create_ollama_devops_model.py
```

### Quick Performance Test
```bash
cd evaluation-scripts/
python quick_devops_test.py
```

## 🔧 Dependencies

Each subdirectory contains tools that work independently. Key requirements:
- **evaluation-scripts/**: torch, transformers, peft
- **server-tools/**: fastapi, uvicorn, torch, transformers, peft
- **ollama-tools/**: ollama CLI installed

## 📝 Notes

- All scripts support both local LoRA adapter and HuggingFace Hub models
- Server tools use CPU device mapping to avoid MPS issues on Apple Silicon
- Ollama tools require the `qwen3:8b` base model to be downloaded
- Results are automatically timestamped and saved to the `results/` directory

---

**🎯 Remember**: This organized structure ensures easy maintenance, clear separation of concerns, and improved workflow efficiency for model evaluation tasks.
