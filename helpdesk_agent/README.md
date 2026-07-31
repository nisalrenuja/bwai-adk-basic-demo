# University Helpdesk Agent

A single-agent helpdesk built with **Google's Agent Development Kit (ADK)**. It answers student
questions about courses, exam schedules, registration procedures, and campus facilities at a Sri
Lankan university - grounding every answer in Python function tools rather than guessing.

It is the starting point of this workshop repository, and demonstrates the most fundamental ADK
pattern: **one `Agent`, a handful of function tools, and an instruction prompt**. Once this makes
sense, [`trip_organizer_agent/`](../trip_organizer_agent/README.md) shows how to chain several
agents together.

---

## Table of Contents

- [How It Works](#how-it-works)
- [The Tools](#the-tools)
- [The Data](#the-data)
- [Project Files](#project-files)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Agent](#running-the-agent)
- [Example Session](#example-session)
- [Customizing the Agent](#customizing-the-agent)
- [Troubleshooting](#troubleshooting)
- [Notes and Limitations](#notes-and-limitations)

---

## How It Works

There is one agent, `university_helpdesk`. When a student sends a message, the model reads the
instruction prompt, decides which (if any) tool answers the question, calls it, and writes a reply
from what came back.

```
Student question
     │
     ▼
┌──────────────────────────┐
│  university_helpdesk     │  ← instruction prompt: never guess,
│  (google Gemini model)   │     ground every answer in tool output,
└──────────────────────────┘     ask ONE clarifying question if unclear
     │
     │  the model picks a tool based on the question
     ├──────────────┬──────────────────┬─────────────────┐
     ▼              ▼                  ▼                 ▼
list_courses   get_exam_schedule  get_registration_  get_campus_info
     │              │              info                  │
     ▼              ▼                  ▼                 ▼
  COURSES     EXAM_SCHEDULE     REGISTRATION_INFO    CAMPUS_INFO
     └──────────────┴──────────────────┴─────────────────┘
                            │
                            ▼
              {"status": "success", ...} back to the model
                            │
                            ▼
                    Natural-language answer
```

Three design choices are worth noticing, because they are the habits that make ADK agents behave:

1. **The tools are ordinary Python functions.** ADK reads their signature, type hints, and
   docstring to build the schema it shows the model. The docstring *is* the tool documentation the
   model sees - vague docstrings produce wrong tool calls.
2. **Arguments are constrained with `Literal`.** `department: Literal["IT", "Business",
   "Engineering", "Science"]` means the model cannot invent a department name; the set of valid
   values is part of the schema.
3. **Tools return a status dict, never an exception.** Every tool returns
   `{"status": "success", ...}` or `{"status": "error", "message": ...}`. A raised exception would
   break the run; a returned error is something the model can read and explain to the student.

## The Tools

| Tool | Arguments | Returns |
|------|-----------|---------|
| `list_courses` | `department` *(optional)*, `semester` *(optional)* | All courses, or those matching the filters, plus a count |
| `get_exam_schedule` | `department` *(required)*, `semester` *(required)* | Exam date, time, venue, and duration for each course in that department and semester |
| `get_registration_info` | - | Registration steps, deadlines, late fee, finance-division hours, contacts |
| `get_campus_info` | `topic` *(required)* | Hours and contacts for `library`, `canteen`, `hostel`, `clinic`, `sports`, or `general` |

Both `list_courses` filters are optional, so "show me every course" and "what Business courses are
there?" hit the same tool. `get_exam_schedule` deliberately requires both arguments - that is what
makes the agent ask *"which department are you in?"* instead of guessing, which is the clarifying
behaviour the prompt asks for.

## The Data

All data is hardcoded at the top of `agent.py` as plain Python lists and dicts. There is no
database - that is intentional for a workshop, and replacing it is the first extension exercise.

**Course catalogue** (`COURSES`)

| Code | Course | Department | Semester | Credits | Lecturer |
|------|--------|------------|----------|---------|----------|
| CS2101 | Data Structures and Algorithms | IT | 2 | 3 | Dr. Perera |
| CS2102 | Database Management Systems | IT | 2 | 3 | Ms. Jayawardena |
| CS2103 | Software Engineering | IT | 2 | 3 | Dr. Fernando |
| CS2104 | Computer Networks | IT | 2 | 3 | Mr. Dissanayake |
| BM2101 | Marketing Management | Business | 2 | 3 | Ms. Silva |
| BM2102 | Financial Accounting | Business | 2 | 3 | Dr. Wijesinghe |
| EN2101 | Structural Analysis | Engineering | 2 | 4 | Prof. Rathnayake |
| EN2102 | Thermodynamics | Engineering | 2 | 3 | Dr. Bandara |

**Exam schedule** (`EXAM_SCHEDULE`) - one entry per course above, with date, time, venue, and
duration in hours.

**Registration** (`REGISTRATION_INFO`) - the six-step portal procedure, the deadline and late
deadline, the late fee, finance-division hours, and the registrar's contact details.

**Campus facilities** (`CAMPUS_INFO`) - six topics: `library`, `canteen`, `hostel`, `clinic`,
`sports`, and `general` (main office, security, student affairs, wifi).

> `Science` is a valid value in the `department` `Literal` but has no courses or exams in the data.
> Asking for Science exams is the easiest way to see the `{"status": "error"}` path in action.

## Project Files

```
helpdesk_agent/
├── __init__.py     # package marker
├── agent.py        # data, four function tools, and the Agent definition
├── .env.example    # config template for this agent (copy to .env)
└── README.md       # this file
```

`agent.py` exports `root_agent`, which is the symbol ADK's CLI and web UI look for when loading an
agent folder. The file is organized in three commented sections - Data, Tools, Agent - so you can
read it top to bottom.

## Prerequisites

- **Python 3.10+**
- **pip**
- A **Google API key** with access to Gemini models - get one free at
  [Google AI Studio](https://aistudio.google.com/apikey)

Verify your Python version:

```bash
python3 --version
```

## Installation

Run these from the **repository root**, not from inside this folder - `adk` discovers agents by
scanning the directory you run it from.

```bash
# 1. Clone the repo (skip if you already have it)
git clone <your-repository-url>
cd <repository-directory>

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

Confirm the ADK CLI is available:

```bash
adk --version
```

## Configuration

Copy the template at the repository root and fill in your key:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOOGLE_API_KEY` | Yes | Your Google AI Studio / Gemini API key |
| `GOOGLE_GENAI_USE_VERTEXAI` | No | Set to `TRUE` to authenticate through Vertex AI instead of an API key |
| `GOOGLE_GENAI_MODEL` | No | Model this agent uses. Defaults to `gemini-3.1-flash-lite` |

If you set `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, drop `GOOGLE_API_KEY` and provide
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` instead, with application-default credentials
already set up (`gcloud auth application-default login`).

Copy [`.env.example`](.env.example) in this folder to `.env` if you want this agent on its own key
or model; ADK prefers it over the repository root `.env`. Otherwise the root `.env` is used. See
[Change the model](#change-the-model).

> `.env` is listed in `.gitignore`, so your real key stays local. Keep placeholder values only in
> `.env.example` - that file **is** tracked by git.

## Running the Agent

All commands are run from the repository root with the virtualenv active.

### Option 1 - Web UI (recommended)

The web UI is the best way to learn, because it shows each tool call and its raw return value
alongside the conversation.

```bash
adk web
```

Then open <http://localhost:8000> and pick **helpdesk_agent** from the agent dropdown.

Useful flags:

```bash
adk web --port 9000                                    # different port
adk web --session_service_uri sqlite://sessions.db     # persist sessions to disk
```

### Option 2 - CLI, single request

```bash
adk run helpdesk_agent "When are the IT semester 2 exams?"
```

### Option 3 - CLI, interactive

Omit the query to get an interactive prompt where you can iterate:

```bash
adk run helpdesk_agent
```

### Option 4 - API server

Expose the agent over HTTP for use from your own frontend or scripts:

```bash
adk api_server
```

Then call it:

```bash
curl -X POST http://localhost:8000/apps/helpdesk_agent/users/u1/sessions/s1

curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "helpdesk_agent",
    "user_id": "u1",
    "session_id": "s1",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What time does the library close on Saturday?"}]
    }
  }'
```

## Example Session

**Courses**

```
> Hi, I am a second-year IT student. What courses do I have this semester?
```

The model calls `list_courses(department="IT", semester=2)` and lists the four CS2xxx courses with
their lecturers and credits.

**The clarifying question** - the behaviour worth demonstrating in a workshop:

```
> When are my exams?
```

`get_exam_schedule` requires a department, and the student didn't give one. Instead of guessing,
the agent replies:

```
Happy to help! Which department are you in - IT, Business, or Engineering?
```

```
> IT
```

Now it calls `get_exam_schedule(department="IT", semester=2)` and returns the four exam dates,
times, and venues.

**The error path**

```
> When are the Science exams?
```

`get_exam_schedule(department="Science", semester=2)` returns
`{"status": "error", "message": "No exam schedule found for Science, Semester 2."}` and the agent
tells the student no schedule is published, rather than inventing one.

**More to try**

| Topic | Prompt |
|-------|--------|
| Courses | "What Business courses are available?" · "Show me every course on offer." |
| Exams | "When is the exam for Database Management Systems?" · "What time and venue is the Software Engineering final?" |
| Registration | "What do I need to do to register, and what's the deadline?" · "How much is the late registration fee?" |
| Campus | "What time does the library close tonight?" · "Where can I find hostel warden contacts?" · "What are the clinic hours?" |

## Customizing the Agent

### Change the model

The model comes from `.env`, with a fallback pinned near the top of `agent.py`:

```python
MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-3.1-flash-lite")
```

Set `GOOGLE_GENAI_MODEL` in `.env` to switch models without editing code, or change the fallback.
`trip_organizer_agent` uses the identical pattern.

### Edit the instruction prompt

The prompt is the `instruction=` string in the `Agent` definition. It does three jobs: sets the
persona, maps question types to tools, and mandates the one-clarifying-question rule. Change one
line at a time and watch the behaviour shift - removing *"Never guess or make up information"* is a
memorable demo of why the line is there.

### Add a tool

1. Write a plain Python function with type hints and a docstring (the docstring is what the model
   reads).
2. Return a status dict - `{"status": "success", ...}` or `{"status": "error", "message": ...}` -
   rather than raising.
3. Add the function to the `tools=[...]` list in the `Agent` definition.
4. Mention when to use it in the instruction prompt.

```python
def submit_ticket(
    category: Literal["academic", "facilities", "finance", "it"],
    message: str,
) -> dict:
    """Log a student support ticket.

    Args:
        category: The department the ticket should be routed to.
        message: The student's description of the issue.

    Returns:
        The generated ticket reference.
    """
    ticket_id = f"TKT-{len(message):04d}"
    return {"status": "success", "ticket_id": ticket_id, "category": category}
```

### Replace the hardcoded data

The tools are the only thing that touch `COURSES`, `EXAM_SCHEDULE`, `REGISTRATION_INFO`, and
`CAMPUS_INFO`. Swap those module constants for real database queries (SQLAlchemy, `psycopg2`) and
the agent, prompt, and tool signatures stay exactly the same - which is the point of putting the
lookup behind a function.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Agent dropdown is empty in `adk web` | Started the server from the wrong directory | Run `adk web` from the repository root, which contains the agent folders |
| `command not found: adk` | Virtualenv not active | `source .venv/bin/activate` |
| `401` / `API key not valid` | Missing or wrong `GOOGLE_API_KEY` | Check this folder's `.env` first, then the repository root one; regenerate the key in Google AI Studio |
| `404` / model not found | The chosen model isn't available on your key | Set `GOOGLE_GENAI_MODEL` in `.env` to a model your key can access, or change the fallback in `agent.py` |
| `Warning: python-dotenv not installed` printed at startup | `agent.py` catches the missing import and carries on, so `.env` is never read | Activate the venv and run `pip install -r requirements.txt`; without it you must export `GOOGLE_API_KEY` yourself |
| Agent answers without calling a tool | The prompt or docstrings don't make the mapping obvious | Tighten the tool docstrings and the "when a student asks X, use Y" lines in the instruction |
| Agent asks for a department every time | `get_exam_schedule` requires both arguments by design | Give the department in your question, or make the parameter optional with a default |

Enable verbose logging to see the raw model traffic and tool calls:

```bash
adk run helpdesk_agent --log_level DEBUG "When are the IT exams?"
```

## Notes and Limitations

- **The data is fictional and hardcoded.** Courses, dates, fees, and contacts are workshop
  placeholders, not a real university's records.
- **The exam dates are in 2025** and the registration deadlines have passed. The agent reports them
  as-is; it has no concept of today's date.
- **No memory across turns.** Each `adk run` invocation starts fresh unless you enable a session
  service - the agent will ask a returning student for their department again. Persisting that is
  an extension exercise.
- **No authentication.** There is no notion of *which* student is asking, so there is nothing
  student-specific (grades, fee balance, personal timetable) it can look up.
- **`Science` is accepted but empty.** It is a valid `Literal` value with no backing data, which
  exercises the error path.

## Related Modules

- [`trip_organizer_agent/`](../trip_organizer_agent/README.md) - the next step: a `SequentialAgent`
  pipeline of six sub-agents that pass work through shared session state.

## License

MIT - see the repository root.
