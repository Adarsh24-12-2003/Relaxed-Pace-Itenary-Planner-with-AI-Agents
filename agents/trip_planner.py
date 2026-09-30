"""Trip Planner agent for requirements and inventory selection."""

from models import TravelRequirements, TripPlanDecision
from tools.travel_tools import search_activities, search_flights, search_hotels
from utils import ask_model


def run_trip_planner(
    user_request: str,
    travel_data: dict[str, list[dict]],
) -> tuple[TravelRequirements, dict]:
    """Extract requirements, then select grounded transport, stay, and activities."""
    requirements = ask_model(
        system_prompt=(
            "You are the Trip Planner. Extract travel requirements from the user request. "
            "Use only supported information, put uncertainty in assumptions, and do "
            "not invent dates or budgets. Default pace_preference to 'relaxed' unless "
            "the user clearly asks for a balanced or packed itinerary."
        ),
        payload={"user_request": user_request},
        output_model=TravelRequirements,
    )
    flight_options = search_flights(requirements, travel_data["flights"])
    hotel_options = search_hotels(requirements, travel_data["hotels"])
    activity_options = search_activities(requirements, travel_data["activities"])
    if not flight_options:
        raise ValueError("The Trip Planner found no flights for the requested route.")
    if not hotel_options:
        raise ValueError("The Trip Planner found no hotels at the destination.")
    if not activity_options:
        raise ValueError("The Trip Planner found no activities at the destination.")

    decision = ask_model(
        system_prompt=(
            "You are the Trip Planner continuing the same request. Select exactly one "
            "flight and one hotel, plus a small varied pool of activities, from the "
            "supplied inventories. Respect route, red-eye preference, hotel budget, "
            "interests, and requested pace. For relaxed trips, favor 'relaxed-pace' or "
            "'easy-pace' activities and avoid full-day options unless requested. Return "
            "exact IDs only. Explain the decision and trade-offs without revealing "
            "private chain-of-thought."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "flight_options": flight_options,
            "hotel_options": hotel_options,
            "activity_options": activity_options,
        },
        output_model=TripPlanDecision,
    )

    flights_by_id = {option["flight_id"]: option for option in flight_options}
    hotels_by_id = {option["hotel_id"]: option for option in hotel_options}
    activities_by_id = {option["activity_id"]: option for option in activity_options}
    if decision.selected_flight_id not in flights_by_id:
        raise ValueError("The Trip Planner selected an unknown flight ID.")
    if decision.selected_hotel_id not in hotels_by_id:
        raise ValueError("The Trip Planner selected an unknown hotel ID.")
    if not decision.selected_activity_ids:
        raise ValueError("The Trip Planner did not select any activities.")
    if len(decision.selected_activity_ids) != len(set(decision.selected_activity_ids)):
        raise ValueError("The Trip Planner selected a duplicate activity ID.")
    if not set(decision.selected_activity_ids).issubset(activities_by_id):
        raise ValueError("The Trip Planner selected an unknown activity ID.")

    trace = decision.model_dump()
    worker_outputs = {
        "flight": {
            "trace": trace,
            "tool_results": flight_options,
            "selected_options": [flights_by_id[decision.selected_flight_id]],
        },
        "hotel": {
            "trace": trace,
            "tool_results": hotel_options,
            "selected_options": [hotels_by_id[decision.selected_hotel_id]],
        },
        "activities": {
            "trace": trace,
            "tool_results": activity_options,
            "selected_options": [
                activities_by_id[item_id]
                for item_id in decision.selected_activity_ids
            ],
        },
    }
    return requirements, worker_outputs