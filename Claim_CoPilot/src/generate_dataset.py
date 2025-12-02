import json
import random
import datetime
from pathlib import Path

# --------------------------------------------------------------------
# Project paths (relative to this file)
# --------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUT_PATH = DATA_DIR / "claims.jsonl"

# --------------------------------------------------------------------
# Synthetic data templates
# --------------------------------------------------------------------
random.seed(42)

FIRST_NAMES = [
    "John", "Jane", "Mark", "Priya", "Carlos", "Emily",
    "Ravi", "Anita", "Michael", "Sara", "David", "Liu",
]

LAST_NAMES = [
    "Doe", "Smith", "Lee", "Nair", "Rivera", "Chen",
    "Patel", "Khan", "Johnson", "Brown", "Garcia", "Nguyen",
]

POLICY_TYPES = ["Health", "Auto", "Property"]

HEALTH_EVENTS = [
    "a slip and fall at home",
    "a workplace accident",
    "a sports injury during a local match",
    "a minor surgery following a chronic condition",
    "an emergency room visit after chest pain",
]

HEALTH_INJURIES = [
    "no complications were reported",
    "the patient suffered a minor sprain",
    "the patient sustained a fracture",
    "follow-up physiotherapy sessions were recommended",
    "the patient required an overnight hospital stay",
]

AUTO_EVENTS = [
    "a rear-end collision at a traffic light",
    "a side-impact accident at an intersection",
    "a low-speed parking lot collision",
    "a highway collision involving multiple vehicles",
    "a single-vehicle skid on a wet road",
]

AUTO_INJURIES = [
    "no injuries were reported",
    "the driver reported mild whiplash",
    "the passenger reported minor bruising",
    "no occupants were harmed",
]

PROPERTY_EVENTS = [
    "water damage from a burst pipe",
    "fire damage in the kitchen area",
    "storm damage to the roof and windows",
    "theft resulting in loss of electronics",
    "flooding in the basement after heavy rain",
]

PROPERTY_NOTES = [
    "no injuries occurred",
    "no occupants were present at the time",
    "the tenant was not at home when the incident happened",
]

BASE_DATE = datetime.date(2024, 1, 1)


def random_date() -> str:
    """Sample a random date in 2024 (YYYY-MM-DD)."""
    delta_days = random.randint(0, 365)
    d = BASE_DATE + datetime.timedelta(days=delta_days)
    return d.isoformat()


def generate_single_claim(i: int) -> dict:
    """
    Generate one synthetic claim record with fields aligned
    to what the pipeline expects.
    """
    claim_id = f"c{i:05d}"
    policy_type = random.choice(POLICY_TYPES)
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    incident_date = random_date()

    if policy_type == "Health":
        event = random.choice(HEALTH_EVENTS)
        injury = random.choice(HEALTH_INJURIES)
        base_amt = random.randint(600, 9000)
    elif policy_type == "Auto":
        event = random.choice(AUTO_EVENTS)
        injury = random.choice(AUTO_INJURIES)
        base_amt = random.randint(800, 15000)
    else:  # Property
        event = random.choice(PROPERTY_EVENTS)
        injury = random.choice(PROPERTY_NOTES)
        base_amt = random.randint(1000, 20000)

    severity = random.choice(["low", "medium", "high"])
    multiplier = {"low": 0.6, "medium": 1.0, "high": 1.6}[severity]
    claim_amount = round(base_amt * multiplier, 2)

    # Priority logic aligned with TriageAgent
    if "fracture" in injury or "surgery" in injury or severity == "high" or claim_amount > 5000:
        priority = "High"
    elif claim_amount >= 3000:
        priority = "Medium"
    else:
        priority = "Low"

    text = (
        f"{name} submitted a {policy_type} claim on {incident_date} after {event}. "
        f"The estimated cost is ${claim_amount:.2f}. {injury.capitalize()}."
    )

    gold_summary = (
        f"{name} filed a {priority.lower()}-priority {policy_type.lower()} claim on "
        f"{incident_date} after {event}, with an estimated cost of ${claim_amount:.2f} "
        f"and {injury}."
    )

    return {
        "id": claim_id,
        "text": text,
        "claimant_name": name,
        "policy_type": policy_type,
        "claim_amount": claim_amount,
        "incident_date": incident_date,
        "priority": priority,
        "gold_summary": gold_summary,
    }


def main(n_total: int = 10000):
    print(f"Generating {n_total} synthetic claims...")
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for i in range(1, n_total + 1):
            rec = generate_single_claim(i)
            f.write(json.dumps(rec) + "\n")
    print(f"Wrote dataset to: {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
