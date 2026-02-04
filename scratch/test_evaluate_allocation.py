import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.compensation import evaluate_allocation

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

result = evaluate_allocation(allocation, available_stems)

print("Evaluation:")
for k, v in result.items():
    print(f"{k}: {v}")
