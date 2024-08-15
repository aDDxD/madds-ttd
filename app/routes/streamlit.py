from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/")
def streamlit_app():
    return RedirectResponse(url="http://localhost:8501")
