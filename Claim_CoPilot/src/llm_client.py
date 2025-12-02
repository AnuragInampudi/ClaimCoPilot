import os
from typing import Optional
from openai import OpenAI

class LLMClient:
   """
   Simple wrapper around OpenAI chat completion.
   If OPENAI_API_KEY is not set, it falls back to a debug 'echo' behavior.
   """
   def __init__(self, model: str = "gpt-4o-mini"):
       self.model = model
       # Check if we actually have an OpenAI key
       self._has_openai = bool(os.environ.get("OPENAI_API_KEY"))
       self._client: Optional[OpenAI] = OpenAI() if self._has_openai else None

   def chat(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
       """
       Send a chat-style prompt to the LLM and return the response text.
       If no API key is set, return a debug string instead (so code doesn't crash).
       """
       if not self._has_openai:
           # Fallback when no key is configured
           return f"[LLM disabled] Would have answered based on: {prompt[:200]!r}"

       messages = []
       if system:
           messages.append({"role": "system", "content": system})
       messages.append({"role": "user", "content": prompt})

       resp = self._client.chat.completions.create(
           model=self.model,
           messages=messages,
           temperature=temperature,
       )
       return resp.choices[0].message.content
