# API endpoint for interacting with the agent.
# Accepts a user query, runs the agent loop,
# and returns the final answer along with references and tool-call history.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.loop import run

router = APIRouter()

# Input schema for user queries:
class AskRequest(BaseModel):
    query: str

# Stores document/page references used while answering:
class Reference(BaseModel):
    document_title: str
    pages: list[int]

# Stores the ordered sequence of tool calls made by the agent:
class ToolCall(BaseModel):
    tool: str
    arguments: dict

# Final structured API response:
class AskResponse(BaseModel):
    answer: str
    references: list[Reference]
    tool_calls: list[ToolCall]


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.query.strip(): # Prevents empty requests:
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    
    # Run the manual agent loop:
    result = run(request.query)
    return result
