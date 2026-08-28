from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.schemas import LoginRequest, TaskUpdate

from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.auth import create_access_token
from app.database import Base, engine, get_db, SessionLocal
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password
from app.auth import verify_token

Base.metadata.create_all(bind=engine)

# Seed Admin User
db = SessionLocal()

admin = db.query(User).filter(
    User.username == "admin"
).first()

if not admin:
    admin = User(
        username="admin",
        email="admin@test.com",
        password=hash_password("root"),
        role="admin"
    )

    db.add(admin)
    db.commit()

db.close()

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


#get user object for tasks creation
def get_db_user(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == current_user["sub"]
    ).first()

    return user


#create tasks
@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db_user)
):
    
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id,
        status="Pending"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db_user)
):

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can update only your own tasks"
        )

    task.title = task_data.title
    task.description = task_data.description
    task.status = task_data.status

    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db_user)
):

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own tasks"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }


@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user