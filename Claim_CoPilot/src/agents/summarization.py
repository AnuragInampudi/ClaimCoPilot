import json
from .base import BaseAgent
from state import ClaimState

class SummarizationAgent(BaseAgent):
    name = "SummarizationAgent"

    def run(self, state: ClaimState) -> None:

        text = " ".join(state.raw_texts)
        fields = state.extracted_fields
        triage = state.triage

        prompt = f"""
You are an insurance claim summarization assistant.

Original text:
{text}

Extracted fields:
{json.dumps(fields)}

Triage info:
{json.dumps(triage)}

Write a concise, factual summary (4-6 sentences) so a claim adjuster can quickly understand:
- Who is involved
- What happened and when
- Policy type and claim amount
- Priority and any notable issues

Do not hallucinate information not supported by the text.
"""
        summary = self.llm.chat(
            prompt,
            system="You summarize insurance claims accurately.",
            temperature=0.3,
        )
        state.summary = summary

        state.add_trace(self.name, "summarize_claim", {
            "summary_preview": summary[:120] if summary else ""
        })
