import subprocess
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app):
    # Start Streamlit as a subprocess, served on port 8501 during startup
    process = subprocess.Popen(
        ["streamlit", "run", "app/services/streamlit.py", "--server.port=8501"]
    )
    try:
        yield
    finally:
        # Ensure the Streamlit subprocess is terminated during shutdown
        process.terminate()
