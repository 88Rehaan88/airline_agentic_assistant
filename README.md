### Airline Agentic Assistant

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
