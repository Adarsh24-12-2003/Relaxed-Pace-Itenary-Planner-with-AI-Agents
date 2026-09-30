"""OpenAI and JSON helpers used across the project."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI()

OutputModel = TypeVar("OutputModel", bound=BaseModel)


def ask_model(
    system_prompt: str,
    payload: dict,
    output_model: type[OutputModel],
) -> OutputModel:
    """Send one task to OpenAI and parse its structured response."""
    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, indent=2),
            },
        ],
        text_format=output_model,
    )

    if response.output_parsed is None:
        raise RuntimeError("The model did not return the expected structured output.")
    return response.output_parsed


def pretty_json(value: object) -> str:
    """Format dictionaries and Pydantic objects for classroom output."""
    if isinstance(value, BaseModel):
        value = value.model_dump()
    return json.dumps(value, indent=2, ensure_ascii=False)
