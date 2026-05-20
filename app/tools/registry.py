# Central registry for all agent tools.
# TOOL_SCHEMAS are passed to the OpenAI Responses API,
# New tool: add schema to TOOL_SCHEMAS and function to TOOL_REGISTRY.


from app.tools.datetime_tool import get_current_datetime
from app.tools.search_tool import search_documentation
from app.tools.weather_tool import get_weather

""" 
Tool schemas define:
- tool name
- description
- input parameters
so the model knows what tools are available and how to call them.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_current_datetime",
        "description": "Returns the current UTC date and time. Use this when the user asks about the current time, date, or anything time-sensitive.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": (
            "Returns current weather conditions for any city in the world: "
            "temperature, wind speed and direction, visibility, humidity, and sunrise/sunset times. "
            "Use this when the user asks about weather, wind, visibility, or atmospheric conditions at a location."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name to get weather for (e.g. 'Barcelona', 'Mumbai', 'London').",
                }
            },
            "required": ["city"],
        },
    },
    {
        "type": "function",
        "name": "search_documentation",
        "description": (
            "Searches the airline manual for content relevant to the query. "
            "Use this for any question about airline policies, procedures, safety, "
            "aircraft performance, baggage, or anything covered in the manual."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A focused search query describing what to look up in the manual.",
                }
            },
            "required": ["query"],
        },
    },
]

# Maps tool names to actual callable Python functions.
# loop.py uses this registry to dynamically execute tools requested by the model.
TOOL_REGISTRY: dict[str, callable] = {
    "get_current_datetime": get_current_datetime,
    "get_weather": get_weather,
    "search_documentation": search_documentation,
}
