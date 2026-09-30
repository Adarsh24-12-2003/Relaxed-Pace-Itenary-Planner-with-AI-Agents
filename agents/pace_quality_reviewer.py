"""Pace and Quality Reviewer agent."""

from models import Critique, DraftItinerary, TravelRequirements
from utils import ask_model


def audit_itinerary(
    requirements: TravelRequirements,
    draft: DraftItinerary,
    worker_outputs: dict,
) -> Critique:
    """Review the draft and return specific repair instructions."""
    return ask_model(
        system_prompt=(
            "You are the independent Pace and Quality Reviewer in a travel-planning team. "
            "Check the draft against the user's requirements and grounded planner "
            "outputs. Focus on budget, pacing, preferences, constraints, and unsupported "
            "assumptions. For a relaxed itinerary, flag more than one main activity "
            "on any day, a lack of breaks or open time, and overfilled arrival or "
            "departure days. Do not replace inventory or rewrite the itinerary. Give "
            "actionable fixes."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "draft_itinerary": draft.model_dump(),
            "worker_outputs": worker_outputs,
        },
        output_model=Critique,
    )