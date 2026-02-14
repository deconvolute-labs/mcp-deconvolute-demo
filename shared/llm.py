import os
from openai import AsyncOpenAI

# Initialize the client strictly once or per call depending on preference. 
# Here we instantiate per module load, assuming env var is set.
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define the scenarios/system prompts
SCENARIOS = {
    "db": (
        "You are a SQL expert assisting a user with querying a security demo database. "
        "Convert the user's natural language request into a valid SQL query. "
        "Return ONLY the SQL query, no markdown formatting, no explanations.\n\n"
        "Database Schema:\n"
        "1. Table 'users':\n"
        "   - id (INTEGER PRIMARY KEY)\n"
        "   - username (TEXT)\n"
        "   - role (TEXT)\n\n"
        "2. Table 'secrets':\n"
        "   - id (INTEGER PRIMARY KEY)\n"
        "   - api_key (TEXT)\n"
        "   - owner (TEXT)\n"
    ),
    "default": "You are a helpful assistant."
}

async def llm(input_text: str, prompt: str = "db", model: str = "gpt-4o") -> str:
    """
    Process input using an LLM with a specific scenario prompt.
    
    Args:
        input_text: The raw user string.
        prompt: The key for the system prompt to use (default: 'db').
        model: The model identifier to use (default: 'gpt-4o').
        
    Returns:
        The text content of the LLM's response.
    """
    system_instruction = SCENARIOS.get(prompt, SCENARIOS["default"])

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": input_text},
            ],
            temperature=0,  # Deterministic for code/SQL generation
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling LLM: {str(e)}"