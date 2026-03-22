import json
from tools.image_search import search_part_images
from tools.web_search import (
    search_part_details,
    search_compatible_vehicles,
    search_lifetime_and_maintenance,
    search_failure_symptoms,
    search_installation_steps,
)
from tools.youtube_search import search_installation_videos


# ── Tool schemas passed to Groq (OpenAI-compatible function calling) ──────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_part_images",
            "description": (
                "Search Google Images for real product photos of an automotive part "
                "using its part number and description. Returns image URLs with titles."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string", "description": "OEM or aftermarket part number"},
                    "description": {"type": "string", "description": "Short part description, e.g. 'front brake rotor'"},
                },
                "required": ["part_number", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_part_details",
            "description": (
                "Search the web for detailed technical specifications, features, and "
                "product description of an automotive part using part number, description, "
                "and manufacturer code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string"},
                    "description": {"type": "string"},
                    "manufacturer_code": {"type": "string"},
                },
                "required": ["part_number", "description", "manufacturer_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_compatible_vehicles",
            "description": (
                "Search the web for vehicles (year, make, model) that are compatible "
                "with the given automotive part. Focus on US market fitment."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["part_number", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_lifetime_and_maintenance",
            "description": (
                "Search the web for the expected service lifetime, recommended "
                "maintenance schedule, and safety tips for an automotive part."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["part_number", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_failure_symptoms",
            "description": (
                "Search the web for common symptoms and warning signs that indicate "
                "an automotive part is failing or needs replacement."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_installation_steps",
            "description": (
                "Search the web for OEM-sourced or authoritative step-by-step "
                "installation instructions for an automotive part."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["part_number", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_installation_videos",
            "description": (
                "Search YouTube for how-to / installation videos for an automotive part. "
                "Returns video titles, channels, thumbnails, and URLs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["part_number", "description"],
            },
        },
    },
]


# ── Dispatcher — routes tool_name → async function call ──────────────────────

async def dispatch_tool(tool_name: str, arguments: dict) -> str:
    """
    Execute the named tool with the given arguments.
    Always returns a JSON string so it can be sent back as a tool_result message.
    """
    try:
        if tool_name == "search_part_images":
            result = await search_part_images(**arguments)

        elif tool_name == "search_part_details":
            result = await search_part_details(**arguments)

        elif tool_name == "search_compatible_vehicles":
            result = await search_compatible_vehicles(**arguments)

        elif tool_name == "search_lifetime_and_maintenance":
            result = await search_lifetime_and_maintenance(**arguments)

        elif tool_name == "search_failure_symptoms":
            result = await search_failure_symptoms(**arguments)

        elif tool_name == "search_installation_steps":
            result = await search_installation_steps(**arguments)

        elif tool_name == "search_installation_videos":
            result = await search_installation_videos(**arguments)

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)

    except Exception as exc:
        return json.dumps({"error": str(exc)})