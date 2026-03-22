import httpx
from config import settings


async def search_installation_videos(part_number: str, description: str) -> list[dict]:
    """
    Uses YouTube Data API v3 to find installation / how-to videos
    for the given automotive part.
    """
    url = "https://www.googleapis.com/youtube/v3/search"

    query = f"how to install {description} {part_number} automotive DIY"

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

    async with httpx.AsyncClient(timeout=15) as client:
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