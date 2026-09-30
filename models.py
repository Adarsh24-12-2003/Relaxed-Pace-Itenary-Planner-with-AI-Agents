"""Structured contracts shared by the travel-planner agents."""

from typing import Literal

from pydantic import BaseModel, Field


class TravelRequirements(BaseModel):
    origin: str
    destination: str
    duration_days: int = Field(ge=1, le=14)
    traveller_count: int = Field(ge=1, le=10)
    budget_level: str
    pace_preference: Literal["relaxed", "balanced", "packed"] = "relaxed"
    hotel_budget_inr: int | None = Field(default=None, ge=0)
    avoid_red_eye: bool
    preferences: list[str]
    assumptions: list[str]


class TripPlanDecision(BaseModel):
    selected_flight_id: str
    selected_hotel_id: str
    selected_activity_ids: list[str]
    reason: str
    decision: str
    tradeoffs: list[str]


class DayPlan(BaseModel):
    day: int = Field(ge=1)
    focus: str
    activity_ids: list[str]
    notes: str


class BudgetBreakdown(BaseModel):
    flights_inr: int
    hotel_inr: int
    activities_inr: int
    estimated_total_inr: int


class DraftItinerary(BaseModel):
    selected_flight_id: str
    selected_hotel_id: str
    days: list[DayPlan]
    budget: BudgetBreakdown
    tradeoffs: list[str]
    assumptions: list[str]


class CritiqueIssue(BaseModel):
    severity: Literal["low", "medium", "high"]
    issue: str
    fix: str


class Critique(BaseModel):
    overall_assessment: str
    issues: list[CritiqueIssue]
    revision_instructions: list[str]
    quality_score: int = Field(ge=0, le=100)


class FinalItinerary(DraftItinerary):
    changes_after_critique: list[str]
    final_notes: list[str]
