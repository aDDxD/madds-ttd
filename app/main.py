from fastapi import FastAPI

from app.routes import streamlit
from app.utils.utils import lifespan

# Initialize the FastAPI app with the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Include the routes from the routes folder
app.include_router(streamlit.router)
