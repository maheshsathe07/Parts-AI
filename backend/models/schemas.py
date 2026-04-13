from pydantic import BaseModel
from typing import Optional


class PartInput(BaseModel):
    part_number: str
    description: str
    manufacturer_code: str


class ResearchRequest(BaseModel):
    dataframe_records: list[PartInput]


class PartImage(BaseModel):
    url: str
    title: str
    source: str


class YouTubeVideo(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    url: str
    description: str


class CompatibleVehicle(BaseModel):
    year: str
    make: str
    model: str
    trim: Optional[str] = None

class PartResearchResult(BaseModel):
    part_number: str
    description: str
    manufacturer_code: str
    price: Optional[float] = None
    images: list[PartImage]
    detailed_description: str
    expected_lifetime: str
    maintenance_and_safety: list[str]
    failure_symptoms: list[str]
    compatible_vehicles: list[CompatibleVehicle]
    installation_steps: list[str]
    installation_videos: list[YouTubeVideo]
    sources: list[str]

class Prediction(BaseModel):
    predictions: PartResearchResult