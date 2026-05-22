## Airline Agentic Assistant

This project is an agentic aviation assistant that answers Boeing 737 Operations Manual questions using FastAPI, OpenAI’s Responses API and a hybrid RAG pipeline. The agent can search the manual, look up performance tables, and call datetime, weather tools—without LangChain agents or the OpenAI Agents SDK.

It supports:

- Normal text queries — procedures, policies, limitations (semantic search + LLM reranking)
- Numeric / table queries — takeoff climb limit, field limit, obstacle limit weights (structured table extraction)
- Tool-augmented queries — current UTC time and live weather for any city

The assistant exposes a single /ask API endpoint and returns:
- The final grounded answer
- Document/page references
- The ordered sequence of tool calls made by the agent

-----------------------------------------------------------

### Step-by-step workflow

#### *A. End-to-end request (what happens on /ask)*
 
1. A user sends a query to the /ask endpoint.
2. FastAPI validates the query (empty queries return an error message).
3. The agent loop runs until the model produces a final answer or hits the iteration limit.
4. The API returns:
Answer — final text from the model

References — manual title + page numbers from search results
- Tool_calls — ordered log of every tool the agent invoked
