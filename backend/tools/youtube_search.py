import httpx
from config import settings
import certifi

# ── Connection pooling for better performance ─────────────────────────────────
_yt_http_client: httpx.AsyncClient | None = None


async def get_youtube_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client for YouTube API."""
    global _yt_http_client
    if _yt_http_client is None or _yt_http_client.is_closed:
        _yt_http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            verify=certifi.where(),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    return _yt_http_client


async def close_youtube_http_client():
    """Close the shared HTTP client (call on app shutdown)."""
    global _yt_http_client
    if _yt_http_client is not None and not _yt_http_client.is_closed:
        await _yt_http_client.aclose()
        _yt_http_client = None


async def search_installation_videos(part_number: str, description: str) -> list[dict]:
    """
    Uses YouTube Data API v3 to find installation / how-to videos
    for the given automotive part.
    """
    url = "https://www.googleapis.com/youtube/v3/search"

    # Search for installation, usage, and configuration videos
    queries = [
        f"how to install {description} {part_number}",
        f"why use {description} automotive",
        f"{description} replacement configuration setup"
    ]
    query = " | ".join(queries[:2])  # Combine first two for broader results

    params = {
        "key": settings.youtube_api_key,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": 5,
        "relevanceLanguage": "en",
        "regionCode": "US",
        "videoDuration": "medium",   # 4–20 min — avoids shorts and hour-long lectures
        "videoEmbeddable": "true",
        "safeSearch": "moderate",
        "order": "relevance",
    }

    client = await get_youtube_http_client()
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    videos = []
    for item in data.get("items", []):
        vid_id = item["id"].get("videoId", "")
        snippet = item.get("snippet", {})
        videos.append({
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "description": snippet.get("description", "")[:200],
        })

    return videos