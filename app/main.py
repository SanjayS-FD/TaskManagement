from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.auth import verify_password
from app.schemas import LoginRequest

from app.auth import create_access_token
from app.database import Base, engine, get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password
from app.auth import verify_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API")

@app.get("/")
def home():
    return {"message": "API is running"}


def get_current_user(
    Authorization: str = Header(None)
):
    print("AUTH =", Authorization)

    if not Authorization:
        raise HTTPException(
            status_code=401,
            detail="Token missing"
        )

    token = Authorization.replace(
        "Bearer ",
        ""
    )

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return payload


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can create users"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        role=user.role,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    users = db.query(User).all()
    return users

@app.post("/login")
def login(login_data: LoginRequest,
          db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:
        return {"message": "Invalid username"}

    if not verify_password(login_data.password,user.password):
        return {"message": "Invalid password"}

    token = create_access_token(
    {
        "sub": user.username,
        "role": user.role
    }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete users"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }

@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user