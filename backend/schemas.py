from pydantic import BaseModel
from typing import List


class CampaignBrief(BaseModel):
    campaign_name: str
    product: str
    goal: str
    audience: str
    budget: float
    channels: List[str]
    tone: str
    duration_days: int