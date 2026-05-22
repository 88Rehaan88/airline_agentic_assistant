# Airline Agentic Assistant


## 1. Project Overview:
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

## 2. Step-by-step workflow

## System Workflow Diagram:

<img width="711" height="1081" alt="dark green drawio" src="https://github.com/user-attachments/assets/e0352520-cd15-45b3-ab08-d7c41485f1e9" />


-----------------------------------------------------------


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

## 3. Handling Tool Errors and Runaway Loops:

### 1. Tool Error Handling:

Tool execution is wrapped in try/except blocks inside the agent loop.

If a tool fails:
- the loop does not crash
- the exception is converted into afallback error message. 
- the error output is fed back into the model as a normal tool response

This allows the model to:
- recover gracefully
- retry with different reasoning
- or produce a fallback response

This design keeps the agent loop robust even when:
- external APIs fail
- retrieval returns invalid data
- tool arguments are malformed

### 2. Runaway Loop Protection:

The agent loop can call the model multiple times in one request (tool call → result → model again). To avoid endless tool-calling:
- The agent loop is protected using a fixed max_iterations limit.
- The loop terminates automatically
- And the API returns a safe fallback response

This prevents:
- infinite tool-calling loops
- excessive token usage
- Accidental API cost escalation

-------------------------------------

## 4. Tradeoffs: 

### 1. **Manual Agent Loop Instead of Agent Frameworks:**

**Choice:** The entire tool-calling loop was implemented manually instead of using LangChain Agents, AutoGen, CrewAI, or the OpenAI Agents SDK.

**Why:** Gives full control over tool execution, logging, error handling, safety limits etc

**Trade-off:**  But this has more implementation complexity and more boilerplate than using a framework.

### 2. Hybrid RAG instead of one retrieval path:

**Choice:** Split manual search into a normal text path (FAISS + rerank) and a numeric table path (page selection + structured table extraction).

**Why:** Boeing performance pages look almost identical in embedding space, a single semantic path often picks the wrong table.

**Trade-off:** More moving parts and two code paths to maintain, but much better results on performance-style questions than FAISS alone.

### **3. LLM-based table reading vs. deterministic parsing:**
   
**Choice:** Extract tables offline with pdfplumber, then use a stronger model (GPT-4o) to pick the page and read the cell.

**Why:** PDF tables are messy; hard-coded parsers would be fragile across many table layouts.

**Trade-off:** Faster to build and works well for most common cases (e.g. climb limit at 2000 ft / 50°C), but not reliable on every table (obstacle grids, different altitudes/OAT columns). A deterministic lookup would be more accurate but take longer to implement.

### 4. **Stateless Agent Loop (No Conversation Memory):**

**Choice:** Each /ask request is handled on its own. The agent loop does not store chat history or long-term memory between calls.

**Why:** Reduces complexity and keeps the system simpler and easier to debug, test, and evaluate since every response depends only on the current query and tool outputs, not earlier conversation history that may be incorrect or irrelevant. The model is also less likely to carry forward incorrect assumptions from previous turns.

**Trade-off:** The assistant cannot maintain long multi-turn conversations (e.g. “What was the climb limit you gave me a minute ago?” . 

eg. “Compare the weather in both cities from my last two questions.”).

-----------------------------------

## 5. Limitations and Future Improvements:

### 1. Table Extraction:

The current system uses pdfplumber for table extraction, which works reasonably well for basic table queries but struggles with some complex or double table layouts and merged cells.

Future improvements could include implementing tools like Camelot or Tabula, which provide:
- better structured table parsing
- improved row/column alignment
- more reliable handling of aviation performance tables

This would improve numeric query robustness further.

### 2. OCR and Image Understanding:

Some parts of the manual contain diagrams, charts, or image-based information that are not captured well through text extraction alone.

A future improvement would be:
- OCR integration
- Multimodal/image understanding pipelines

This would allow the assistant to answer questions grounded in visual manual content as well.

### 4. Conversation Memory and Multi-Turn Context

The current assistant is intentionally stateless.

Future versions could support:
- multi-turn conversations
- conversational memory
- follow-up clarification questions

while still maintaining grounding and loop safety.

----------------------

## 6. Setup & Installation:

### ⚠️Important Note (for API queries)

Please avoid including double-quotes (") inside your query text.
Certain characters can interfere with request parsing in FastAPI/Swagger and may cause the query to fail.
Use normal text instead of quoted phrases. 

--------------------------------------------------

1. Clone the Repository:

git clone https://github.com/88Rehaan88/airline_agentic_assistant.git

cd airline_agentic_assistant

2. Create & Activate Virtual Environment

python -m venv venv
- venv\Scripts\activate          # Windows
- source venv/bin/activate     # macOS/Linux

3. Install Dependencies:

pip install -r requirements.txt

4. Configure environment variables

 Create a .env file (or copy .env.example to .env file) add your OpenAI key:

OPENAI_API_KEY=your_key_here

5. Manual and index:

The repo includes:
- data/Boeing B737 Manual.pdf
- Pre-built files in index/ (faiss.index, chunks.json, tables.json)

No extra build step is required to start the API.

6. Start the server:

uvicorn main:app --reload

Once running, open Swagger UI at:

http://localhost:8000/docs

Use POST /ask with a JSON body like:

{ "query": "your question here" }

Note: If port 8000 is busy, use another port, e.g. uvicorn main:app --reload --port 8001 

-----------------------
