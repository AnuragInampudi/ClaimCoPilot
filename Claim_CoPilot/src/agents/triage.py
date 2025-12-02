from .base import BaseAgent
from state import ClaimState

class TriageAgent(BaseAgent):
    name = "TriageAgent"

    def run(self, state: ClaimState) -> None:
        """
        Assign a simple priority (High/Medium/Low) and claim_type.
        Uses both extracted fields and raw text.
        """
        fields = state.extracted_fields
        text = " ".join(state.raw_texts).lower()

        amount = float(fields.get("claim_amount", 0.0)) if fields.get("claim_amount") is not None else 0.0
        priority = "Low"
        if "fracture" in text or "injur" in text or "hospital" in text:
            priority = "High"
        elif amount >= 3000:
            priority = "Medium"

        claim_type = fields.get("policy_type", "Unknown")

        state.triage["priority"] = priority
        state.triage["claim_type"] = claim_type

        state.add_trace(self.name, "assign_triage", {
            "priority": priority,
            "claim_type": claim_type,
            "amount": amount,
        })
