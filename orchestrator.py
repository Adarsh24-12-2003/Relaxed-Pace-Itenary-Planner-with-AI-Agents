"""Deterministic workflow orchestration for the travel-planning agents."""

from agents.itinerary_composer import create_draft, display_plan, refine_itinerary
from agents.pace_quality_reviewer import audit_itinerary
from agents.trip_planner import run_trip_planner
from tools.travel_tools import load_travel_data


def run_pipeline(user_request: str) -> dict:
    """Run analysis, planning, composition, review, and revision."""
    requirements, worker_outputs = run_trip_planner(
        user_request,
        load_travel_data(),
    )

    draft = create_draft(requirements, worker_outputs)
    critique = audit_itinerary(requirements, draft, worker_outputs)
    final = refine_itinerary(requirements, draft, critique, worker_outputs)

    return {
        "requirements": requirements.model_dump(),
        "worker_outputs": worker_outputs,
        "draft_itinerary": draft.model_dump(),
        "critique": critique.model_dump(),
        "final_output": display_plan(final, worker_outputs),
    }