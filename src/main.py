from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from src.auth.jwt_service import authorize
from src.users.models import User
from src.users.schemas import UserRead
from src.users.router import router as users_router
from src.auth.router import router as auth_router


app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/", response_model=UserRead)
async def root(user: User = Depends(authorize)):
    return user
