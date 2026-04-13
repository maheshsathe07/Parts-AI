"""
Groq LLaMA-3 agentic loop — OPTIMIZED VERSION.

Key optimizations:
1. Parallel tool execution — all 7 tools run concurrently
2. Single LLM call for synthesis — eliminates multiple round-trips
3. Graceful error handling for individual tool failures
"""

import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import asyncio
import json
import re
from openai import AsyncOpenAI
from config import settings
from tools.image_search import search_part_images
from tools.web_search import (
    search_part_details,
    search_compatible_vehicles,
    search_lifetime_and_maintenance,
    search_failure_symptoms,
    search_installation_steps,
)
from tools.youtube_search import search_installation_videos

# Databricks AI Gateway client
client = AsyncOpenAI(
    api_key=settings.databricks_token,
    base_url="https://55281934845796.ai-gateway.cloud.databricks.com/mlflow/v1"
)

MODEL = "databricks-gpt-5-4"
SYSTEM_PROMPT = """You are an expert automotive parts research assistant for a US-market automotive retail platform.

Your job is to synthesize pre-gathered research data into a structured JSON response.

You will receive data from multiple sources including:
- Part images
- Technical specifications
- Compatible vehicles
- Lifetime and maintenance info
- Failure symptoms
- Installation steps
- Installation videos

Based on ALL this data, output ONLY a single valid JSON object — no markdown fences, no extra text — with this exact structure:

{
  "detailed_description": "<string — 1-2 meaningful sentences, up to 50 words, clearly explaining what the part does and its purpose>",
  "expected_lifetime": "<string — MUST be in MILES only (e.g., '50,000-80,000 miles') with a single line describing typical replacement interval>",
  "maintenance_and_safety": [
    "<First maintenance or safety tip as a complete sentence>",
    "<Second maintenance or safety tip as a complete sentence>",
    "..."
  ],
  "failure_symptoms": [
    "<First symptom as a complete sentence>",
    "<Second symptom as a complete sentence>",
    "..."
  ],
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

RULES:
1. NEVER invent, guess, or hallucinate any data. Every fact must come from the provided search results.
2. For detailed_description: Write 1-2 meaningful sentences (up to 50 words) clearly explaining what the part does and why it's important.
3. For expected_lifetime: Express ONLY in MILES (e.g., '60,000-100,000 miles'). Keep it to ONE line describing the typical mileage range for replacement.
4. For compatible_vehicles: Parse fitment data carefully. DEDUPLICATE entries — merge overlapping year ranges for the same make/model/trim into a single entry with the widest year range (e.g., "1990-2000 Toyota Corolla" and "1994-2000 Toyota Corolla" become one entry: {"year": "1990-2000", "make": "Toyota", "model": "Corolla"}). Never list the same vehicle multiple times.
5. For installation_steps, extract numbered steps from the results. Aim for 6–12 clear steps.
6. For maintenance_and_safety, provide a LIST of 5-10 separate tips, each as one complete sentence.
7. For failure_symptoms, provide a LIST of 4-8 observable symptoms, each as one complete sentence.
8. For sources, include unique URLs from all web search results.
9. Do NOT include image or video data in your JSON — those are handled separately.
"""


async def _run_tool_safe(coro, tool_name: str):
    """
    Run a tool coroutine safely, returning empty result on error.
    Prevents one failing tool from breaking the entire request.
    """
    try:
        return await asyncio.wait_for(coro, timeout=25.0)
    except asyncio.TimeoutError:
        print(f"[WARN] Tool '{tool_name}' timed out after 25s")
        return []
    except Exception as e:
        print(f"[WARN] Tool '{tool_name}' failed: {e}")
        return []


async def run_all_tools_parallel(
    part_number: str, description: str, manufacturer_code: str
) -> dict:
    """
    Execute ALL required tools in parallel for maximum speed.
    Returns a dict with all tool results.
    """
    results = await asyncio.gather(
        _run_tool_safe(
            search_part_images(part_number, description),
            "search_part_images"
        ),
        _run_tool_safe(
            search_part_details(part_number, description, manufacturer_code),
            "search_part_details"
        ),
        _run_tool_safe(
            search_compatible_vehicles(part_number, description),
            "search_compatible_vehicles"
        ),
        _run_tool_safe(
            search_lifetime_and_maintenance(part_number, description),
            "search_lifetime_and_maintenance"
        ),
        _run_tool_safe(
            search_failure_symptoms(description),
            "search_failure_symptoms"
        ),
        _run_tool_safe(
            search_installation_steps(part_number, description),
            "search_installation_steps"
        ),
        _run_tool_safe(
            search_installation_videos(part_number, description),
            "search_installation_videos"
        ),
    )

    return {
        "images": results[0],
        "part_details": results[1],
        "compatible_vehicles": results[2],
        "lifetime_maintenance": results[3],
        "failure_symptoms": results[4],
        "installation_steps": results[5],
        "videos": results[6],
    }


async def run_agent(part_number: str, description: str, manufacturer_code: str) -> dict:
    """
    OPTIMIZED agentic flow:
      1. Run ALL tools in parallel (no LLM decision-making overhead)
      2. Single LLM call to synthesize results into structured JSON
    
    This eliminates 6+ LLM round-trips and parallel tool execution
    reduces total API wait time by ~70%.
    """

    # ── Step 1: Parallel tool execution ───────────────────────────────────────
    tool_results = await run_all_tools_parallel(
        part_number, description, manufacturer_code
    )

    raw_images = tool_results["images"]
    raw_videos = tool_results["videos"]

    # ── Step 2: Build synthesis prompt with all gathered data ─────────────────
    synthesis_prompt = f"""Research the following automotive part based on the gathered data:

Part Number: {part_number}
Description: {description}
Manufacturer Code: {manufacturer_code}

=== PART DETAILS (from web search) ===
{json.dumps(tool_results["part_details"], indent=2)}

=== COMPATIBLE VEHICLES (from web search) ===
{json.dumps(tool_results["compatible_vehicles"], indent=2)}

=== LIFETIME & MAINTENANCE (from web search) ===
{json.dumps(tool_results["lifetime_maintenance"], indent=2)}

=== FAILURE SYMPTOMS (from web search) ===
{json.dumps(tool_results["failure_symptoms"], indent=2)}

=== INSTALLATION STEPS (from web search) ===
{json.dumps(tool_results["installation_steps"], indent=2)}

Based on ALL the above data, produce the structured JSON response.
Extract sources (URLs) from all the search results above.
"""

    # ── Step 3: Single LLM call for synthesis ─────────────────────────────────
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": synthesis_prompt},
    ]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=4096,
        temperature=0.1,  # near-zero temp → deterministic, factual
    )

    final_text = response.choices[0].message.content or ""
    llm_data = _parse_json_from_text(final_text)

    # ── Step 4: Post-process to deduplicate compatible vehicles ───────────────
    if "compatible_vehicles" in llm_data:
        llm_data["compatible_vehicles"] = _deduplicate_vehicles(llm_data["compatible_vehicles"])

    return {
        "llm_data": llm_data,
        "raw_images": raw_images,
        "raw_videos": raw_videos,
    }


def _deduplicate_vehicles(vehicles: list) -> list:
    """
    Deduplicate compatible vehicles by merging overlapping year ranges
    for the same make/model/trim combination.
    """
    if not vehicles or not isinstance(vehicles, list):
        return vehicles

    # Group vehicles by make+model+trim (case-insensitive)
    grouped = {}
    for v in vehicles:
        if not isinstance(v, dict):
            continue
        
        make = str(v.get("make", "")).strip().lower()
        model = str(v.get("model", "")).strip().lower()
        trim = str(v.get("trim", "")).strip().lower()
        year_str = str(v.get("year", "")).strip()
        
        if not make or not model:
            continue
        
        key = (make, model, trim)
        
        # Parse year range (e.g., "1986-1992" or "1991")
        years = []
        if "-" in year_str:
            parts = year_str.split("-")
            try:
                years = [int(parts[0].strip()), int(parts[1].strip())]
            except (ValueError, IndexError):
                years = []
        else:
            try:
                year = int(year_str)
                years = [year, year]
            except ValueError:
                years = []
        
        if key not in grouped:
            grouped[key] = {
                "make": v.get("make", "").strip(),
                "model": v.get("model", "").strip(),
                "trim": v.get("trim", "").strip() if v.get("trim") else "",
                "min_year": years[0] if years else None,
                "max_year": years[1] if years else None
            }
        else:
            # Merge year ranges
            if years:
                if grouped[key]["min_year"] is None or years[0] < grouped[key]["min_year"]:
                    grouped[key]["min_year"] = years[0]
                if grouped[key]["max_year"] is None or years[1] > grouped[key]["max_year"]:
                    grouped[key]["max_year"] = years[1]
    
    # Build deduplicated list
    result = []
    for key, data in grouped.items():
        entry = {
            "make": data["make"],
            "model": data["model"]
        }
        
        # Format year range
        if data["min_year"] and data["max_year"]:
            if data["min_year"] == data["max_year"]:
                entry["year"] = str(data["min_year"])
            else:
                entry["year"] = f"{data['min_year']}-{data['max_year']}"
        
        if data["trim"]:
            entry["trim"] = data["trim"]
        
        result.append(entry)
    
    # Sort by make, model, year
    result.sort(key=lambda x: (x.get("make", ""), x.get("model", ""), x.get("year", "")))
    
    return result


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