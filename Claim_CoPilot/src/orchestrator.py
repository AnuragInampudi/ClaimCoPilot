from typing import Optional
from llm_client import LLMClient
from state import ClaimState
from agents.extraction import ExtractionAgent
from agents.validation import ValidationAgent
from agents.triage import TriageAgent
from agents.summarization import SummarizationAgent

class Orchestrator:
    """
    Runs a list of agents over a claim until it is 'complete'.
    """
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient()
        self.agents = [
            ExtractionAgent(self.llm),
            ValidationAgent(self.llm),
            TriageAgent(self.llm),
            SummarizationAgent(self.llm),
        ]

    def run(self, text: str) -> ClaimState:
        """
        Create a ClaimState, pass it through agents, and return the final state.
        """
        state = ClaimState.from_single_text(text)
        for agent in self.agents:
            agent.run(state)
            if state.is_complete():
                break
        return state
