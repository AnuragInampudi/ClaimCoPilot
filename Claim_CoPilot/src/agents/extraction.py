import re
from typing import List, Tuple, Optional, Dict, Any

from transformers import pipeline, Pipeline
from .base import BaseAgent
from state import ClaimState

# ---------------- Date & Amount Helpers ----------------

MONTH_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def extract_incident_date(text: str) -> Optional[str]:
    """
    Return incident date as 'YYYY-MM-DD' if we can find one, else None.

    Supports:
      - ISO dates: 2024-06-05
      - Natural dates: November 22, 2024  ->  2024-11-22
    """

    # 1) ISO-style dates like 2024-06-05
    m_iso = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if m_iso:
        return m_iso.group(1)

    # 2) Long-form dates like 'November 22, 2024'
    m_long = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s*(\d{4})",
        text,
    )
    if m_long:
        month_name = m_long.group(1).lower()
        day = int(m_long.group(2))
        year = int(m_long.group(3))
        month_num = MONTH_MAP.get(month_name)
        if month_num:
            return f"{year:04d}-{month_num:02d}-{day:02d}"

    # Nothing found
    return None


def extract_claim_amount(text: str) -> Optional[float]:
    """
    Extract the main monetary amount from the claim text.

    Strategy:
      - Only consider numbers prefixed with '$' to avoid confusing years (e.g., 2024).
      - Remove commas and parse as float.
      - If multiple amounts exist (repairs + medical), pick the largest
        as the main claim amount.
    """
    # Capture things like $3,750 or $280 or $1200.50
    matches = re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", text)
    if not matches:
        return None

    amounts: List[float] = []
    for m in matches:
        cleaned = m.replace(",", "")
        try:
            amounts.append(float(cleaned))
        except ValueError:
            continue

    if not amounts:
        return None

    # Heuristic: main claim amount = largest value
    return max(amounts)


class ExtractionAgent(BaseAgent):
    name = "ExtractionAgent"
    _ner: Optional[Pipeline] = None  # shared NER pipeline

    def _get_ner(self) -> Optional[Pipeline]:
        """
        Lazily create the NER pipeline the first time it's needed.
        If something goes wrong, return None instead of crashing.
        """
        if self._ner is not None:
            return self._ner
        try:
            self._ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
            )
        except Exception as e:
            # Fallback: no NER, just regex-based extraction
            print("[ExtractionAgent] Warning: could not load NER model:", e)
            self._ner = None
        return self._ner

    def run(self, state: ClaimState) -> None:
        """
        Extract basic fields (claimant_name, policy_type, claim_amount, incident_date)
        from the first raw text using NER + regex (with graceful fallback).
        """
        text = state.raw_texts[0] if state.raw_texts else ""
        text_stripped = text.strip()
        entities: List[Tuple[str, str]] = []

        # ---------------- NER extraction ----------------
        ner = self._get_ner()
        if ner is not None and text_stripped:
            try:
                ents = ner(text)
                # ents elements look like: {"word": "...", "entity_group": "PER", ...}
                entities = [(e["word"], e["entity_group"]) for e in ents]
            except Exception as e:
                print("[ExtractionAgent] Warning during NER:", e)

        # ---------------- Policy type from keywords ----------------
        policy: Optional[str] = None
        lowered = text.lower()
        for p in ["Health", "Auto", "Property"]:
            if p.lower() in lowered:
                policy = p
                break

        # ---------------- Claimant name from PERSON NER ----------------
        claimant_name: Optional[str] = None
        for word, label in entities:
            if label == "PER":
                # With aggregation_strategy="simple", this is usually full name
                claimant_name = word
                break

        # ---------------- Amount & date using helper functions ----------------
        claim_amount = extract_claim_amount(text)
        incident_date = extract_incident_date(text)

        # ---------------- Update state.extracted_fields ----------------
        if claimant_name:
            state.extracted_fields["claimant_name"] = claimant_name
        if policy:
            state.extracted_fields["policy_type"] = policy
        if claim_amount is not None:
            state.extracted_fields["claim_amount"] = claim_amount
        if incident_date is not None:
            state.extracted_fields["incident_date"] = incident_date

        # ---------------- Trace logging ----------------
        trace_payload: Dict[str, Any] = {
            "entities": entities,
            "policy_guess": policy,
            "claimant_name": claimant_name,
            "claim_amount": claim_amount,
            "incident_date": incident_date,
        }

        state.add_trace(self.name, "extract_fields", trace_payload)
