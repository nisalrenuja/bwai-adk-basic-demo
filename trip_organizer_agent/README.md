# Trip Organizer Agent

A multi-agent trip planner built with **Google's Agent Development Kit (ADK)**. You give it a
one-line trip request - *"Plan a 5-day trip to Sigiriya and the Cultural Triangle in February for
two people"* - and it returns a complete Markdown trip brief: destination research, a day-by-day
itinerary, transport and accommodation logistics, a budget estimate, and a packing/prep checklist.

It is the second agent in this workshop repository, and demonstrates the `SequentialAgent` pattern:
a fixed pipeline of specialist `LlmAgent`s that hand work to each other through shared session
state. If you haven't yet, start with [`helpdesk_agent/`](../helpdesk_agent/README.md) - one agent,
a few tools - then come back here.

---

## Table of Contents

- [How It Works](#how-it-works)
- [The Agents](#the-agents)
- [Project Files](#project-files)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Agent](#running-the-agent)
- [Example Session](#example-session)
- [Customizing the Agent](#customizing-the-agent)
- [Taking It Further: Google Search Grounding](#taking-it-further-google-search-grounding)
- [Troubleshooting](#troubleshooting)
- [Notes and Limitations](#notes-and-limitations)

---

## How It Works

The root agent is a `SequentialAgent` named `TripPlanner`. It runs six sub-agents in a
fixed order. Each sub-agent writes its result into session state under an `output_key`, and later
agents read those keys from their instructions.

```
User request
     │
     ▼
┌────────────────────────────┐
│ 1. PlaceFinder             │  ← no tools; see "Taking It Further"
│    → destination_research  │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 2. DayPlanner              │    reads: destination_research
│    → itinerary_plan        │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 3. TravelPlanner           │    reads: itinerary_plan, destination_research
│    → logistics_plan        │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 4. CostEstimator           │    reads: destination_research, itinerary_plan, logistics_plan
│    → budget_breakdown      │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 5. PackingHelper           │    reads: destination_research, itinerary_plan
│    → packing_and_prep      │
└────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│ 6. TripWriter              │    reads: all of the above
│    → final_trip_brief      │
└────────────────────────────┘
     │
     ▼
Final Markdown trip brief
```

There is no routing logic or LLM-driven delegation here - the order is deterministic. That is the
point of `SequentialAgent`: the pipeline is predictable and each step is independently testable.

## The Agents

| # | Agent | Tools | State key written | Responsibility |
|---|-------|-------|-------------------|----------------|
| 1 | `PlaceFinder` | - | `destination_research` | Attractions, best time to visit, weather, local transport, typical costs, safety, visa/entry notes |
| 2 | `DayPlanner` | - | `itinerary_plan` | Day-by-day plan (morning/afternoon/evening), grouped geographically, with travel times |
| 3 | `TravelPlanner` | - | `logistics_plan` | Transport per transition, which areas to stay in, what to book in advance |
| 4 | `CostEstimator` | - | `budget_breakdown` | Per-category cost ranges, per-person and whole-trip totals, daily spend |
| 5 | `PackingHelper` | - | `packing_and_prep` | Packing list, documents and admin, local practicalities (currency, plugs, SIM, etiquette) |
| 6 | `TripWriter` | - | `final_trip_brief` | Merges everything into one Markdown brief, preserving earlier caveats |

**No sub-agent currently has a tool.** Agent 1 researches from the model's own training data;
agents 2–6 are pure reasoning steps over what is already in session state. That keeps a full run
cheap - a five-day trip completes in roughly 25 seconds - but it means the facts are *remembered*,
not looked up. [Taking It Further](#taking-it-further-google-search-grounding) explains the
trade-off and how to add live search.

## Project Files

```
trip_organizer_agent/
├── __init__.py        # exposes `agent` so ADK can discover root_agent
├── agent.py           # agent definitions + the SequentialAgent pipeline
├── instructions.py    # the system prompt for every sub-agent
└── README.md          # this file
```

`agent.py` exports `root_agent`, which is the symbol ADK's CLI and web UI look for when loading an
agent folder. `instructions.py` is kept separate so prompts can be edited without touching wiring.

## Prerequisites

- **Python 3.11+** (required by Google ADK 2.0+)
- **pip**
- A **Google API key** with access to Gemini models - get one free at
  [Google AI Studio](https://aistudio.google.com/apikey)

Verify your Python version:

```bash
python3 --version
```

## Installation

Run these from the **repository root**, not from inside this folder - `agent.py` imports
`trip_organizer_agent.instructions`, so the parent directory must be on the Python path.

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
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GOOGLE_API_KEY` | Yes | - | Your Google AI Studio / Gemini API key |
| `GOOGLE_GENAI_USE_VERTEXAI` | No | `FALSE` | Set to `TRUE` to authenticate through Vertex AI instead of an API key |

The model is **not** configured here - it is pinned in code as the `MODEL_NAME` constant in
[`agent.py`](agent.py), the same way `helpdesk_agent` pins its own. See
[Change the model](#change-the-model).

If you set `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, drop `GOOGLE_API_KEY` and provide
`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` instead, with application-default credentials
already set up (`gcloud auth application-default login`).

> `.env` is listed in `.gitignore`, so your real key stays local. Keep placeholder values only in
> `.env.example` - that file **is** tracked by git.

## Running the Agent

All commands are run from the repository root with the virtualenv active.

### Option 1 - Web UI (recommended)

The web UI is the best way to see the pipeline execute, because it shows each sub-agent's output
and the session state as it fills up.

```bash
adk web .
```

Then open <http://localhost:8000>, pick **trip_organizer_agent** from the agent dropdown, and send
your trip request in the chat box.

Useful flags:

```bash
adk web . --port 9000                        # different port
adk web . --session_service_uri sqlite://sessions.db   # persist sessions to disk
```

### Option 2 - CLI, single request

```bash
adk run trip_organizer_agent "Plan a 5-day trip to Sigiriya and the Cultural Triangle in February for two people"
```

### Option 3 - CLI, interactive

Omit the query to get an interactive prompt where you can iterate:

```bash
adk run trip_organizer_agent
```

### Option 4 - API server

Expose the agent over HTTP for use from your own frontend or scripts:

```bash
adk api_server .
```

Then call it:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "trip_organizer_agent",
    "user_id": "u1",
    "session_id": "s1",
    "new_message": {
      "role": "user",
      "parts": [{"text": "Plan a 4-day trip to Ella and the hill country in March for two people, mid budget"}]
    }
  }'
```

Create the session first if the server requires it:

```bash
curl -X POST http://localhost:8000/apps/trip_organizer_agent/users/u1/sessions/s1
```

## Example Session

**Input:**

```
Plan a 5-day trip from Colombo to Sigiriya and the Cultural Triangle in February for two
people, budget around LKR 150,000 total, interested in ancient sites and wildlife.
```

**What happens:**

1. `PlaceFinder` reports February weather in the dry zone (the best window for the
   Cultural Triangle), Sigiriya Rock Fortress and Dambulla Cave Temple, Polonnaruwa and Minneriya,
   and how to get there from Colombo - flagging ticket prices and opening hours as things to verify,
   since it has no live search.
2. `DayPlanner` produces Day 1–5 with morning/afternoon/evening blocks: the Sigiriya climb at
   dawn before the heat and the crowds, Pidurangala for the view back at the rock, Dambulla on the
   way past, Polonnaruwa by bicycle on a full day, and a Minneriya or Kaudulla safari at dusk.
3. `TravelPlanner` recommends a van and driver versus the Colombo→Habarana bus, suggests basing
   all four nights in Sigiriya or Habarana rather than moving hotels, and flags the safari jeep and
   the Sigiriya ticket as things to sort out in advance.
4. `CostEstimator` breaks the LKR 150,000 into transport, accommodation, food, site tickets - and
   notes that foreign-national rates at Sigiriya and Polonnaruwa are far higher than local rates,
   so the total swings hard on that assumption - safari jeep hire, and a contingency.
5. `PackingHelper` covers sun protection and water for the climb, shoulder-and-knee cover
   for the cave temple, leech socks if you're extending into the hills, plug type G, and cash for
   places outside Colombo that don't take cards.
6. `TripWriter` merges it all into one Markdown document.

**Output:** a single Markdown brief with sections for *Trip at a Glance*, *Destination Overview*,
*Itinerary*, *Logistics*, *Budget*, and *Packing & Preparation*.

**More to try:**

- "Plan a 3-day trip to Ella for two people in March - Nine Arch Bridge, Little Adam's Peak, and
  the train from Kandy."
- "Plan a weekend in Galle for four friends, staying inside the Fort."
- "Plan a 4-day wildlife trip to Yala and Udawalawe in August, budget around LKR 120,000."
- "Plan a 10-day first visit to Sri Lanka in December for two people, budget around USD 2,500 -
  Cultural Triangle, hill country, and the south coast beaches."

The more specific your request - dates, traveller count, budget, nationality, interests, pace - the
better the plan. When you leave something out, the agents state the assumption they used instead of
inventing a fact. Nationality matters more than you'd expect here: local and foreign ticket prices
at Sri Lankan heritage sites differ by an order of magnitude, and entry requirements (ETA) only
apply to inbound travellers.

## Customizing the Agent

### Change the model

One constant near the top of `agent.py` feeds all six sub-agents:

```python
MODEL_NAME = "gemini-3.1-flash-lite"
```

Change it there and every step picks it up. To give a single sub-agent a different model, pass
`model=` explicitly on that one:

```python
budget_estimator_agent = LlmAgent(
    name="CostEstimator",
    model="gemini-2.5-pro",   # override just this step
    instruction=BUDGET_ESTIMATOR_INSTRUCTION,
    output_key="budget_breakdown",
)
```

### Edit a prompt

Every prompt lives in `instructions.py` as a module-level constant. Editing
`BUDGET_ESTIMATOR_INSTRUCTION` changes only the budget step; nothing else needs to move.

### Add a sub-agent

1. Write its instruction constant in `instructions.py`.
2. Define the `LlmAgent` in `agent.py` with a unique `output_key`.
3. Insert it into the `sub_agents` list at the position you want it to run.
4. Reference its `output_key` from the instructions of any downstream agent that needs it -
   including `FORMATTER_INSTRUCTION` if it should appear in the final brief.

### Reference state explicitly

Sub-agents see prior output through session state. You can also interpolate a state key straight
into an instruction:

```python
instruction="Build a day-by-day itinerary from: {destination_research}"
```

`agent.py` keeps commented examples of this next to each sub-agent.

### Give another agent a tool

Import from `google.adk.tools` (or pass your own Python function) and add it to a `tools` list on
the `LlmAgent`. See [Taking It Further](#taking-it-further-google-search-grounding) for the
worked example, and [`helpdesk_agent`](../helpdesk_agent/README.md) for custom function tools.

## Taking It Further: Google Search Grounding

This is the single most valuable upgrade to this agent, and it is a two-line change.

### Where the facts come from today

`PlaceFinder` has no tools, so everything in the brief comes from the model's **training
data**. That works better than you might expect for well-documented places: the model already
"knows" the Sigiriya rock fortress, the dress code at Dambulla Cave Temple, that Polonnaruwa is
best explored by bicycle, and that February is dry season in the Cultural Triangle. None of that
needs a live lookup.

But the Sigiriya entry fee or the safari jeep rate in your brief is a *remembered* number, not a
looked-up one. You can confirm no search is happening - a grounded response carries extra fields:

```bash
# Run the agent via the API server, then inspect the response for grounding evidence
grep -o 'groundingMetadata\|webSearchQueries\|groundingChunks' response.json
# no output = the model answered from training data alone
```

### What grounding buys you

| | Without `google_search` (now) | With `google_search` |
|---|---|---|
| Facts from | training data (fixed cutoff) | live web results |
| Prices, hours, schedules | possibly outdated, no way to tell | current |
| Citations | none | source links returned |
| Cost | model tokens only | tokens **plus** a separate grounding quota |
| Latency | ~25s for a 5-day trip | slower - the search round-trip is added |

### How to add it

1. Import the tool and attach it to the research agent in `agent.py`:

   ```python
   from google.adk.tools import google_search

   destination_research_agent = LlmAgent(
       name="PlaceFinder",
       model=MODEL_NAME,
       instruction=DESTINATION_RESEARCH_INSTRUCTION,
       tools=[google_search],          # ← add this
       output_key="destination_research"
   )
   ```

2. Update step 2 of `DESTINATION_RESEARCH_INSTRUCTION` in `instructions.py` to tell the agent the
   tool exists, and drop the "you have no live search" caveat step:

   ```
   2. Use the available Google Search tool to gather relevant information: top attractions,
      best time to visit, local transport, typical costs, safety notes, and entry requirements.
      Prioritize recent and authoritative sources.
   ```

3. Restart the server - unlike `.env`, code changes are not picked up on the fly.

### The catch: grounding is billed separately

Grounding with Google Search draws on **its own quota, independent of the model**. A project can be
perfectly able to call Gemini and still be refused for search. The symptom is a `429` on the very
first sub-agent while every other step would have worked:

```
429 RESOURCE_EXHAUSTED
"You exceeded your current quota, please check your plan and billing details."
```

Two details identify this as a grounding problem rather than ordinary rate limiting:

- the error carries **no `RetryInfo` and no `QuotaFailure` metric** - a hard denial, not a burst
  limit you can wait out;
- the same model, same key, **succeeds without tools and fails with them**, seconds apart.

That isolation test is worth running before you blame the key or the model:

```bash
K=$(awk -F= '/^GOOGLE_API_KEY=/{print $2}' .env)
U="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

# A - no tools
curl -s -o /dev/null -w "no tools: %{http_code}\n" -H "x-goog-api-key: $K" \
  -H "Content-Type: application/json" -X POST "$U" \
  -d '{"contents":[{"parts":[{"text":"Say OK"}]}]}'

# B - same call with grounding
curl -s -o /dev/null -w "grounded: %{http_code}\n" -H "x-goog-api-key: $K" \
  -H "Content-Type: application/json" -X POST "$U" \
  -d '{"contents":[{"parts":[{"text":"Entry fee for Sigiriya?"}]}],"tools":[{"google_search":{}}]}'
```

`200` then `429` means the model is fine and grounding is not enabled - set up billing for
Grounding with Google Search on the project, or leave the agent tool-less.

### Why it is worth doing anyway

Ungrounded, this agent is a *plausible* trip planner. Grounded, it is a *current* one - and the
difference shows up exactly where it hurts most: ticket prices, opening hours, and transport
schedules. It is also the honest thing to demonstrate. An agent that confidently states a stale
entry fee with no citation is the failure mode worth showing an audience, not hiding from them.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'trip_organizer_agent'` | Running from inside the agent folder | `cd` to the repository root and run `adk run trip_organizer_agent` from there |
| `Warning: python-dotenv not installed` | Dependencies not installed, or wrong venv | Activate the venv and run `pip install -r requirements.txt` |
| `401` / `API key not valid` | Missing or wrong `GOOGLE_API_KEY` | Check `.env` at the repository root; regenerate the key in Google AI Studio |
| Agent dropdown is empty in `adk web` | Started the server from the wrong directory | Run `adk web .` from the repository root, which contains the agent folders |
| `429 RESOURCE_EXHAUSTED` | Free-tier rate limit - six sequential agents burn quota fast | Wait and retry, use a lighter model, or enable billing. If the error says `limit: 0`, that project has no free-tier allowance at all and waiting won't help |
| `429` on the **first** sub-agent only, after adding `google_search` | Grounding is billed separately from the model | See [the isolation test](#the-catch-grounding-is-billed-separately) - `200` without tools and `429` with them means grounding isn't enabled |
| `command not found: adk` | Virtualenv not active | `source .venv/bin/activate` |
| Brief quotes a stale price or opening hour | Expected - no live search; facts come from training data | Treat every number as indicative, or [add grounding](#taking-it-further-google-search-grounding) |

Enable verbose logging to see the raw model traffic:

```bash
adk run trip_organizer_agent --log_level DEBUG "Plan a weekend in Galle"
```

## Notes and Limitations

- **Nothing here is looked up live.** With no `google_search`, every fact comes from the model's
  training data, which has a fixed cutoff. Prices, opening hours, and schedules may be out of date,
  and there are no citations to check them against. This is the limitation that
  [grounding](#taking-it-further-google-search-grounding) removes.
- **Costs and prices are estimates, not quotes.** The budget agent is explicitly told to say so.
  Verify fares and rates before booking.
- **Visa, entry, and health requirements change often.** The packing agent tells you to confirm
  against the official government source for your nationality. Do that.
- **A full run makes six sequential model calls.** On a free-tier key a long trip can hit rate
  limits partway through the pipeline.
- **No live availability or pricing.** The agent does not connect to booking APIs; it plans, it
  doesn't reserve.
- **The pipeline is one-shot.** `SequentialAgent` runs each step once, in order - there is no loop
  back to revise an earlier step. To iterate, send a new, more specific request.

## Related Modules

- [`helpdesk_agent/`](../helpdesk_agent/README.md) - the foundation this builds on: a single
  `Agent` with four Python function tools over hardcoded data.

## License

MIT - see the repository root.
