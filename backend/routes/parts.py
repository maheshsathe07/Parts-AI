from fastapi import APIRouter, HTTPException
from models.schemas import ResearchRequest, PartResearchResult, PartImage, YouTubeVideo, CompatibleVehicle
from agent import run_agent

router = APIRouter(prefix="/api", tags=["parts"])


@router.post("/research", response_model=PartResearchResult)
async def research_part(request: ResearchRequest):
    """
    Main endpoint: accepts part metadata, runs the Groq LLaMA-3 agentic loop
    with real tool calls, and returns fully researched part data.
    """
    part = request.part

    try:
        agent_output = await run_agent(
            part_number=part.part_number,
            description=part.description,
            manufacturer_code=part.manufacturer_code,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(exc)}")

    llm = agent_output["llm_data"]
    raw_images = agent_output["raw_images"]
    raw_videos = agent_output["raw_videos"]

    # ── Map raw tool outputs to response schema ────────────────────────────

    images = [
        PartImage(
            url=img.get("url", ""),
            title=img.get("title", ""),
            source=img.get("source", ""),
        )
        for img in raw_images
        if img.get("url")
    ]

    videos = [
        YouTubeVideo(
            video_id=v.get("video_id", ""),
            title=v.get("title", ""),
            channel=v.get("channel", ""),
            thumbnail=v.get("thumbnail", ""),
            url=v.get("url", ""),
            description=v.get("description", ""),
        )
        for v in raw_videos
        if v.get("video_id")
    ]

    compatible_vehicles = []
    for v in llm.get("compatible_vehicles", []):
        if isinstance(v, dict) and v.get("year") and v.get("make") and v.get("model"):
            compatible_vehicles.append(
                CompatibleVehicle(
                    year=str(v.get("year", "")),
                    make=str(v.get("make", "")),
                    model=str(v.get("model", "")),
                    trim=str(v.get("trim", "")) if v.get("trim") else None,
                )
            )

    return PartResearchResult(
        part_number=part.part_number,
        description=part.description,
        manufacturer_code=part.manufacturer_code,
        price=part.price,
        images=images,
        detailed_description=llm.get("detailed_description", ""),
        expected_lifetime=llm.get("expected_lifetime", ""),
        maintenance_and_safety=llm.get("maintenance_and_safety", ""),
        failure_symptoms=llm.get("failure_symptoms", ""),
        compatible_vehicles=compatible_vehicles,
        installation_steps=llm.get("installation_steps", []),
        installation_videos=videos,
        sources=llm.get("sources", []),
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "auto-parts-ai"} 