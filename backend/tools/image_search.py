from tools.web_search import image_search_serpapi


async def search_part_images(part_number: str, description: str) -> list[dict]:
    """
    Uses SerpApi Google Image Search to find real product photos
    for the given automotive part.
    """
    query = f"{part_number} {description} automotive part"
    return await image_search_serpapi(query, num=6)