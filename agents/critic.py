"""Critic Agent for independent itinerary review."""

from models import Critique, DraftItinerary, TravelRequirements
from utils import ask_model


def critique_itinerary(
    requirements: TravelRequirements,
    draft: DraftItinerary,
    worker_outputs: dict,
) -> Critique:
    """Review the draft against requirements and provide actionable fixes."""
    return ask_model(
        system_prompt=(
            "You are the Critic Agent on a travel-planning team. Review the draft "
            "against the user's requirements and specialist-approved options. Focus "
            "on budget, pacing, preferences, constraints, and unsupported assumptions. "
            "For a relaxed itinerary, flag more than one main activity on a day, lack "
            "of breaks or open time, and overfilled arrival or departure days. Do not "
            "replace inventory or rewrite the itinerary. Give specific repair guidance."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "draft_itinerary": draft.model_dump(),
            "worker_outputs": worker_outputs,
        },
        output_model=Critique,
    )