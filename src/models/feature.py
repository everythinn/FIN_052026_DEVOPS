from pydantic import BaseModel
from typing import Optional


class FeatureCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None


class FeatureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Feature(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    enabled: bool = False
