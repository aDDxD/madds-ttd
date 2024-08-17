from typing import List
from pydantic import BaseModel


class VisualizationItem(BaseModel):
    description: str
    sql_query: str
    visualization: str
    plotly_express_function: str


class DataAnalysisResponse(BaseModel):
    visualizations: List[VisualizationItem]
