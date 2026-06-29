# NOVA-X

**Next-Gen Omniscient Virtual Assistant -- eXtreme**

![CI](https://github.com/solasolago12-maker/NOVA-X/actions/workflows/ci.yml/badge.svg)

NOVA-X is a terminal-based AI assistant built for students, with support for multiple providers and specialized academic workflows. The app includes a Rich-powered TUI, subject tracking, assignment management, and safe Ollama endpoint handling.

## Features

- **Multi-provider AI**: Gemini, local Ollama, and OpenAI-compatible endpoints
- **Safe Ollama handling**: model names like `qwen2.5:7b` are never treated as server URLs
- **7 specialized modes**: chat, math, essay, code, research, quiz, and explain
- **Web search**: DuckDuckGo support for real-time research
- **Session history**: save, search, and recall past conversations
- **Export support**: TXT, Markdown, DOCX, PDF
- **Learning profile**: track subjects, strengths, and quiz performance
- **Beautiful terminal UI**: four themes and rich message rendering

## Installation

### Requirements

- Python 3.10 or higher
- `pip`

### Install

```bash
git clone <repository-url>
cd NOVA-X
pip install -r requirements.txt

Optional (local models):

For a local high-performance model using `llama-cpp-python` (CPU or GPU), install:

```bash
pip install "llama-cpp-python>=0.1.0"
```

You will also need a compatible GGML or GGUF model file. See `llama-cpp-python` documentation and model repositories (e.g. Hugging Face) for download instructions. Configure the model path in the NOVA-X setup or by setting `local_model_path` in `~/.nova_x/config.json`.

GPU notes and recommendations
---------------------------

llama-cpp-python can be built with GPU support (CUDA) for much faster inference on supported NVIDIA hardware. Quick tips:

- If you have an NVIDIA GPU, install `torch` with CUDA matching your drivers to enable detection, or ensure `nvidia-smi` is available.
- When running on CPU-only systems, choose an optimized GGUF model (quantized) for reasonable performance.
- Example: install `llama-cpp-python` and `torch` (CUDA) with:

```bash
# CPU-only (simplest)
pip install "llama-cpp-python>=0.1.0"

# GPU (example - choose the correct CUDA version for your system)
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install "llama-cpp-python>=0.1.0"
```

The engine performs a lightweight GPU detection at startup and will print guidance; advanced GPU/config options are left to users and model builds.

vllm (optional)
----------------

You can also use `vllm` as a high-performance GPU-first inference backend. Install and configure `vllm` separately and set `vllm_model_path` in the config. NOVA-X will detect `vllm` if installed and attempt to use it when `ai_provider` is set to `vllm`.

Example usage with the included example script:

```bash
python examples/run_local.py --model-path /path/to/model.gguf
```
```

### Run

**Windows:**

```cmd
run.bat
```

**macOS / Linux:**

```bash
./run.sh
```

**Directly:**

```bash
python nova_x.py
```

## Setup Wizard

Run the first-time setup wizard to configure your profile and AI provider:

```bash
python nova_x.py --setup
```

The wizard configures:

- user name and grade level
- AI provider selection
- Gemini/OpenAI API settings
- Ollama host and model settings
- subjects and theme preference

## Using Ollama

NOVA-X treats the Ollama host and model as separate values.

### Valid host formats

- `http://host:port`
- `https://host:port`
- `host:port` (normalized to `http://host:port`)

### Example

```bash
/provider set ollama host=http://localhost:11434 model=qwen2.5:7b
```

Model identifiers like `qwen2.5:7b` are never used as the host.

## Commands

| Command | Description |
|---------|-------------|
| `/quit`, `/exit` | Exit NOVA-X |
| `/help` | Show help screen |
| `/welcome` | Show welcome message |
| `/clear` | Clear current conversation |
| `/save [format]` | Export chat |
| `/history` | Show session history |
| `/stats` | Show learning statistics |
| `/mode <name>` | Change active mode |
| `/subjects` | List tracked subjects |
| `/subjects add <name>` | Add a subject |
| `/subjects remove <name>` | Remove a subject |
| `/assignments` | View assignments |
| `/quiz <subject>` | Start a quiz |
| `/explain <topic>` | Explain a topic |

## Modes

### Chat
General conversation and Q&A.

### Math
Solve math problems step-by-step.

### Essay
Outline, draft, and refine essays.

### Code
Write, debug, and explain code.

### Research
Search and summarize information.

### Quiz
Generate quizzes and practice questions.

### Explain
Simplify topics with analogies and summaries.

## Testing

Run the included test suite with:

```bash
python -m pytest -q
```

## Configuration

User settings are stored in `~/.nova_x/config.json`.

## Security

If you discover a security vulnerability, please report it privately to `security@nova-x.dev`. Do not open a public issue for sensitive security reports — see `SECURITY.md` for details.

## Notes

- Keep Ollama host URLs separate from model names.
- Use `/provider validate` in the TUI to check current provider configuration.
- The `.gitignore` file excludes Python artifacts, virtual environments, editor files, and test caches.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

