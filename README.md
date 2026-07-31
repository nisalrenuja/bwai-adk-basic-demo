# ADK Agent Demos

A beginner-friendly [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) workshop repository containing two agents that demonstrate two different ADK patterns.

| Agent | Folder | Pattern | Docs |
| --- | --- | --- | --- |
| University Helpdesk | [`helpdesk_agent/`](helpdesk_agent/) | Single agent + function tools | [README](helpdesk_agent/README.md) |
| Trip Organizer | [`trip_organizer_agent/`](trip_organizer_agent/) | `SequentialAgent` pipeline | [README](trip_organizer_agent/README.md) |

Start with `helpdesk_agent/` - it shows the fundamentals (one agent, tools, an instruction prompt). Then move to `trip_organizer_agent/` to see multiple agents chained together through shared session state.

## The agents

### University Helpdesk - `helpdesk_agent/`

A single ADK agent that answers student questions about courses, exam schedules, registration procedures, and campus facilities at a Sri Lankan university. Four Python function tools look up real data so the agent never guesses, `Literal` type hints constrain every tool argument to valid values, and the prompt makes the agent ask one clarifying question when a request is ambiguous - for example, asking which department a student is in before looking up an exam schedule.

Try: *"Hi, I am a second-year IT student. What courses do I have this semester?"* or *"When are my exams?"*

→ **[Full documentation](helpdesk_agent/README.md)** - tools, data, customizing, troubleshooting.

### Trip Organizer - `trip_organizer_agent/`

A multi-agent trip planner. Give it a one-line request and it returns a complete Markdown trip brief: destination research, a day-by-day itinerary, transport and accommodation logistics, a budget estimate, and a packing checklist. A `SequentialAgent` runs six specialist `LlmAgent`s in a fixed order - `PlaceFinder` → `DayPlanner` → `TravelPlanner` → `CostEstimator` → `PackingHelper` → `TripWriter` - each writing its result into session state for the next one to read. No sub-agent currently uses a tool - they reason over what is already in state, and `PlaceFinder` works from the model's training data. Adding `google_search` back is the headline upgrade, documented in [Taking It Further](trip_organizer_agent/README.md#taking-it-further-google-search-grounding).

Try: *"Plan a 5-day trip to Sigiriya and the Cultural Triangle in February for two people."*

→ **[Full documentation](trip_organizer_agent/README.md)** - the pipeline, prompts, customizing, limitations.

## Project structure

```text
.
├── helpdesk_agent/
│   ├── __init__.py
│   ├── agent.py            # data, four function tools, the Agent
│   ├── .env.example        # per-agent config template
│   └── README.md
├── trip_organizer_agent/
│   ├── __init__.py
│   ├── agent.py            # the SequentialAgent pipeline
│   ├── instructions.py     # prompts for every sub-agent
│   ├── .env.example        # per-agent config template
│   └── README.md
├── .env.example            # shared config template (repository root)
├── .gitignore
├── README.md
└── requirements.txt
```

Local credentials, virtual environments, Python caches, and ADK session data are excluded from Git.

## Prerequisites

Before you start, make sure you have the following. These are the minimum tools ADK needs to run an agent locally.

- **Python 3.10 or newer** - ADK is a Python framework, so you need a Python interpreter installed to run it at all. Check your version with `python3 --version`. If it's older than 3.10, install a newer Python from [python.org](https://www.python.org/downloads/) first.
- **A Google AI Studio API key or a configured Google Cloud project** - the agent's "brain" is a Gemini model, which runs on Google's servers, not on your laptop. You need credentials so your code is allowed to call that model. An [AI Studio](https://aistudio.google.com/apikey) API key is the fastest option for a workshop; a Vertex AI project is the alternative if your organization already uses Google Cloud.
- **Git** - used to download (clone) this project's code to your machine.

## Setup

Each step below explains *why* it exists, not just what to type, so you understand what's happening to your machine. One setup serves both agents.

1. Clone the repository and enter its directory.

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

   `git clone` downloads a copy of this project (all its files and history) from a remote location to your computer. `cd` ("change directory") then moves your terminal into that new folder, so every command you run afterward applies to this project instead of wherever you were before.

2. Create and activate a virtual environment, at the **repository root**.

   macOS/Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **What is a virtual environment, and why bother?** Every Python project needs its own set of installed packages (libraries), often at specific versions. If you installed everything globally on your machine, two projects that need different versions of the same package would conflict, and eventually your system Python would become a tangle of incompatible libraries.

   A virtual environment ("venv") is an isolated, self-contained copy of Python that lives inside a folder - here, `.venv` - just for this project. `python3 -m venv .venv` creates that folder. `source .venv/bin/activate` (or `Activate.ps1` on Windows) then tells your current terminal session "use the Python and packages inside `.venv`, not the system-wide ones." You'll know it worked because your terminal prompt will show `(.venv)` at the start of the line. You only need to activate it once per terminal session; deactivate any time with `deactivate`.

3. Install the dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

   `pip` is Python's package manager - it downloads and installs libraries from the Python Package Index (PyPI). `requirements.txt` is a plain text file listing exactly which libraries this project needs (here, `google-adk` and `python-dotenv`, plus their dependencies) so that anyone setting up the project gets the same, known-working set instead of guessing what to install. Running this with your venv active means the libraries are installed *inside* `.venv`, keeping them isolated from other projects.

4. Create your local environment file.

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

   `.env.example` is a template checked into Git showing which configuration values the project expects (like which API key variable name to use) without containing any real secrets. Copying it to `.env` gives you your own private file to fill in. `.env` is listed in `.gitignore`, so Git will never track or upload it - this is what keeps your personal API key from accidentally ending up in a public repository.

5. Edit `.env` and provide either your Google AI Studio API key or your Vertex AI project settings. Never commit this file.

   ADK reads these environment variables at startup to know which Gemini model account to bill and authenticate against. Treat this file like a password: don't paste its contents into chat, screenshots, or commits.

## Configuration

You can configure the agents in either of two places:

| Location | Template to copy | Use when |
| --- | --- | --- |
| Repository root `.env` | `.env.example` | One key for both agents. Simplest, and what a workshop usually wants. |
| `helpdesk_agent/.env`, `trip_organizer_agent/.env` | that folder's `.env.example` | You want each agent on its own key, project, or model. |

**When you run under `adk web` or `adk run`, the agent's own `.env` wins.** ADK searches upward
from the agent folder and stops at the first `.env` it finds, so a file inside
`trip_organizer_agent/` takes priority over the one at the root.

Each `agent.py` also calls `load_dotenv()` itself, so the agents still work in a plain script or
notebook where ADK's CLI never runs. That call searches upward from your **current working
directory**, so from the repository root it picks up the root `.env` and does not see a per-agent
one. In short: per-agent `.env` files are honoured by ADK, and the root `.env` is the reliable
choice everywhere else.

A variable exported in your shell beats every `.env`, because `load_dotenv` never overwrites
something already set.

All `.env` files are gitignored at any depth; the `.env.example` templates are tracked.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `GOOGLE_GENAI_USE_VERTEXAI` | Yes | `FALSE` | `FALSE` to authenticate with an API key, `TRUE` to use Vertex AI |
| `GOOGLE_API_KEY` | When not using Vertex AI | - | Your Google AI Studio / Gemini API key |
| `GOOGLE_CLOUD_PROJECT` | When using Vertex AI | - | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | When using Vertex AI | - | Region, e.g. `us-central1` |
| `GOOGLE_GENAI_MODEL` | No | `gemini-3.1-flash-lite` | Model both agents use. Each falls back to the default if unset |

If you set `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, drop `GOOGLE_API_KEY` and set up application-default credentials first with `gcloud auth application-default login`.

## Run the agents

From the repository root, with the virtual environment active, run:

```bash
adk web
```

`adk web` is a command installed by the `google-adk` package (from step 3). It scans the current directory for agent folders like `helpdesk_agent/` and `trip_organizer_agent/`, starts a local web server, and gives you a chat UI in the browser to talk to your agents - so you can test them interactively without writing any extra code. It prints a local URL (something like `http://localhost:8000`); open that in a browser and pick an agent from the dropdown. Stop the server anytime with `Ctrl+C` in the terminal.

You can also run a single agent straight from the terminal:

```bash
adk run helpdesk_agent
adk run trip_organizer_agent
```

Always run these from the repository root - `trip_organizer_agent/agent.py` imports `trip_organizer_agent.instructions`, so the parent directory has to be on the Python path.

### If port 8000 is already in use

```
ERROR: [Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): address already in use
```

An earlier `adk web` is still running. This happens easily: closing the terminal does not always stop the server, and a process started in the background can be orphaned and keep holding the port.

Find it and stop it:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN     # see what is holding the port
lsof -ti:8000 | xargs kill           # stop it
```

If it refuses to die, `lsof -ti:8000 | xargs kill -9`. Or just use a different port and leave the old one alone:

```bash
adk web --port 9000
```

On Windows PowerShell the equivalent lookup is `Get-NetTCPConnection -LocalPort 8000`, then `Stop-Process -Id <pid>`.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Agent dropdown is empty in `adk web` | Started the server from the wrong directory | Run `adk web` from the repository root, which contains the agent folders |
| `ModuleNotFoundError: No module named 'trip_organizer_agent'` | Running from inside the agent folder | `cd` to the repository root and run `adk run trip_organizer_agent` from there |
| `command not found: adk` | Virtual environment not active | `source .venv/bin/activate` (or `.venv\Scripts\Activate.ps1`) |
| `Warning: python-dotenv not installed` | Dependencies not installed, or wrong venv | Activate the venv and run `python -m pip install -r requirements.txt` |
| `401` / `API key not valid` | Missing or wrong `GOOGLE_API_KEY` | Check your `.env`; regenerate the key at [AI Studio](https://aistudio.google.com/apikey) |
| `[Errno 48] address already in use` on port 8000 | An earlier `adk web` is still running, often orphaned after its terminal closed | `lsof -ti:8000 \| xargs kill` to stop it, or start on another port with `adk web --port 9000` |
| `429 RESOURCE_EXHAUSTED` | Free-tier rate limit - the trip organizer's six sequential agents burn quota fast | Wait and retry, use a lighter model, or enable billing |
| `429` only after adding `google_search` | Grounding is billed separately from the model | See [the isolation test](trip_organizer_agent/README.md#the-catch-grounding-is-billed-separately) |

Agent-specific troubleshooting lives in each agent's own README.

## Security

Keep API keys and cloud credentials only in your local `.env` file or a secure secret manager. If a secret is ever committed, revoke or rotate it before removing it from Git history.
