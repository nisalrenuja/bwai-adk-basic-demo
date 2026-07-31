import dotenv
from google.adk.agents import LlmAgent, SequentialAgent

from trip_organizer_agent.instructions import (
    DESTINATION_RESEARCH_INSTRUCTION,
    ITINERARY_PLANNER_INSTRUCTION,
    LOGISTICS_PLANNER_INSTRUCTION,
    BUDGET_ESTIMATOR_INSTRUCTION,
    PACKING_AND_PREP_INSTRUCTION,
    FORMATTER_INSTRUCTION,
    TRIP_ORCHESTRATOR_INSTRUCTION
)

dotenv.load_dotenv()

# Shared by every sub-agent below.
MODEL_NAME = "gemini-3.1-flash-lite"

# --- Sub Agent 1: DestinationResearcher ---
# No tools: Google Search grounding needs a separate paid quota, so this agent
# researches from the model's own knowledge and states its assumptions instead.
destination_research_agent = LlmAgent(
    name="DestinationResearcher",
    model=MODEL_NAME,
    instruction=DESTINATION_RESEARCH_INSTRUCTION,
    output_key="destination_research"
)

# --- Sub Agent 2: ItineraryPlanner ---
itinerary_planner_agent = LlmAgent(
    name="ItineraryPlanner",
    model=MODEL_NAME,
    instruction=ITINERARY_PLANNER_INSTRUCTION,
    # This agent will automatically receive the output of the previous agent (DestinationResearcher)
    # and can also access other state variables if needed, e.g.,
    # instruction="Build a day-by-day itinerary from: {{state.destination_research}}"
    output_key="itinerary_plan"  # Save result to state under this key
)

# --- Sub Agent 3: LogisticsPlanner ---
logistics_planner_agent = LlmAgent(
    name="LogisticsPlanner",
    model=MODEL_NAME,
    instruction=LOGISTICS_PLANNER_INSTRUCTION,
    # instruction="Plan transport and stays for this itinerary: {{state.itinerary_plan}}"
    output_key="logistics_plan"  # Save result to state
)

# --- Sub Agent 4: BudgetEstimator ---
budget_estimator_agent = LlmAgent(
    name="BudgetEstimator",
    model=MODEL_NAME,
    instruction=BUDGET_ESTIMATOR_INSTRUCTION,
    # instruction="Estimate trip costs from: {{state.itinerary_plan}} and {{state.logistics_plan}}"
    output_key="budget_breakdown"  # Save result to state
)

# --- Sub Agent 5: PackingAndPrepAdvisor ---
packing_and_prep_agent = LlmAgent(
    name="PackingAndPrepAdvisor",
    model=MODEL_NAME,
    instruction=PACKING_AND_PREP_INSTRUCTION,
    # instruction="Suggest packing and pre-trip admin for: {{state.itinerary_plan}}"
    output_key="packing_and_prep"  # Save result to state
)

# --- Sub Agent 6: Formatter ---
# This agent will read multiple state keys and combine into the final Markdown
formatter_agent = LlmAgent(
    name="TripBriefFormatter",
    model=MODEL_NAME,
    instruction=FORMATTER_INSTRUCTION,
    output_key="final_trip_brief"  # Save final result to state
)

trip_orchestrator = SequentialAgent(
    name="TripOrganizerAssistant",
    description=TRIP_ORCHESTRATOR_INSTRUCTION,
    sub_agents=[
        destination_research_agent,
        itinerary_planner_agent,
        logistics_planner_agent,
        budget_estimator_agent,
        packing_and_prep_agent,
        formatter_agent,
    ]
)

root_agent = trip_orchestrator
