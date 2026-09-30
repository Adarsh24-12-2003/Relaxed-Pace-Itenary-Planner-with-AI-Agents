
# Relaxed-Pace Multi-Agent Travel Planner

A multi-agent AI travel planner that creates and improves easygoing itineraries using specialized AI agents.

The Manager Agent coordinates three specialist agents — Flight, Hotel, and Activity — and a Critic Agent reviews and improves the itinerary. Relaxed pacing is the default: the planner limits each day to one main activity, preserves downtime, and keeps arrival and departure days light.

## Project Goal

The goal of this mini-project is to extend a basic multi-agent travel planner so that it creates realistic itineraries without packing every day with activities.

The Activity Worker favors activities tagged `relaxed-pace` or `easy-pace`. A deterministic manager check enforces a daily activity limit: one for relaxed, two for balanced, and three for packed itineraries.

## Architecture

```text
User Request
     |
     v
Manager Agent
     |
     +------------------+
     |        |         |
     v        v         v
 Flight    Hotel    Activity
 Worker    Worker     Worker
     |        |         |
     +--------+---------+
              |
              v
       Draft Itinerary
              |
              v
        Critic Agent
              |
              v
      Revision by Manager
              |
              v
     Final Travel Plan
````

The OpenAI model performs the reasoning, while local JSON files provide the available flights, hotels, and activities.

## Relaxed-Pace Customization

The project is customized for travelers who value a slower trip:

* Requirement extraction records a `pace_preference`, defaulting to `relaxed`.
* Activity inventory uses `relaxed-pace`, `easy-pace`, and `full-day` tags to help the Activity Worker distinguish lighter options.
* The Manager leaves open time, adds rest and meal breaks to day notes, and keeps arrival and departure days especially light.
* The Critic flags overfilled days and missing downtime; manager validation rejects plans that exceed their selected pace limit.

Example relaxed-pace request:

```text
Plan a relaxed 4-day trip from Mumbai to Singapore for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day, leave generous breaks and unplanned time, and avoid red-eye flights.
```

## Project Structure

```text
relaxed_pace_travel_planner/
│
├── agents/
│   ├── manager.py
│   ├── workers.py
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
├── requirements.txt
├── .gitignore
└── README.md
```

## How the Agents Work

### Manager Agent

The Manager receives the user's travel request and extracts important requirements such as:

* Origin
* Destination
* Number of days
* Number of travellers
* Budget
* Travel preferences
* Requested pace (relaxed by default)

It coordinates the specialist workers and creates the initial itinerary.

### Flight Worker

The Flight Worker examines the available flight records and selects a suitable flight based on the user's requirements.

### Hotel Worker

The Hotel Worker examines the available hotel records and selects a suitable hotel based on budget, location, amenities, and preferences.

### Activity Worker

The Activity Worker examines the available activities and selects activities that match the user's interests.

For relaxed trips, it prefers activities tagged:

```text
relaxed-pace
easy-pace
```

The manager enforces the selected pace limit even if the language model returns an overfilled day.

### Critic Agent

The Critic reviews the generated itinerary and identifies problems such as:

* Budget issues
* Overloaded days
* Unsupported assumptions
* Poor activity pacing

It then provides revision instructions to the Manager.

For relaxed trips, the Critic specifically checks for more than one main activity per day, insufficient breaks, and overfilled arrival or departure days.

### Revision

The Manager uses the Critic's feedback to produce the final refined itinerary.

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
python main.py --request "Plan a relaxed 4-day trip from Mumbai to Singapore for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day, leave generous breaks and unplanned time, and avoid red-eye flights."
```

For a relaxed request, the Activity Worker can select lighter activities such as:

* Chinatown and Maxwell Food Centre walk
* Kampong Glam food and heritage trail
* National Gallery and Civic District

depending on the agent's reasoning and the available local inventory.

## Viewing the Full Agent Trace

To see the intermediate agent outputs:

```bash
python main.py --show-trace
```

You can also combine a custom request with the full trace:

```bash
python main.py --request "Plan a relaxed 4-day trip from Mumbai to Singapore for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time." --show-trace
```

The trace shows:

```text
Requirements extracted by Manager
        |
        v
Flight Worker decision
        |
        v
Hotel Worker decision
        |
        v
Activity Worker decision
        |
        v
Draft itinerary
        |
        v
Critic feedback
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
Chinatown and Maxwell Food Centre walk
Tags: food, culture, walkable, relaxed-pace

National Gallery and Civic District
Tags: culture, museum, history, indoor, easy-pace

Sentosa half-day: beaches and cable car
Tags: leisure, views, full-day
```

These tags help the Activity Worker choose a suitable anchor activity without overfilling the day.

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
* Manager and specialist agents
* Tool-grounded agent decisions
* Structured outputs using Pydantic
* Critic-based evaluation
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
python main.py --request "Plan a relaxed 4-day trip from Mumbai to Singapore for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time."
```

The complete pipeline was tested with:

```bash
python main.py --request "Plan a relaxed 4-day trip from Mumbai to Singapore for two people. Prefer food, city views, and cultural sites. Schedule no more than one main activity per day and leave generous breaks and unplanned time." --show-trace
```

The test successfully demonstrated:

* Requirement extraction
* Flight selection
* Hotel selection
* Relaxed-pace activity selection and schedule validation
* Draft itinerary generation
* Critic evaluation
* Final itinerary revision

## Conclusion

This project extends the base Multi-Agent Travel Planner into a relaxed-pace travel planning system.

The main customization is the pace-aware workflow: agents favor lighter activities, the Manager preserves downtime, and deterministic validation prevents relaxed itineraries from exceeding one main activity per day.

