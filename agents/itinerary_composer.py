"""Itinerary composition and deterministic validation."""

from models import BudgetBreakdown, Critique, DraftItinerary, FinalItinerary, TravelRequirements
from tools.travel_tools import estimate_budget
from utils import ask_model


def _selected_inventory(worker_outputs: dict) -> tuple[dict, dict, list[dict]]:
    flight = worker_outputs["flight"]["selected_options"][0]
    hotel = worker_outputs["hotel"]["selected_options"][0]
    activities = worker_outputs["activities"]["selected_options"]
    return flight, hotel, activities


def _composer_context(worker_outputs: dict) -> dict:
    """Give the composer agent decisions and approved records."""
    return {
        name: {
            "decision": output["trace"]["decision"],
            "tradeoffs": output["trace"]["tradeoffs"],
            "selected_options": output["selected_options"],
        }
        for name, output in worker_outputs.items()
    }


def _ground_itinerary(
    itinerary: DraftItinerary,
    requirements: TravelRequirements,
    worker_outputs: dict,
) -> None:
    """Verify IDs and replace model arithmetic with tool-calculated totals."""
    flight, hotel, activities = _selected_inventory(worker_outputs)
    allowed_activity_ids = {item["activity_id"] for item in activities}

    if itinerary.selected_flight_id != flight["flight_id"]:
        raise ValueError("Itinerary Composer selected a flight outside the Trip Planner's result.")
    if itinerary.selected_hotel_id != hotel["hotel_id"]:
        raise ValueError("Itinerary Composer selected a hotel outside the Trip Planner's result.")

    planned_ids = [item_id for day in itinerary.days for item_id in day.activity_ids]
    if not set(planned_ids).issubset(allowed_activity_ids):
        raise ValueError("Itinerary Composer used an activity outside the Trip Planner's result.")
    if len(planned_ids) != len(set(planned_ids)):
        raise ValueError("Itinerary Composer repeated an activity on multiple days.")
    if len(itinerary.days) != requirements.duration_days:
        raise ValueError("Itinerary Composer created the wrong number of day blocks.")

    activity_limit = {"relaxed": 1, "balanced": 2, "packed": 3}[
        requirements.pace_preference
    ]
    if any(len(day.activity_ids) > activity_limit for day in itinerary.days):
        raise ValueError(
            f"Itinerary Composer exceeded the {requirements.pace_preference} pace limit "
            f"of {activity_limit} activities per day."
        )

    planned_activity_ids = set(planned_ids)
    planned_activities = [
        item for item in activities if item["activity_id"] in planned_activity_ids
    ]
    itinerary.budget = BudgetBreakdown(
        **estimate_budget(requirements, flight, hotel, planned_activities)
    )


def _enforce_daily_pace(
    itinerary: DraftItinerary,
    requirements: TravelRequirements,
    worker_outputs: dict,
) -> list[str]:
    """Move overflow activities into open days or leave them unscheduled."""
    activity_limit = {"relaxed": 1, "balanced": 2, "packed": 3}[
        requirements.pace_preference
    ]
    activities = {
        item["activity_id"]: item
        for item in worker_outputs["activities"]["selected_options"]
    }
    overflow = []
    for index, day in enumerate(itinerary.days):
        overflow.extend((index, item_id) for item_id in day.activity_ids[activity_limit:])
        day.activity_ids = day.activity_ids[:activity_limit]

    adjustments = []
    for source_index, activity_id in overflow:
        source_day = itinerary.days[source_index]
        target = next(
            (
                day
                for day in itinerary.days[source_index + 1 :]
                if len(day.activity_ids) < activity_limit
            ),
            None,
        )
        if target is None:
            target = next(
                (
                    day
                    for day in itinerary.days[:source_index]
                    if len(day.activity_ids) < activity_limit
                ),
                None,
            )

        activity_name = activities.get(activity_id, {}).get("name", activity_id)
        if target is None:
            adjustment = (
                f"Left {activity_name} unscheduled because the trip had no open "
                f"day within the {requirements.pace_preference} pace limit."
            )
            source_day.notes += f" {activity_name} was left unscheduled to preserve downtime."
        else:
            target.activity_ids.append(activity_id)
            adjustment = (
                f"Moved {activity_name} from day {source_day.day} to day {target.day} "
                "to preserve the requested daily pace."
            )
            source_day.notes += f" {activity_name} was moved to day {target.day} to preserve downtime."
            target.notes += f" Includes {activity_name}, moved from day {source_day.day}; allow breaks around it."
        adjustments.append(adjustment)

    return adjustments


def _repair_final_inventory(final: FinalItinerary, worker_outputs: dict) -> None:
    """Remove invented or repeated IDs before the final grounding check."""
    flight, hotel, activities = _selected_inventory(worker_outputs)
    allowed_activity_ids = {item["activity_id"] for item in activities}
    corrections = []

    if final.selected_flight_id != flight["flight_id"]:
        final.selected_flight_id = flight["flight_id"]
        corrections.append("Restored the flight selected by the Trip Planner.")
    if final.selected_hotel_id != hotel["hotel_id"]:
        final.selected_hotel_id = hotel["hotel_id"]
        corrections.append("Restored the hotel selected by the Trip Planner.")

    seen_ids: set[str] = set()
    for day in reversed(final.days):
        valid_ids = []
        for activity_id in reversed(day.activity_ids):
            if activity_id in allowed_activity_ids and activity_id not in seen_ids:
                valid_ids.append(activity_id)
                seen_ids.add(activity_id)
        valid_ids.reverse()
        if valid_ids != day.activity_ids:
            day.activity_ids = valid_ids
            corrections.append(f"Removed an invalid or duplicate activity from day {day.day}.")

    final.changes_after_critique.extend(corrections)


def create_draft(
    requirements: TravelRequirements,
    worker_outputs: dict,
) -> DraftItinerary:
    """Build the first itinerary from approved specialist recommendations."""
    draft = ask_model(
        system_prompt=(
            "You are the Itinerary Composer. Build a practical, day-wise itinerary "
            "using only the agents' selected option IDs. Respect pace_preference: "
            "relaxed means at most one main activity per day, generous breaks, and "
            "open time; do not fill every day just because options exist. Keep arrival "
            "and departure days especially light. Mention recovery time and meal breaks "
            "in day notes. Use each activity at most once. Explain trade-offs and state "
            "assumptions. The budget field will be verified by Python."
        ),
        payload={
            "requirements": requirements.model_dump(),
            "worker_outputs": _composer_context(worker_outputs),
        },
        output_model=DraftItinerary,
    )
    draft.tradeoffs.extend(_enforce_daily_pace(draft, requirements, worker_outputs))
    _ground_itinerary(draft, requirements, worker_outputs)
    return draft


def refine_itinerary(
    requirements: TravelRequirements,
    draft: DraftItinerary,
    critique: Critique,
    worker_outputs: dict,
) -> FinalItinerary:
    """Apply reviewer feedback without changing grounded inventory."""
    prompt = (
        "You are the Itinerary Composer revising a travel plan after review. Fix only "
        "the identified problems. Keep all choices grounded in agent-selected IDs, "
        "preserve good parts, and list the changes made. Respect the requested pace "
        "limit per day, preserve breaks and open time, and do not add activities just "
        "to fill the schedule. Return exactly one day block per trip day. Every "
        "activity ID may appear at most once: moving an activity means removing it "
        "from its old day, not copying it. An arrival or departure day may have an "
        "empty activity list."
    )
    payload = {
        "requirements": requirements.model_dump(),
        "draft_itinerary": draft.model_dump(),
        "critique": critique.model_dump(),
        "worker_outputs": _composer_context(worker_outputs),
    }

    final = ask_model(
        system_prompt=prompt,
        payload=payload,
        output_model=FinalItinerary,
    )
    _repair_final_inventory(final, worker_outputs)
    final.changes_after_critique.extend(
        _enforce_daily_pace(final, requirements, worker_outputs)
    )
    _ground_itinerary(final, requirements, worker_outputs)
    return final


def display_plan(final: FinalItinerary, worker_outputs: dict) -> dict:
    """Replace IDs with local inventory records for readable output."""
    flight, hotel, activities = _selected_inventory(worker_outputs)
    activity_by_id = {item["activity_id"]: item for item in activities}
    days = []
    for day in final.days:
        days.append({
            "day": day.day,
            "focus": day.focus,
            "activities": [activity_by_id[item_id] for item_id in day.activity_ids],
            "notes": day.notes,
        })

    return {
        "selected_flight": flight,
        "selected_hotel": hotel,
        "daily_plan": days,
        "budget": final.budget.model_dump(),
        "tradeoffs": final.tradeoffs,
        "assumptions": final.assumptions,
        "changes_after_critique": final.changes_after_critique,
        "final_notes": final.final_notes,
    }
