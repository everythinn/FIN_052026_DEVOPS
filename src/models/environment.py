from pydantic import BaseModel
from typing import Optional

class EnvironmentCreate(BaseModel):
    name: str
    description: Optional[str] = None

class EnvironmentUpdate(BaseModel):
    description: Optional[str] = None

class Environment(BaseModel):
    name: str
    description: Optional[str] = None
