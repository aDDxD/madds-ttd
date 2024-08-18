import os


class Config:
    # Configuration class to fetch environment variables
    DW_DATABASE_URL = os.getenv("DW_DATABASE_URL")
    OLTP_DATABASE_URL = os.getenv("OLTP_DATABASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
