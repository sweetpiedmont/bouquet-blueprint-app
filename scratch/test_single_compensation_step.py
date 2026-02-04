import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.compensation import apply_compensation

allocation = {
    "Focal": 3,
    "Foundation": 3,
    "Filler": 0,
    "Floater": 2,
    "Finisher": 1,
    "Foliage": 2,
}

available_stems = {
    "Focal": 30,
    "Foundation": 100,
    "Filler": 0,
    "Floater": 20,
    "Finisher": 50,
    "Foliage": 10,
}

stem_bounds = {
    "Focal": {"absolute_min": 2},
    "Foundation": {"absolute_min": 3},
    "Filler": {"absolute_min": 0},
    "Floater": {"absolute_min": 0},
    "Finisher": {"absolute_min": 0},
    "Foliage": {"absolute_min": 0},
}

COMPENSATION_RULES = {}  # not used yet

result = apply_compensation(
    allocation=allocation,
    available_stems=available_stems,
    stem_bounds=stem_bounds,
    compensation_rules=COMPENSATION_RULES,
)

print("New allocation:", result["allocation"])
print("Evaluation:", result["evaluation"])
