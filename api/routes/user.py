from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/me")
async def me(request: Request):
    user_data = request.state.user_data

    return JSONResponse(user_data, 200)
