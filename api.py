from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json


from agno.agent import Agent

# from agno.models.openai.chat import OpenAIChat as OpenAI
from agno.models.ollama import Ollama

from agno.tools.yfinance import YFinanceTools
import logging
import os

app = FastAPI(title="Agno Agent API")


def clean_answer(raw: str):
    """Remove markdown fences, backticks, and newline characters from the raw answer.
    If the cleaned string contains a JSON object with an "answer" key, return that dict.
    Otherwise return the cleaned string.
    """
    # Strip surrounding whitespace
    cleaned = raw.strip()
    # Remove markdown code fences if present
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned.strip("`")
    cleaned = cleaned.strip()
    # Remove escaped newline sequences and actual newlines
    cleaned = cleaned.replace("\\n", "").replace("\n", "").replace("\r", "")
    # Remove any stray backticks
    cleaned = cleaned.replace("`", "")
    # Try to parse JSON
    try:
        inner = json.loads(cleaned)
        if isinstance(inner, dict) and "answer" in inner:
            return inner
    except Exception:
        pass
    return cleaned


# Configure basic logging (stdout)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")
logger.info("Ollama URL from env: %s", os.getenv("OLLAMA_HOST", "not set"))


class QueryRequest(BaseModel):
    question: str


# Initialize the agent once at startup
agent = Agent(
    # model=OpenAI(id="gpt-4o-mini"),
    model=Ollama(id="llama3.2"),
    tools=[YFinanceTools(stock_price=True)],
    instructions=""" 
    You must always respond with a valid and clean JSON object containing a single key called "answer".

    The value of "answer" must be an array of objects, each using the stock code as the key and the corresponding price as the value, for example:

    {"answer":[{"AAPL":229.35},{"PETR4":129.98}]}.

    Always use only the stock code (e.g., "AAPL", "PETR4") as the key, and only the price as a numerical value.

    Do not include any additional text, markdown, explanations, or line break characters—return only the compact JSON response on a single line.

    If the answer cannot be provided in this format, respond with: {"error":"Invalid JSON format requested"}.
    """,
    markdown=False,
)


@app.post("/query")
async def query_agent(request: QueryRequest):
    """Accept a question and return the agent's answer.

    The endpoint runs the Agno agent synchronously (stream=False) and extracts the
    final response content. If anything goes wrong, a 500 error is returned.
    """
    logger.info("Received query: %s", request.question)
    try:
        # Run the agent synchronously (stream=False) which returns a object.
        run_response = agent.run(request.question, stream=False)
        # Extract the content if available; otherwise return an empty string.
        answer = getattr(run_response, "content", "") or ""
        logger.info("Agent response generated")
        # Clean possible markdown fences and newlines
        cleaned = clean_answer(answer)
        # If clean_answer returned a dict, handle possible error
        if isinstance(cleaned, dict):
            if "error" in cleaned:
                err = cleaned["error"]
                # Use provided code if present, otherwise default to 500
                status = err.get("code", 500) if isinstance(err, dict) else 500
                message = (
                    err.get("message", "Error") if isinstance(err, dict) else str(err)
                )
                raise HTTPException(status_code=status, detail=message)
            # No error, return the dict (should contain "answer")
            return cleaned
        # cleaned is a string – try to parse it as JSON to detect error
        try:
            inner = json.loads(cleaned)
            if isinstance(inner, dict) and "error" in inner:
                err = inner["error"]
                status = err.get("code", 500) if isinstance(err, dict) else 500
                message = (
                    err.get("message", "Error") if isinstance(err, dict) else str(err)
                )
                raise HTTPException(status_code=status, detail=message)
            # If inner dict has "answer", return it
            if isinstance(inner, dict) and "answer" in inner:
                return inner
        except Exception:
            pass
        # Fallback: return the cleaned string as answer
        return {"answer": cleaned}
    except Exception as exc:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(exc))
