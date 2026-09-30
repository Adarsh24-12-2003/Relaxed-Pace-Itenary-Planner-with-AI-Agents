"""Deterministic workflow orchestration for the travel-planning agents."""

from agents.critic import critique_itinerary
from agents.manager import create_draft, display_plan, extract_requirements, refine_itinerary
from agents.workers import run_activity_worker, run_flight_worker, run_hotel_worker
from tools.travel_tools import load_travel_data


def run_pipeline(user_request: str) -> dict:
    """Run analysis, planning, composition, review, and revision."""
    travel_data = load_travel_data()
    requirements = extract_requirements(user_request)
    worker_outputs = {
        "flight": run_flight_worker(requirements, travel_data["flights"]),
        "hotel": run_hotel_worker(requirements, travel_data["hotels"]),
        "activities": run_activity_worker(requirements, travel_data["activities"]),
    }

    draft = create_draft(requirements, worker_outputs)
    critique = critique_itinerary(requirements, draft, worker_outputs)
    final = refine_itinerary(requirements, draft, critique, worker_outputs)

    return {
        "requirements": requirements.model_dump(),
        "worker_outputs": worker_outputs,
        "draft_itinerary": draft.model_dump(),
        "critique": critique.model_dump(),
        "final_output": display_plan(final, worker_outputs),
    }