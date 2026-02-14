import os
import json
from typing import Any, Dict, List
from openai import AsyncOpenAI
from mcp import Tool

# Initialize client
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Standard Text-to-SQL Prompt (for simple queries)
SCENARIOS = {
    "db": (
        "You are a SQL expert. Convert the user request to a SQLite query. "
        "Schema: users(id, username, role), secrets(id, api_key, owner). "
        "Return ONLY the SQL string."
    ),
}

async def llm(input_text: str, prompt: str = "db", system_prompt: str | None = None, model: str = "gpt-4o") -> str:
    """Simple Text-to-Text generation."""
    system_instruction = system_prompt or SCENARIOS.get(prompt, "You are a helpful assistant.")
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": input_text},
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"