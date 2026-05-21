from fastapi import APIRouter, HTTPException
from src.models.feature import FeatureCreate, FeatureUpdate, Feature
from src.services.feature_evaluator import evaluate_feature_access
import src.storage as storage

router = APIRouter(prefix="/api/features", tags=["features"])


@router.post("", response_model=Feature, status_code=201)
def create_feature(feature: FeatureCreate):
    for f in storage.features:
        if f["key"] == feature.key:
            raise HTTPException(status_code=409, detail="Feature already exists")

    new_feature = {
        "key": feature.key,
        "name": feature.name,
        "description": feature.description,
        "enabled": False,
        "env_configs": {}
    }
    storage.features.append(new_feature)
    return new_feature


@router.get("", response_model=list[Feature], status_code=200)
def get_features():
    return storage.features


@router.get("/{key}", response_model=Feature, status_code=200)
def get_feature(key: str):
    for f in storage.features:
        if f["key"] == key:
            return f
    raise HTTPException(status_code=404, detail="Feature not found")


@router.patch("/{key}", response_model=Feature, status_code=200)
def update_feature(key: str, feature: FeatureUpdate):
    for f in storage.features:
        if f["key"] == key:
            if feature.name is not None:
                f["name"] = feature.name
            if feature.description is not None:
                f["description"] = feature.description
            return f
    raise HTTPException(status_code=404, detail="Feature not found")


@router.delete("/{key}", status_code=204)
def delete_feature(key: str):
    for i, f in enumerate(storage.features):
        if f["key"] == key:
            storage.features.pop(i)
            return
    raise HTTPException(status_code=404, detail="Feature not found")


@router.patch("/{key}/enable", response_model=Feature, status_code=200)
def enable_feature(key: str):
    for f in storage.features:
        if f["key"] == key:
            f["enabled"] = True
            return f
    raise HTTPException(status_code=404, detail="Feature not found")


@router.patch("/{key}/disable", response_model=Feature, status_code=200)
def disable_feature(key: str):
    for f in storage.features:
        if f["key"] == key:
            f["enabled"] = False
            return f
    raise HTTPException(status_code=404, detail="Feature not found")


@router.put("/{key}/environments/{env}/config", status_code=200)
def set_env_config(key: str, env: str, config: dict):
    # Vérifier que la feature existe
    for f in storage.features:
        if f["key"] == key:
            # Vérifier que l'environnement existe
            env_exists = any(e["name"] == env for e in storage.environments)
            if not env_exists:
                raise HTTPException(status_code=404, detail="Environment not found")
            f["env_configs"][env] = config
            return f["env_configs"][env]
    raise HTTPException(status_code=404, detail="Feature not found")


@router.get("/{key}/environments/{env}/config", status_code=200)
def get_env_config(key: str, env: str):
    for f in storage.features:
        if f["key"] == key:
            if env not in f["env_configs"]:
                raise HTTPException(status_code=404, detail="Config not found")
            return f["env_configs"][env]
    raise HTTPException(status_code=404, detail="Feature not found")


@router.delete("/{key}/environments/{env}/config", status_code=204)
def delete_env_config(key: str, env: str):
    for f in storage.features:
        if f["key"] == key:
            if env not in f["env_configs"]:
                raise HTTPException(status_code=404, detail="Config not found")
            del f["env_configs"][env]
            return
    raise HTTPException(status_code=404, detail="Feature not found")

@router.get("/{key}/evaluate", status_code=200)
def evaluate_feature(key: str, userId: int, env: str):
    # 1. Trouver la feature
    feature = None
    for f in storage.features:
        if f["key"] == key:
            feature = f
            break
    if feature is None:
        raise HTTPException(status_code=404, detail="Feature not found")

    # 2. Trouver l'utilisateur
    user = None
    for u in storage.users:
        if u["id"] == userId:
            user = u
            break
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Récupérer la config de l'environnement
    config = feature.get("env_configs", {}).get(env, None)

    # 4. Récupérer les groupes de l'utilisateur
    user_groups = []
    for g in storage.groups:
        if userId in g["user_ids"]:
            user_groups.append(g["name"])

    # 5. Évaluer
    result = evaluate_feature_access(feature, config, user, user_groups)

    return {
        "feature": key,
        "enabled": result["enabled"],
        "reason": result["reason"]
    }
