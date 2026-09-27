from pathlib import Path

import pytest
import yaml  # type: ignore
from evaluation.harness.tutor_harness import TutorEvaluationHarness
from evaluation.models.eval_case import EvalCase

DATASETS_DIR = Path(__file__).parent.parent / "datasets" / "tutor"

def load_cases() -> list[EvalCase]:
    cases: list[EvalCase] = []
    if not DATASETS_DIR.exists():
        return cases
        
    for yaml_file in DATASETS_DIR.glob("*.yaml"):
        with yaml_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                cases.extend(EvalCase(**case_dict) for case_dict in data)
    return cases

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c.id)
async def test_tutor_evaluation_case(case: EvalCase) -> None:
    harness = TutorEvaluationHarness()
    await harness.evaluate(case)

