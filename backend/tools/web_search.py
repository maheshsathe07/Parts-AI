"""
Web search tool using SerpApi (https://serpapi.com)
Free tier: 100 searches/month
Paid: $50/month for 5,000 searches

SerpApi hits real Google Search with no domain restrictions —
unlike Google Custom Search Engine which can no longer search the entire web.
"""
import httpx
from config import settings
import certifi
from contextlib import asynccontextmanager

# ── Connection pooling for better performance ─────────────────────────────────
_http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client with connection pooling."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            verify=certifi.where(),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


async def close_http_client():
    """Close the shared HTTP client (call on app shutdown)."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


async def _serpapi_search(query: str, num: int = 5, search_type: str = "search") -> dict:
    """
    Core SerpApi call.
    search_type = "search" for web results, "images" for image results.
    """
    url = "https://serpapi.com/search"

    params = {
        "api_key": settings.serpapi_key,
        "q": query,
        "num": num,
        "gl": "us",        # US market
        "hl": "en",
        "engine": "google",
        "safe": "active",
    }

    if search_type == "images":
        params["tbm"] = "isch"

    client = await get_http_client()
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


async def web_search(query: str, num: int = 5) -> list[dict]:
    """Generic Google web search. Returns list of {title, snippet, link}."""
    data = await _serpapi_search(query, num=num, search_type="search")
    results = []
    for item in data.get("organic_results", []):
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
        })
    return results


async def image_search_serpapi(query: str, num: int = 6) -> list[dict]:
    """Google image search via SerpApi. Returns list of {url, title, source}."""
    data = await _serpapi_search(query, num=num, search_type="images")
    results = []
    for item in data.get("images_results", [])[:num]:
        results.append({
            "url": item.get("original", ""),
            "title": item.get("title", ""),
            "source": item.get("source", ""),
        })
    return results


# ── Named query helpers used by agent tool registry ──────────────────────────

async def search_part_details(part_number: str, description: str, manufacturer_code: str) -> list[dict]:
    query = f'"{part_number}" {description} {manufacturer_code} automotive part specifications'
    return await web_search(query, num=5)


async def search_compatible_vehicles(part_number: str, description: str) -> list[dict]:
    query = f"{part_number} {description} compatible vehicles year make model fitment US"
    return await web_search(query, num=5)


async def search_lifetime_and_maintenance(part_number: str, description: str) -> list[dict]:
    query = f"{description} automotive part expected lifetime maintenance schedule safety tips"
    return await web_search(query, num=4)


async def search_failure_symptoms(description: str) -> list[dict]:
    query = f"{description} bad failing symptoms warning signs automotive"
    return await web_search(query, num=4)


async def search_installation_steps(part_number: str, description: str) -> list[dict]:
    query = f"how to install {description} {part_number} step by step OEM DIY automotive US"
    return await web_search(query, num=5)