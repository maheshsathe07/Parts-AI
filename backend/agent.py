"""
Groq LLaMA-3 agentic loop.

The model decides WHICH tools to call and WHEN.
All factual data comes from tool results (real internet searches).
The LLM only synthesises / formats the gathered data — it never invents facts.
"""

import json
import re
from groq import AsyncGroq
from config import settings
from tools.registry import TOOL_DEFINITIONS, dispatch_tool

client = AsyncGroq(api_key=settings.groq_api_key)

MODEL = "llama-3.3-70b-versatile"   # Best freely available LLaMA-3 on Groq

SYSTEM_PROMPT = """You are an expert automotive parts research assistant for a US-market automotive retail platform.

Your ONLY job is to gather REAL data from the internet using the provided tools and then compile it into a structured JSON response.

CRITICAL RULES:
1. You MUST call ALL of the following tools before producing a final answer — do not skip any:
   - search_part_images
   - search_part_details
   - search_compatible_vehicles
   - search_lifetime_and_maintenance
   - search_failure_symptoms
   - search_installation_steps
   - search_installation_videos

2. NEVER invent, guess, or hallucinate any data. Every fact must come from a tool result.

3. After calling all tools and receiving all results, output ONLY a single valid JSON object — no markdown fences, no extra text — with this exact structure:

{
  "detailed_description": "<string — comprehensive technical description from web search results>",
  "expected_lifetime": "<string — service life data from web search results>",
  "maintenance_and_safety": "<string — maintenance schedule and safety tips from web search results>",
  "failure_symptoms": "<string — symptoms and warning signs from web search results>",
  "compatible_vehicles": [
    {"year": "...", "make": "...", "model": "...", "trim": "..."},
    ...
  ],
  "installation_steps": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "sources": ["url1", "url2", ...]
}

4. For compatible_vehicles, parse the fitment data carefully. Include year, make, model. Trim is optional.
5. For installation_steps, extract numbered steps from the web results. Aim for 6–12 clear steps.
6. For sources, include unique URLs from all web search tool results.
7. Do NOT include image or video data in your JSON — those are handled separately.
"""


async def run_agent(part_number: str, description: str, manufacturer_code: str) -> dict:
    """
    Runs the full agentic loop:
      1. LLM decides which tools to call
      2. Tools execute against real APIs
      3. Results fed back to LLM
      4. LLM synthesises final structured JSON
    Returns a dict with all raw tool outputs + LLM synthesis.
    """

    # Initial user message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Research this automotive part thoroughly using ALL available tools:\n\n"
                f"Part Number: {part_number}\n"
                f"Description: {description}\n"
                f"Manufacturer Code: {manufacturer_code}\n\n"
                f"Call every tool, then output the final JSON."
            ),
        },
    ]

    # Containers for raw tool outputs (returned alongside LLM synthesis)
    raw_images = []
    raw_videos = []

    # ── Agentic loop ──────────────────────────────────────────────────────────
    max_iterations = 20   # safety cap
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            max_tokens=4096,
            temperature=0.1,   # near-zero temp → deterministic, factual
        )

        message = response.choices[0].message

        # Append assistant turn to history
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in (message.tool_calls or [])
            ] or None,
        })

        # If no tool calls → LLM is done, extract final JSON
        if not message.tool_calls:
            final_text = message.content or ""
            llm_data = _parse_json_from_text(final_text)
            return {
                "llm_data": llm_data,
                "raw_images": raw_images,
                "raw_videos": raw_videos,
            }

        # Execute each tool call
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            tool_result = await dispatch_tool(fn_name, fn_args)

            # Capture image / video results separately for direct use in response
            parsed_result = json.loads(tool_result)
            if fn_name == "search_part_images" and isinstance(parsed_result, list):
                raw_images = parsed_result
            elif fn_name == "search_installation_videos" and isinstance(parsed_result, list):
                raw_videos = parsed_result

            # Feed tool result back into conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })

    # If we hit the iteration cap without a final answer
    raise RuntimeError("Agent did not converge within the allowed iterations.")


def _parse_json_from_text(text: str) -> dict:
    """Extract JSON object from LLM output, stripping any surrounding text."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find a JSON block
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return empty skeleton so the rest of the pipeline doesn't crash
    return {
        "detailed_description": "",
        "expected_lifetime": "",
        "maintenance_and_safety": "",
        "failure_symptoms": "",
        "compatible_vehicles": [],
        "installation_steps": [],
        "sources": [],
    }