from fastapi import APIRouter, HTTPException
from src.models.environment import EnvironmentCreate, EnvironmentUpdate, Environment
import src.storage as storage

router = APIRouter(prefix="/api/environments", tags=["environments"])

@router.post("", response_model=Environment, status_code=201)
def create_environment(env: EnvironmentCreate):
    for e in storage.environments:
        if e["name"] == env.name:
            raise HTTPException(status_code=409, detail="Environment already exists")
    
    new_env = {
        "name": env.name,
        "description": env.description
    }
    storage.environments.append(new_env)
    return new_env

@router.get("", response_model=list[Environment], status_code=200)
def get_environments():
    return storage.environments

@router.get("/{name}", response_model=Environment, status_code=200)
def get_environment(name: str):
    for e in storage.environments:
        if e["name"] == name:
            return e
    raise HTTPException(status_code=404, detail="Environment not found")

@router.patch("/{name}", response_model=Environment, status_code=200)
def update_environment(name: str, env: EnvironmentUpdate):
    for e in storage.environments:
        if e["name"] == name:
            if env.description is not None:
                e["description"] = env.description
            return e
    raise HTTPException(status_code=404, detail="Environment not found")

@router.delete("/{name}", status_code=204)
def delete_environment(name: str):
    for i, e in enumerate(storage.environments):
        if e["name"] == name:
            storage.environments.pop(i)
            return
    raise HTTPException(status_code=404, detail="Environment not found")