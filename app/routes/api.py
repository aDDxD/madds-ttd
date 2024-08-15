import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.prompt_service import process_query

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    query: str


@router.post("/process_query/")
async def process_query_endpoint(request: QueryRequest):
    try:
        result_df, sql_query, visualization_suggestions = process_query(request.query)
        return {
            "result": result_df.to_dict(orient="records"),
            "sql_query": sql_query,
            "visualization_suggestions": visualization_suggestions,
        }
    except ValueError as e:
        logger.error("Error processing query: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error processing query: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the query.",
        )
