# Agent Specification: Smart Travel & Itinerary Concierge

## Track
**Concierge Agent** (Personal Life & Productivity Automation)

---

## Objective
Build a simple, modular AI agent that interacts with a user to plan customized travel itineraries based on destination, duration, budget, and personal preferences.

---

## Architecture Overview

```
                        +---------------------------+
                        |         User Input        |
                        | (City, Days, Budget, etc.)|
                        +-------------+-------------+
                                      |
                                      v
                        +-------------+-------------+
                        |   Travel Concierge Agent  |
                        |  (System Instructions &   |
                        |     Planning Logic)       |
                        +-------------+-------------+
                                      |
           +--------------------------+--------------------------+
           |                                                     |
           v                                                     v
+----------+----------+                               +----------+----------+
|    Weather Tool     |                               |   Attractions Tool   |
| (Fetches forecast)  |                               | (Fetches top spots)  |
+----------+----------+                               +----------+----------+
           |                                                     |
           +--------------------------+--------------------------+
                                      |
                                      v
                        +-------------+-------------+
                        |  Itinerary Formatter Tool |
                        | (Generates itinerary.md)  |
                        +---------------------------+
```

---

## 5-Day Curriculum Mapping

| Day | Topic | Module / Focus |
|---|---|---|
| **Day 1** | Agent Prompting Basics | Designing system instructions & persona for `TravelConciergeAgent`. |
| **Day 2** | Tool Integration | Creating functional tools (`get_weather`, `get_attractions`, `search_flights_estimate`). |
| **Day 3** | Memory & State | Handling multi-turn user conversation (e.g., "Add a vegetarian dinner option on Day 2"). |
| **Day 4** | Markdown Artifact Output | Formatted file generation to save the final `itinerary.md`. |
| **Day 5** | Full Agent Integration & CLI | Assembling the end-to-end agent loop into a single executable CLI application. |

---

## Sample Execution Flow

```python
# User Input:
# "Plan a 3-day budget-friendly trip to Kyoto for a culture lover."

# Step 1: Agent queries attractions tool for "Kyoto cultural sights"
# Step 2: Agent queries weather tool for "Kyoto 3-day forecast"
# Step 3: Agent constructs daily schedule balancing activity levels & budget
# Step 4: Agent saves formatted Markdown itinerary to output/kyoto_itinerary.md
```
