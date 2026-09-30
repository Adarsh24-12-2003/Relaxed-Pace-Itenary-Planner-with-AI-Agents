
# Relaxed-Pace Multi-Agent Travel Planner

A multi-agent AI travel planner that creates and improves easygoing itineraries using specialized AI agents.

The project uses five AI roles coordinated by a small Python workflow: a Manager Agent, Flight Specialist, Hotel Specialist, Activity Specialist, and Critic Agent. The Manager extracts requirements, drafts the itinerary, and revises it after critique. Relaxed pacing is the default, with downtime and light arrival and departure days.

## Project Goal

The goal of this mini-project is to extend a basic multi-agent travel planner so that it creates realistic itineraries without packing every day with activities.

The Activity Specialist favors activities tagged `relaxed-pace` or `easy-pace`. A deterministic Python check enforces a daily activity limit: one for relaxed, two for balanced, and three for packed itineraries.

## Architecture

![Travel planner architecture](architecture.svg)

[Download the architecture diagram](architecture.svg)

The OpenAI model performs the reasoning, while local JSON files provide sample flights, hotels, and activities. Prices, schedules, and options are illustrative mock data, not live travel availability or quotes.

## Relaxed-Pace Customization

The project is customized for travelers who value a slower trip:

* The Manager records a `pace_preference`, defaulting to `relaxed`, and shares it with the specialists.
* Activity inventory uses `relaxed-pace`, `easy-pace`, and `full-day` tags to guide the Activity Specialist.
* The Manager preserves breaks and keeps arrival and departure days especially light.
* The Critic flags overfilled days and missing downtime; Python validation enforces the selected pace limit.

Example relaxed-pace request:

```text
Plan a relaxed 4-day trip from Delhi to Dubai for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day, leave generous breaks and unplanned time, and avoid red-eye flights.
```

## Project Structure

```text
relaxed_pace_travel_planner/
│
├── agents/
│   ├── manager.py
│   ├── workers.py        # Flight, Hotel, and Activity Specialists
│   └── critic.py
│
├── tools/
│   └── travel_tools.py
│
├── data/
│   ├── sample_activities.json
│   ├── sample_hotels.json
│   └── sample_flights.json
│
├── models.py
├── utils.py
├── main.py
├── orchestrator.py
├── requirements.txt
├── .gitignore
└── README.md
```

## How the Agents Work

### Manager Agent

The Manager turns the user's request into structured requirements such as:

* Origin
* Destination
* Number of days
* Number of travellers
* Budget
* Travel preferences
* Requested pace (relaxed by default)

Uncertain details are recorded as assumptions rather than invented. The Manager coordinates the specialists, drafts the itinerary from their selected options, then revises it after critique.

### Flight, Hotel, and Activity Specialists

Each specialist searches its matching local inventory and returns exact selected IDs. The Activity Specialist favors `relaxed-pace` and `easy-pace` activities for relaxed requests.

### Critic Agent

The Critic checks the draft for problems such as:

* Budget issues
* Overloaded days
* Unsupported assumptions
* Poor activity pacing

It provides actionable revision instructions without replacing specialist inventory selections.

For relaxed trips, the Critic checks for more than one main activity per day, insufficient breaks, and overfilled arrival or departure days. Python validation also enforces the selected pace limit.

### Revision

The Manager applies the Critic's feedback. The orchestrator then validates IDs, day count, pace limits, and budget totals before returning the final plan.

## Setup

### Linux / Ubuntu

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### Windows PowerShell

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

## API Key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Never commit or share the real API key.

The `.gitignore` file excludes `.env` from Git.

## Running the Project

Run the default travel request:

```bash
python main.py
```

The program generates a final travel plan containing:

* Selected flight
* Selected hotel
* Daily activities
* Budget
* Tradeoffs
* Assumptions
* Changes made after critique
* Final notes

## Testing With a Custom Request

The application accepts a custom travel request using the `--request` argument.

Example:

```bash
python main.py --request "Plan a relaxed 4-day trip from Delhi to Dubai for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day, leave generous breaks and unplanned time, and avoid red-eye flights."
```

For a relaxed request, the Activity Specialist can select lighter activities such as:

* Old Dubai souks and creek abra ride
* Al Fahidi heritage quarter
* Spice Souk and creekside food walk

depending on the agent's reasoning and the available local inventory.

## Viewing the Full Agent Trace

To see the intermediate agent outputs:

```bash
python main.py --show-trace
```

You can also combine a custom request with the full trace:

```bash
python main.py --request "Plan a relaxed 4-day trip from Delhi to Dubai for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time." --show-trace
```

The trace shows:

```text
Manager extracts requirements
        |
        v
Flight, Hotel, and Activity Specialists
select from local inventories
        |
        v
Manager drafts the itinerary
        |
        v
Critic Agent feedback
        |
        v
Revision instructions
        |
        v
Final itinerary
```

## Example Activity Pace Tags

The local activity data marks options by the effort and time they tend to require:

```text
Old Dubai souks and creek abra ride
Tags: culture, food, walkable, low-cost, relaxed-pace

Al Fahidi heritage quarter
Tags: culture, history, walkable, easy-pace

Desert conservation safari
Tags: nature, adventure, premium, full-day
```

These tags help the Activity Specialist choose suitable options without overfilling the day.

## Technologies Used

* Python
* OpenAI API
* Pydantic
* Python-dotenv
* JSON
* Multi-Agent Architecture

## Key Concepts Demonstrated

This project demonstrates:

* Multi-agent AI architecture
* A five-agent workflow with three specialist roles
* Tool-grounded agent decisions
* Structured outputs using Pydantic
* Independent review and refinement
* Revision / Reflexion-style improvement
* Pace-aware agent customization and deterministic schedule validation
* Local JSON data as tool results
* Command-line user requests

## Testing

Run the default relaxed-pace request with:

```bash
python main.py
```

A custom relaxed-pace request can be run with:

```bash
python main.py --request "Plan a relaxed 4-day trip from Delhi to Dubai for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time."
```

The complete pipeline was tested with:

```bash
python main.py --request "Plan a relaxed 4-day trip from Delhi to Dubai for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time." --show-trace
```

The test successfully demonstrated:

* Trip requirements and inventory selection
* Relaxed-pace activity selection and schedule validation
* Draft itinerary generation
* Independent review and final revision

## Conclusion

This project extends the base Multi-Agent Travel Planner into a relaxed-pace travel planning system.

The main customization is the pace-aware workflow: the Activity Specialist favors lighter options, the Manager preserves downtime, and deterministic validation prevents relaxed itineraries from exceeding one main activity per day.

