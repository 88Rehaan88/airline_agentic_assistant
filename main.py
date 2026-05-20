# FastAPI application entry point
# Sets up the API routes and starts the server for the airline assistant.

# Run locally using:
# uvicorn main:app --reload
# (Use --port 8001 if port 8000 is already in use)

import uvicorn
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Airline Agentic Assistant",
    description="Answers airline travel questions using a manual agent loop over the Boeing 737 Operations Manual.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Starts the FastAPI server:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
