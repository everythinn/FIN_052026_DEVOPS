from fastapi import APIRouter, HTTPException
from src.models.user import UserCreate, UserUpdate, User
import src.storage as storage

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=User, status_code=201)
def create_user(user: UserCreate):
    global storage
    # Vérifier si l'email existe déjà
    for u in storage.users:
        if u["email"] == user.email:
            raise HTTPException(status_code=409, detail="Email already exists")

    new_user = {
        "id": storage.next_user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }
    storage.users.append(new_user)
    storage.next_user_id += 1
    return new_user

@router.get("", response_model=list[User], status_code=200)
def get_users():
    return storage.users

@router.get("/{user_id}", response_model=User, status_code=200)
def get_user(user_id: int):
    for u in storage.users:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")

@router.patch("/{user_id}", response_model=User, status_code=200)
def update_user(user_id: int, user: UserUpdate):
    for u in storage.users:
        if u["id"] == user_id:
            if user.email is not None:
                # Vérifier si le nouvel email existe déjà
                for other in storage.users:
                    if other["email"] == user.email and other["id"] != user_id:
                        raise HTTPException(
                            status_code=409, detail="Email already exists"
                            )
                u["email"] = user.email
            if user.name is not None:
                u["name"] = user.name
            if user.role is not None:
                u["role"] = user.role
            return u
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    for i, u in enumerate(storage.users):
        if u["id"] == user_id:
            storage.users.pop(i)
            return
    raise HTTPException(status_code=404, detail="User not found")