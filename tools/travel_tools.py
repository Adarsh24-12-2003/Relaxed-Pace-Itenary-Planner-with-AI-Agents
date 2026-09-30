"""Simple local-data tools used by the specialist workers."""

from __future__ import annotations

import json
from pathlib import Path

from models import TravelRequirements
from utils import PROJECT_ROOT


def _read_json(filename: str) -> list[dict]:
    path = PROJECT_ROOT / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def load_travel_data() -> dict[str, list[dict]]:
    """Load the mock inventory that stands in for travel APIs."""
    return {
        "flights": _read_json("sample_flights.json"),
        "hotels": _read_json("sample_hotels.json"),
        "activities": _read_json("sample_activities.json"),
    }


def search_flights(requirements: TravelRequirements, flights: list[dict]) -> list[dict]:
    """Return flights matching the requested route."""
    return [
        flight
        for flight in flights
        if flight["origin"].lower() == requirements.origin.lower()
        and flight["destination"].lower() == requirements.destination.lower()
    ]


def search_hotels(requirements: TravelRequirements, hotels: list[dict]) -> list[dict]:
    """Return destination hotels with their full-stay price."""
    nights = max(requirements.duration_days - 1, 1)
    matches = []
    for hotel in hotels:
        if hotel["destination"].lower() == requirements.destination.lower():
            option = dict(hotel)
            option["nights"] = nights
            option["total_price_inr"] = hotel["price_per_night_inr"] * nights
            matches.append(option)
    return matches


def search_activities(requirements: TravelRequirements, activities: list[dict]) -> list[dict]:
    """Return activities available at the destination."""
    return [
        activity
        for activity in activities
        if activity["destination"].lower() == requirements.destination.lower()
    ]


def estimate_budget(
    requirements: TravelRequirements,
    flight: dict,
    hotel: dict,
    activities: list[dict],
) -> dict[str, int]:
    """Calculate a grounded budget from selected inventory records."""
    travellers = requirements.traveller_count
    flights_total = flight["price_inr"] * travellers
    hotel_total = hotel["total_price_inr"]
    activities_total = sum(item["cost_inr"] for item in activities) * travellers
    return {
        "flights_inr": flights_total,
        "hotel_inr": hotel_total,
        "activities_inr": activities_total,
        "estimated_total_inr": flights_total + hotel_total + activities_total,
    }
