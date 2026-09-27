Write-Host "Running 100 VU pre-release runner..."
uv run python scripts/100_vu_runner.py

Write-Host "Running forward compatibility check..."
bash scripts/verify_forward_compatibility.sh

Write-Host "Running Pytest load gates..."
uv run pytest packages/evaluation/tests/test_load_gates.py
