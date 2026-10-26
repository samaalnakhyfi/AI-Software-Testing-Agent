import ollama

from agent.config import OLLAMA_MODEL


class AIUnavailableError(RuntimeError):
    """Raised when the local Ollama model cannot be reached or fails."""


def ask_model(prompt, model=OLLAMA_MODEL):
    """Send a single prompt to the local Ollama model and return its reply text."""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except ollama.ResponseError as error:
        raise AIUnavailableError(
            f"Ollama returned an error for model '{model}': {error.error}. "
            f"Try: ollama pull {model}"
        ) from error
    except Exception as error:
        raise AIUnavailableError(
            f"Could not reach Ollama ({error}). Make sure it is running: ollama serve"
        ) from error

    return response["message"]["content"].strip()
