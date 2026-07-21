# University Helpdesk Agent

University Helpdesk Agent is a beginner-friendly [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) demo for university workshops. It answers student questions about courses, exam schedules, registration, and campus facilities at a Sri Lankan university, using Python function tools to look up real data instead of guessing.

## Features

- A single ADK agent with a clear `root_agent` entry point
- Four tools covering courses, exam schedules, registration, and campus FAQs
- `Literal` type hints that constrain every tool argument to valid values
- Status-dict tool returns (`{"status": "success" | "error", ...}`) instead of raised exceptions
- An instruction prompt that asks a clarifying question when a request is ambiguous (e.g. exams without a department)

## Course catalogue

| Code | Course | Department | Semester | Lecturer |
| --- | --- | --- | --- | --- |
| CS2101 | Data Structures and Algorithms | IT | 2 | Dr. Perera |
| CS2102 | Database Management Systems | IT | 2 | Ms. Jayawardena |
| CS2103 | Software Engineering | IT | 2 | Dr. Fernando |
| CS2104 | Computer Networks | IT | 2 | Mr. Dissanayake |
| BM2101 | Marketing Management | Business | 2 | Ms. Silva |
| BM2102 | Financial Accounting | Business | 2 | Dr. Wijesinghe |
| EN2101 | Structural Analysis | Engineering | 2 | Prof. Rathnayake |
| EN2102 | Thermodynamics | Engineering | 2 | Dr. Bandara |

## Project structure

```text
.
├── helpdesk_agent/
│   ├── __init__.py
│   └── agent.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

Local credentials, virtual environments, Python caches, and ADK session data are excluded from Git.

## Prerequisites

Before you start, make sure you have the following. These are the minimum tools ADK needs to run an agent locally.

- **Python 3.10 or newer** — ADK is a Python framework, so you need a Python interpreter installed to run it at all. Check your version with `python3 --version`. If it's older than 3.10, install a newer Python from [python.org](https://www.python.org/downloads/) first.
- **A Google AI Studio API key or a configured Google Cloud project** — the agent's "brain" is a Gemini model, which runs on Google's servers, not on your laptop. You need credentials so your code is allowed to call that model. An [AI Studio](https://aistudio.google.com/) API key is the fastest option for a workshop; a Vertex AI project is the alternative if your organization already uses Google Cloud.
- **Git** — used to download (clone) this project's code to your machine.

## Setup

Each step below explains *why* it exists, not just what to type, so you understand what's happening to your machine.

1. Clone the repository and enter its directory.

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

   `git clone` downloads a copy of this project (all its files and history) from a remote location to your computer. `cd` ("change directory") then moves your terminal into that new folder, so every command you run afterward applies to this project instead of wherever you were before.

2. Create and activate a virtual environment.

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

   A virtual environment ("venv") is an isolated, self-contained copy of Python that lives inside a folder — here, `.venv` — just for this project. `python3 -m venv .venv` creates that folder. `source .venv/bin/activate` (or `Activate.ps1` on Windows) then tells your current terminal session "use the Python and packages inside `.venv`, not the system-wide ones." You'll know it worked because your terminal prompt will show `(.venv)` at the start of the line. You only need to activate it once per terminal session; deactivate any time with `deactivate`.

3. Install the dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

   `pip` is Python's package manager — it downloads and installs libraries from the Python Package Index (PyPI). `requirements.txt` is a plain text file listing exactly which libraries this project needs (in this case, the `google-adk` package and its dependencies) so that anyone setting up the project gets the same, known-working set instead of guessing what to install. Running this with your venv active means the libraries are installed *inside* `.venv`, keeping them isolated from other projects.

4. Create your local environment file.

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

   `.env.example` is a template checked into Git showing which configuration values the project expects (like which API key variable name to use) without containing any real secrets. Copying it to `.env` gives you your own private file to fill in. `.env` is listed in `.gitignore`, so Git will never track or upload it — this is what keeps your personal API key from accidentally ending up in a public repository.

5. Edit `.env` and provide either your Google AI Studio API key or your Vertex AI project settings. Never commit this file.

   ADK reads these environment variables at startup to know which Gemini model account to bill and authenticate against. Treat this file like a password: don't paste its contents into chat, screenshots, or commits.

## Run the agent

From the repository root, with the virtual environment active, run:

```bash
adk web
```

`adk web` is a command installed by the `google-adk` package (from step 3). It scans the current directory for agent folders like `helpdesk_agent/`, starts a local web server, and gives you a chat UI in the browser to talk to your agent — so you can test it interactively without writing any extra code. It prints a local URL (something like `http://localhost:8000`); open that in a browser and select `university_helpdesk` from the list of available agents. Stop the server anytime with `Ctrl+C` in the terminal.

## Example prompts

Courses:

- "Hi, I am a second-year IT student. What courses do I have this semester?"
- "What Business courses are available?"
- "Show me every course on offer."

Exams:

- "When is the exam for Database Management Systems?"
- "When are my exams?" (the agent will ask which department you're in)
- "What time and venue is the Software Engineering final?"

Registration:

- "I want to register for next semester. What do I need to do and what is the deadline?"
- "How much is the late registration fee?"

Campus info:

- "What time does the library close tonight?"
- "Where can I find hostel warden contacts?"
- "What are the clinic hours?"

## How it works

[`helpdesk_agent/agent.py`](helpdesk_agent/agent.py) defines the course, exam, registration, and campus data, four function tools, and the ADK agent:

- `list_courses` lists all courses or filters them by department and/or semester.
- `get_exam_schedule` returns exam dates, times, and venues for a department and semester.
- `get_registration_info` returns registration steps, deadlines, fees, and contacts.
- `get_campus_info` returns hours and contacts for library, canteen, hostel, clinic, sports, or general topics.

The agent is instructed to ground every answer in tool output, never guess, and ask one clarifying question when a request is ambiguous — for example, asking which department a student is in before looking up an exam schedule.

## Workshop extension ideas

- Replace the hardcoded data with a real database (PostgreSQL/MySQL via SQLAlchemy or `psycopg2`).
- Add a `submit_ticket` tool that logs student complaints or support requests.
- Add a `check_result` tool that looks up a student's grades by index number.
- Use ADK session state so the agent remembers a student's department across turns.
- Explore ADK multi-agent systems, with an orchestrator delegating to specialist sub-agents.

## Security

Keep API keys and cloud credentials only in your local `.env` file or a secure secret manager. If a secret is ever committed, revoke or rotate it before removing it from Git history.
