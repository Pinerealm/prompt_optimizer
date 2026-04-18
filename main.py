import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from database import get_recent_optimizations, init_db, log_optimization
from service import optimize_prompt

logger = logging.getLogger(__name__)

app = FastAPI()

try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


@app.get("/health")
def health_check():
    return {"status": "ok"}


class PromptRequest(BaseModel):
    prompt: str = Field(description="The original prompt to optimize")
    goal: str = Field(description="What the prompt should accomplish")
    model_config = {"extra": "forbid"}


class PromptResponse(BaseModel):
    original_prompt: str = Field(description="The original prompt that was submitted")
    optimized_prompt: str = Field(description="The improved version of the prompt")
    changes: str = Field(description="Explanation of what was improved and why")


class OptimizationLog(BaseModel):
    id: int = Field(description="Unique identifier for the optimization log")
    original_prompt: str = Field(description="The original prompt that was submitted")
    optimized_prompt: str = Field(description="The improved prompt")
    changes: str = Field(description="Explanation of what was improved and why")
    created_at: datetime = Field(description="When the optimization was logged")


@app.post("/optimize", response_model=PromptResponse)
def optimize_prompt_endpoint(request: PromptRequest):
    try:
        result = optimize_prompt(request.prompt, request.goal)
    except ValueError as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(
            status_code=502, detail="Invalid upstream LLM response. Please retry."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error. Please try again."
        )

    try:
        log_optimization(
            result["original_prompt"],
            result["optimized_prompt"],
            result["changes"],
        )
    except Exception as e:
        logger.error(f"Failed to log optimization: {e}")

    return PromptResponse(**result)


@app.get("/history", response_model=list[OptimizationLog])
def optimization_history(limit: int = Query(10, ge=1, le=100)):
    try:
        logs = get_recent_optimizations(limit=limit)
        return [OptimizationLog(**log) for log in logs]
    except Exception as e:
        logger.error(f"Failed to fetch optimization history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch optimization history.",
        )
