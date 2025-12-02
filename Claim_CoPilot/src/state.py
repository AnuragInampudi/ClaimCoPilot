import json
import time
from typing import Any, Dict, List, Optional

class ClaimState:
    """
    Shared state for one insurance claim as it moves through the agents.
    """
    def __init__(self, raw_texts: List[str]):
        # Original text(s) for this claim (e.g., combined from multiple docs)
        self.raw_texts: List[str] = raw_texts

        # Structured information extracted from text
        self.extracted_fields: Dict[str, Any] = {}

        # Triage decisions (priority, claim_type, etc.)
        self.triage: Dict[str, Any] = {}

        # Final human-readable summary string
        self.summary: Optional[str] = None

        # Any issues flagged by agents (missing fields, contradictions, etc.)
        self.issues: List[str] = []

        # Trace of what each agent did (for explainability)
        self.trace: List[Dict[str, Any]] = []

    @classmethod
    def from_single_text(cls, text: str) -> "ClaimState":
        """
        Convenience constructor when you just have one big text string.
        """
        return cls([text])

    def add_trace(self, agent: str, action: str, info: Optional[Dict[str, Any]] = None) -> None:
        """
        Record what an agent did, when, and what it produced.
        """
        self.trace.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent": agent,
            "action": action,
            "info": info or {}
        })

    def is_complete(self) -> bool:
        """
        Decide if the claim is 'ready':
        - Required fields exist
        - Summary is not None
        """
        required = ["claimant_name", "policy_type", "claim_amount", "incident_date"]
        missing = [f for f in required if f not in self.extracted_fields]
        return len(missing) == 0 and self.summary is not None

    def to_json(self) -> str:
        """
        Serialize the entire state to pretty JSON (for saving / debugging).
        """
        return json.dumps({
            "raw_texts": self.raw_texts,
            "extracted_fields": self.extracted_fields,
            "triage": self.triage,
            "summary": self.summary,
            "issues": self.issues,
            "trace": self.trace,
        }, indent=2)
