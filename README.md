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

- Python 3.10 or newer
- A Google AI Studio API key or a configured Google Cloud project

## Setup

1. Clone the repository and enter its directory.

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

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

3. Install the dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create your local environment file.

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Edit `.env` and provide either your Google AI Studio API key or your Vertex AI project settings. Never commit this file.

## Run the agent

From the repository root, with the virtual environment active, run:

```bash
adk web
```

Open the local URL printed by ADK and select `university_helpdesk`.

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
