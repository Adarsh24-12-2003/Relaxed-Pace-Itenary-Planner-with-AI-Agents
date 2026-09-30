"""Flight, hotel, and activity workers."""

from __future__ import annotations

from models import TravelRequirements, WorkerDecision
from tools.travel_tools import search_activities, search_flights, search_hotels
from utils import ask_model


def _run_worker(
    worker_name: str,
    task: str,
    requirements: TravelRequirements,
    options: list[dict],
    id_field: str,
) -> dict:
    """Ask one specialist to choose only from its tool results."""
    if not options:
        raise ValueError(f"The {worker_name} tool found no matching options.")

    decision = ask_model(
        system_prompt=(
            f"You are the {worker_name} worker in a travel-planning team. {task} "
            "Use only the supplied tool results. Never invent an option. "
            "Summarise Reason, Action, Observation, and Decision without revealing "
            "private chain-of-thought. Return exact IDs in selected_ids."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "tool_results": options,
            "id_field": id_field,
        },
        output_model=WorkerDecision,
    )

    option_by_id = {option[id_field]: option for option in options}
    selected = [option_by_id[item_id] for item_id in decision.selected_ids if item_id in option_by_id]
    if not selected:
        raise ValueError(f"The {worker_name} worker did not select a valid option ID.")

    return {
        "trace": decision.model_dump(),
        "tool_results": options,
        "selected_options": selected,
    }


def run_flight_worker(requirements: TravelRequirements, flights: list[dict]) -> dict:
    options = search_flights(requirements, flights)
    return _run_worker(
        "flight",
        "Choose one flight that best respects route, timing, cost, and red-eye constraints.",
        requirements,
        options,
        "flight_id",
    )


def run_hotel_worker(requirements: TravelRequirements, hotels: list[dict]) -> dict:
    options = search_hotels(requirements, hotels)
    return _run_worker(
        "hotel",
        "Choose one hotel that best respects the full-stay budget, location, and preferences.",
        requirements,
        options,
        "hotel_id",
    )


def run_activity_worker(requirements: TravelRequirements, activities: list[dict]) -> dict:
    options = search_activities(requirements, activities)
    return _run_worker(
        "activities",
        "Choose a small pool of varied activities that match the interests and "
        "requested pace. For relaxed trips, prioritize options tagged 'relaxed-pace' "
        "or 'easy-pace', and avoid full-day or strenuous options unless specifically "
        "requested. The manager will schedule at most one main activity per day.",
        requirements,
        options,
        "activity_id",
    )
