from fastapi import APIRouter, HTTPException
from src.models.group import GroupCreate, GroupUpdate, Group
import src.storage as storage

router = APIRouter(prefix="/api/groups", tags=["groups"])

@router.post("", response_model=Group, status_code=201)
def create_group(group: GroupCreate):
    for g in storage.groups:
        if g["name"] == group.name:
            raise HTTPException(status_code=409, detail="Group already exists")
    
    new_group = {
        "id": storage.next_group_id,
        "name": group.name,
        "description": group.description,
        "user_ids": []
    }
    storage.groups.append(new_group)
    storage.next_group_id += 1
    return new_group

@router.get("", response_model=list[Group], status_code=200)
def get_groups():
    return storage.groups

@router.get("/{group_id}", response_model=Group, status_code=200)
def get_group(group_id: int):
    for g in storage.groups:
        if g["id"] == group_id:
            return g
    raise HTTPException(status_code=404, detail="Group not found")

@router.patch("/{group_id}", response_model=Group, status_code=200)
def update_group(group_id: int, group: GroupUpdate):
    for g in storage.groups:
        if g["id"] == group_id:
            if group.name is not None:
                for other in storage.groups:
                    if other["name"] == group.name and other["id"] != group_id:
                        raise HTTPException(status_code=409, detail="Group name already exists")
                g["name"] = group.name
            if group.description is not None:
                g["description"] = group.description
            return g
    raise HTTPException(status_code=404, detail="Group not found")

@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int):
    for i, g in enumerate(storage.groups):
        if g["id"] == group_id:
            storage.groups.pop(i)
            return
    raise HTTPException(status_code=404, detail="Group not found")

@router.post("/{group_id}/users/{user_id}", status_code=201)
def add_user_to_group(group_id: int, user_id: int):
    # Vérifier que le groupe existe
    group = None
    for g in storage.groups:
        if g["id"] == group_id:
            group = g
            break
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # Vérifier que l'user existe
    user = None
    for u in storage.users:
        if u["id"] == user_id:
            user = u
            break
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Vérifier que l'user n'est pas déjà dans le groupe
    if user_id in group["user_ids"]:
        raise HTTPException(status_code=409, detail="User already in group")

    group["user_ids"].append(user_id)
    return {"message": "User added to group"}

@router.delete("/{group_id}/users/{user_id}", status_code=204)
def remove_user_from_group(group_id: int, user_id: int):
    for g in storage.groups:
        if g["id"] == group_id:
            if user_id not in g["user_ids"]:
                raise HTTPException(status_code=404, detail="User not in group")
            g["user_ids"].remove(user_id)
            return
    raise HTTPException(status_code=404, detail="Group not found")

@router.get("/{group_id}/users", status_code=200)
def get_group_users(group_id: int):
    for g in storage.groups:
        if g["id"] == group_id:
            users = [u for u in storage.users if u["id"] in g["user_ids"]]
            return users
    raise HTTPException(status_code=404, detail="Group not found")