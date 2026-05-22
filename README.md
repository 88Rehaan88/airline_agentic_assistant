# Airline Agentic Assistant


## Project Overview:
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

## Step-by-step workflow

#### *A. End-to-end request (what happens on /ask)*
 
1. A user sends a query to the /ask endpoint.
2. FastAPI validates the query (empty queries return an error message).
3. The agent loop runs until the model produces a final answer or hits the iteration limit.
4. The API returns:
   - Answer — final text from the model
   - References — manual title + page numbers from search results
   - Tool_calls — ordered log of every tool the agent invoked

-------------------------------------------------------------------

#### *B. Agent loop (how the agent works):*

1. User asks a question
The question is sent to the /ask endpoint.

2. Agent loop starts
A hand-rolled loop calls the OpenAI Responses API. The gpt-4o-mini model decides whether it needs tools or can answer directly.

3. Tools run when needed
The agent can call:
- Search documentation — Search the Boeing 737 manual
- Get current datetime — UTC or local date and time for major cities. 
- Get weather — Live weather conditions for a city

4. Inside search_documentation (hybrid RAG)
Every manual question goes through this path when the agent calls search_documentation:

A. Embed & retrieve — Embed the query and fetch the top 8 chunks from FAISS.

B. Classify — If a query has ≥2 numbers and a performance/table keyword (e.g. climb limit, OAT, pressure altitude), we treat it as a numeric_query.

C. Branch

*a. Normal (text) path:*
- Rerank candidates with gpt-4o-mini and keep the top 2 chunks.
- Format chunk text with document title and page number.
- Return formatted text + chunks for references.

*b. Numeric (table) path:*
- Gpt-4o selects the single best page from the 8 candidates.
- Load raw tables for that page from tables.json using pdfplumber.
- Gpt-4o reads structured tables + page context and returns one value (e.g. 52.2 (1000 KG)), or NOT FOUND.
- Format the answer in a proper sentence so the agent can report it clearly.
- If extraction fails, fall back to the normal rerank path.


5. Results go back to the agent:
Tool outputs are returned to the model. It may call more tools or write the final answer.

6. Response to the user
The API returns the answer, which manual pages were used, and which tools were called.

---------------------------------------------------------------

