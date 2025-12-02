from abc import ABC, abstractmethod
from typing import Optional
from llm_client import LLMClient
from state import ClaimState

class BaseAgent(ABC):
    """
    Abstract base class for all agents in ClaimCopilot.
    Each agent:
      - Has a name
      - Has access to an LLMClient
      - Implements run(state) which modifies the ClaimState in place.
    """
    name: str = "BaseAgent"

    def __init__(self, llm: Optional[LLMClient] = None):
        # If no LLM is supplied, create a default one
        self.llm = llm or LLMClient()

    @abstractmethod
    def run(self, state: ClaimState) -> None:
        """
        Perform this agent's operation on the given ClaimState.
        This method should update state.* and add a trace entry.
        """
        ...
