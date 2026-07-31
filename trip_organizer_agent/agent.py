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

# --- Sub Agent 1: PlaceFinder ---
# No tools: Google Search grounding needs a separate paid quota, so this agent
# researches from the model's own knowledge and states its assumptions instead.
place_finder_agent = LlmAgent(
    name="PlaceFinder",
    model=MODEL_NAME,
    instruction=DESTINATION_RESEARCH_INSTRUCTION,
    output_key="destination_research"
)

# --- Sub Agent 2: DayPlanner ---
day_planner_agent = LlmAgent(
    name="DayPlanner",
    model=MODEL_NAME,
    instruction=ITINERARY_PLANNER_INSTRUCTION,
    # This agent will automatically receive the output of the previous agent (PlaceFinder)
    # and can also access other state variables if needed, e.g.,
    # instruction="Build a day-by-day itinerary from: {{state.destination_research}}"
    output_key="itinerary_plan"  # Save result to state under this key
)

# --- Sub Agent 3: TravelPlanner ---
travel_planner_agent = LlmAgent(
    name="TravelPlanner",
    model=MODEL_NAME,
    instruction=LOGISTICS_PLANNER_INSTRUCTION,
    # instruction="Plan transport and stays for this itinerary: {{state.itinerary_plan}}"
    output_key="logistics_plan"  # Save result to state
)

# --- Sub Agent 4: CostEstimator ---
cost_estimator_agent = LlmAgent(
    name="CostEstimator",
    model=MODEL_NAME,
    instruction=BUDGET_ESTIMATOR_INSTRUCTION,
    # instruction="Estimate trip costs from: {{state.itinerary_plan}} and {{state.logistics_plan}}"
    output_key="budget_breakdown"  # Save result to state
)

# --- Sub Agent 5: PackingHelper ---
packing_helper_agent = LlmAgent(
    name="PackingHelper",
    model=MODEL_NAME,
    instruction=PACKING_AND_PREP_INSTRUCTION,
    # instruction="Suggest packing and pre-trip admin for: {{state.itinerary_plan}}"
    output_key="packing_and_prep"  # Save result to state
)

# --- Sub Agent 6: TripWriter ---
# This agent will read multiple state keys and combine into the final Markdown
trip_writer_agent = LlmAgent(
    name="TripWriter",
    model=MODEL_NAME,
    instruction=FORMATTER_INSTRUCTION,
    output_key="final_trip_brief"  # Save final result to state
)

trip_planner = SequentialAgent(
    name="TripPlanner",
    description=TRIP_ORCHESTRATOR_INSTRUCTION,
    sub_agents=[
        place_finder_agent,
        day_planner_agent,
        travel_planner_agent,
        cost_estimator_agent,
        packing_helper_agent,
        trip_writer_agent,
    ]
)

root_agent = trip_planner
