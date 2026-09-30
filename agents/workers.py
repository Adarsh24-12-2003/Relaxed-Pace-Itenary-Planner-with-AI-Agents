"""Flight, hotel, and activity specialist agents."""

from models import TravelRequirements, WorkerDecision
from tools.travel_tools import search_activities, search_flights, search_hotels
from utils import ask_model


def _run_worker(
    worker_name: str,
    task: str,
    requirements: TravelRequirements,
    options: list[dict],
    id_field: str,
    selection_limit: int | None = None,
) -> dict:
    """Ask a specialist to choose only valid IDs from its local inventory."""
    if not options:
        raise ValueError(f"The {worker_name} search found no matching options.")

    decision = ask_model(
        system_prompt=(
            f"You are the {worker_name} Specialist. {task} Use only the supplied "
            "inventory and return exact IDs in selected_ids. Do not invent options. "
            f"Set worker to '{worker_name}'. Give concise reason, action, observation, "
            "decision, and tradeoffs without revealing private chain-of-thought."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "tool_results": options,
            "id_field": id_field,
        },
        output_model=WorkerDecision,
    )

    if decision.worker != worker_name:
        raise ValueError(f"The {worker_name} Specialist returned the wrong worker type.")
    option_by_id = {option[id_field]: option for option in options}
    if not decision.selected_ids:
        raise ValueError(f"The {worker_name} Specialist selected no options.")
    if len(decision.selected_ids) != len(set(decision.selected_ids)):
        raise ValueError(f"The {worker_name} Specialist selected duplicate IDs.")
    if not set(decision.selected_ids).issubset(option_by_id):
        raise ValueError(f"The {worker_name} Specialist selected an unknown option ID.")
    if selection_limit is not None and len(decision.selected_ids) != selection_limit:
        raise ValueError(
            f"The {worker_name} Specialist must select exactly {selection_limit} option."
        )

    return {
        "trace": decision.model_dump(),
        "tool_results": options,
        "selected_options": [option_by_id[item_id] for item_id in decision.selected_ids],
    }


def run_flight_worker(requirements: TravelRequirements, flights: list[dict]) -> dict:
    """Select one route- and timing-appropriate flight."""
    return _run_worker(
        "flight",
        "Choose exactly one flight that respects route, timing, cost, and red-eye constraints.",
        requirements,
        search_flights(requirements, flights),
        "flight_id",
        selection_limit=1,
    )


def run_hotel_worker(requirements: TravelRequirements, hotels: list[dict]) -> dict:
    """Select one hotel for the destination and full trip stay."""
    return _run_worker(
        "hotel",
        "Choose exactly one hotel that best respects the full-stay budget, location, and preferences.",
        requirements,
        search_hotels(requirements, hotels),
        "hotel_id",
        selection_limit=1,
    )


def run_activity_worker(
    requirements: TravelRequirements,
    activities: list[dict],
) -> dict:
    """Select a small pool of varied activities for the requested interests and pace."""
    return _run_worker(
        "activities",
        "Choose a small, varied pool of activities matching the interests and requested pace. "
        "For relaxed trips, prioritize 'relaxed-pace' or 'easy-pace' activities and avoid "
        "full-day or strenuous options unless specifically requested.",
        requirements,
        search_activities(requirements, activities),
        "activity_id",
    )