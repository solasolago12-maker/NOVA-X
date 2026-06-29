# NOVA-X

**Next-Gen Omniscient Virtual Assistant -- eXtreme**

NOVA-X is an AI-powered homework assistant that runs in your terminal. It supports multiple AI providers (Gemini, Ollama, OpenAI), features 7 specialised modes for different academic tasks, and tracks your learning progress over time.
Ollama host/model handling
---------------------------

When configuring the Ollama provider, NOVA-X treats the host (endpoint)
and the model identifier as separate values. Model identifiers commonly use
colons (for example `qwen2.5:7b`) and must not be misinterpreted as a
host. The CLI and TUI perform strict validation and normalization:

- Acceptable host formats:
  - `http://host:port` or `https://host:port` (any path is stripped)
  - `host:port` (normalized to `http://host:port`)
- Model identifiers (e.g. `qwen2.5:7b`) are never treated as hosts.

Use `/provider set ollama host=http://localhost:11434 model=qwen2.5:7b`
or the setup wizard to configure Ollama safely. You can validate current
settings in the TUI with `/provider validate`.


```
    _   _______  _____  __   _________  __
   / | / / __ \/   \ \/ /  / ____/   |/  /
  /  |/ / / / / /| |\  /  / / __/ /|_/  /
 / /|  / /_/ / ___ |/ /  / /_/ / /  /  /
/_/ |_/_____/_/  |_/_/   \____/_/  /__/
```

## Features

- **7 Specialised Modes**: Chat, Math Solver, Essay Writer, Code Helper, Research Assistant, Quiz Generator, and Explainer
- **Multi-Provider AI**: Supports Google Gemini, local Ollama models, and OpenAI-compatible APIs
- **Web Search**: DuckDuckGo integration for real-time research
- **Learning Profile**: Tracks subjects, weak areas, strong areas, and quiz performance
- **Assignment Tracker**: Manage deadlines and priorities
- **Export**: Save conversations as TXT, Markdown, DOCX, or PDF
- **Session History**: Automatically saves and can search past sessions
- **Beautiful TUI**: Rich-powered terminal interface with 4 themes (dark, light, neon, minimal)

## Screenshots

The TUI features:
- A mode sidebar with keyboard shortcuts
- Styled chat messages with Markdown rendering
- Welcome screen with quick-start guide
- Statistics dashboard
- Assignment overview panel

## Installation

### Requirements
- Python 3.10 or higher
- pip package manager

### Quick Install
```bash
git clone <repository-url>
cd NOVA-X
pip install -r requirements.txt
```

### Platform Launchers

**Windows:**
```cmd
run.bat
```

**macOS / Linux:**
```bash
./run.sh
```

Or directly with Python:
```bash
python nova_x.py
```

## Setup Wizard

On first run, NOVA-X will guide you through setup:
```bash
python nova_x.py --setup
```

This configures:
- Your name and grade level
- AI provider (Gemini, Ollama, or OpenAI)
- API keys / host settings
- Subjects you want to track
- Visual theme preference

## VS Code Integration

You can run NOVA-X directly from VS Code's integrated terminal:
1. Open the project folder in VS Code
2. Open a terminal (`Ctrl+` `` ` ``)
3. Run: `python nova_x.py`

For a dedicated terminal profile, add to your VS Code settings.json:
```json
{
  "terminal.integrated.profiles.linux": {
    "NOVA-X": {
      "path": "bash",
      "args": ["-c", "cd /path/to/NOVA-X && ./run.sh"]
    }
  }
}
```

## Mode Guide

### Chat Mode (default)
General conversation and Q&A with the AI.
```
[Chat] > What is photosynthesis?
```

### Math Mode
Step-by-step math problem solving with work checking.
```
[Math Solver] > solve 2x + 5 = 13
[Math Solver] > check x = 4
```

### Essay Mode
Essay planning, drafting, and improvement.
```
[Essay Writer] > outline The Impact of Climate Change
[Essay Writer] > draft <paste your outline here>
[Essay Writer] > improve <paste your essay here>
```

### Code Mode
Programming help with write, debug, explain, and run commands.
```
[Code Helper] > write a function to sort a list using quicksort
[Code Helper] > debug <paste your code here>
[Code Helper] > run print([x**2 for x in range(10)])
```

### Research Mode
Web search and deep research with synthesis.
```
[Research Assistant] > search history of the Roman Empire
[Research Assistant] > deep artificial intelligence in education
```

### Quiz Mode
Generate and take interactive quizzes.
```
[Quiz Generator] > start World Geography
```

### Explain Mode
Simplified explanations with analogies and summaries.
```
[Explainer] > analogy quantum computing
[Explainer] > summarize <paste text here>
[Explainer] > terms photosynthesis
```

## Keyboard Shortcuts / Commands

| Command | Description |
|---------|-------------|
| `/quit`, `/exit` | Exit NOVA-X |
| `/help` | Show full help screen |
| `/welcome` | Show welcome screen |
| `/clear` | Clear current conversation |
| `/save [format]` | Export chat (txt/md/docx/pdf) |
| `/history` | List past sessions |
| `/stats` | Show learning statistics |
| `/mode <name>` | Switch to a different mode |
| `/subjects` | List tracked subjects |
| `/subjects add <name>` | Add a subject |
| `/subjects remove <name>` | Remove a subject |
| `/assignments` | View upcoming assignments |
| `/quiz <subject>` | Start a quiz on a subject |
| `/explain <topic>` | Explain a topic |

## Configuration

Configuration is stored in `~/.nova_x/config.json`:

```json
{
  "ai_provider": "gemini",
  "gemini_api_key": "YOUR_API_KEY",
  "gemini_model": "gemini-2.0-flash",
  "ollama_host": "http://localhost:11434",
  "ollama_model": "llama3.2",
  "openai_api_key": "",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-4o-mini",
  "theme": "dark",
  "user_name": "",
  "grade_level": "",
  "subjects": [],
  "first_run": false
}
```

For Ollama with `qwen2.5:7b`, set:

```json
{
  "ai_provider": "ollama",
  "ollama_host": "http://localhost:11434",
  "ollama_model": "qwen2.5:7b"
}
```

Data files stored in `~/.nova_x/`:
- `config.json` -- Application settings
- `profile.json` -- Learning profile and statistics
- `subjects.json` -- Subject and assignment tracking
- `history/` -- Saved conversation sessions

## Troubleshooting

### "No AI provider configured"
Run `python nova_x.py --setup` to configure your AI provider and API key.

### "Gemini client not initialised"
Install the Google Generative AI SDK: `pip install google-generativeai`
Ensure your Gemini API key is set in the config.

### "Ollama request failed"
Make sure Ollama is running locally: `ollama serve`
Verify the host URL in config (default: http://localhost:11434).

If you are using `qwen2.5:7b`, confirm the model is installed by running:
```bash
ollama list
```
Use the exact model name shown by Ollama, for example `qwen2.5:7b`.

### Module not found errors
Install all dependencies: `pip install -r requirements.txt`

### Rich not found / TUI won't launch
NOVA-X will automatically fall back to a simple CLI mode if Rich is not installed.
Install Rich for the full TUI experience: `pip install rich`

### Permission denied on run.sh
Make the script executable: `chmod +x run.sh`
