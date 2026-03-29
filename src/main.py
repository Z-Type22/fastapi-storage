from fastapi import FastAPI, Depends, Response
from fastapi.staticfiles import StaticFiles
from src.auth.jwt_service import authorize
from src.users.models import User
from src.users.schemas import UserRead
from src.users.router import router as users_router
from src.auth.router import router as auth_router
from src.videos.router import router as videos_router
from fastapi_csrf_protect import CsrfProtect
from src.middlewares import CSRFMiddleware


app = FastAPI()

app.add_middleware(CSRFMiddleware)

app.mount("/media/avatars", StaticFiles(directory="media/avatars"), name="media_avatars")

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(videos_router, prefix="/videos", tags=["Audios"])

@app.get("/csrf-token")
def get_csrf_token(
    response: Response,
    csrf_protect: CsrfProtect = Depends()
):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)
    return {"csrf_token": csrf_token}

@app.get("/", response_model=UserRead)
async def root(user: User = Depends(authorize)):
    return user
