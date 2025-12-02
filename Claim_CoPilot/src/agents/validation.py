import json
from .base import BaseAgent
from state import ClaimState

class ValidationAgent(BaseAgent):
    name = "ValidationAgent"

    def run(self, state: ClaimState) -> None:
        """
        Check for missing fields and simple contradictions.
        Ask the LLM to provide a short QA note.
        """
        issues = []

        required = ["claimant_name", "policy_type", "claim_amount", "incident_date"]
        for field in required:
            if field not in state.extracted_fields:
                issues.append(f"Missing field: {field}")

        # Example contradiction: multiple policy types in raw text
        text = " ".join(state.raw_texts)
        found = [p for p in ["Health", "Auto", "Property"] if p.lower() in text.lower()]
        if len(set(found)) > 1:
            issues.append(f"Multiple policy types mentioned in text: {found}")

        prompt = f"""
You are a claims QA checker.

Text:
{text}

Extracted fields:
{json.dumps(state.extracted_fields)}

1) Note any missing fields (claimant_name, policy_type, claim_amount, incident_date).
2) Note any contradictions.

Reply with 2-4 bullet points.
"""
        note = self.llm.chat(
            prompt,
            system="You are a precise and concise QA checker.",
            temperature=0.2,
        )
        if note:
            state.issues.append(f"LLM-note: {note}")

        for iss in issues:
            state.issues.append(iss)

        state.add_trace(self.name, "validate_fields", {
            "issues": issues,
            "llm_note_present": bool(note),
        })
