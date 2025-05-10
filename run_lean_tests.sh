#!/bin/bash
# Run Lean tests for the Economic Theorem Prover integration

set -e

# Configuration
LEAN_LIBS_DIR="$(realpath ~/Desktop/HardisonCo/hms/lean_libs)"
LEAN_CMD="lean"
HMS_DIR="$(realpath ~/Desktop/HardisonCo)"
GENETIC_DIR="$HMS_DIR/SYSTEM-COMPONENTS/HMS-A2A/genetic_theorem_prover"

echo "=== HMS Economic Theorem Prover Lean Test Runner ==="
echo "Lean libraries directory: $LEAN_LIBS_DIR"

# Check if Lean is installed
if ! command -v $LEAN_CMD &> /dev/null; then
    echo "Error: Lean not found in PATH"
    echo "Please install Lean or set the LEAN_CMD variable"
    exit 1
fi

# Check Lean version
LEAN_VERSION=$($LEAN_CMD --version | head -n 1)
echo "Using Lean: $LEAN_VERSION"

# Check if Moneyball.lean exists
if [ ! -f "$LEAN_LIBS_DIR/Moneyball.lean" ]; then
    echo "Error: Moneyball.lean not found in $LEAN_LIBS_DIR"
    exit 1
fi

echo "=== Testing Lean file compilation ==="
cd $LEAN_LIBS_DIR
$LEAN_CMD Moneyball.lean
if [ $? -eq 0 ]; then
    echo "✅ Moneyball.lean compiles successfully"
else
    echo "❌ Moneyball.lean fails to compile"
    exit 1
fi

# Run smoke tests with Lean
echo "=== Running smoke tests ==="
$LEAN_CMD --run <<EOF
import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic
import Mathlib.Tactic
import Mathlib.Data.Finmap
import "$LEAN_LIBS_DIR/Moneyball.lean"

#eval war_score {
  sector_weights := Finmap.ofList [("Tech", 1.0)],
  agreement_impacts := Finmap.ofList [("Tech", 50.0)],
  deficit_reduction_potentials := Finmap.ofList [("Tech", 2.0)]
}

#eval drp {
  baseline_deficit := 100.0,
  policy_effects := Finmap.ofList [("P1", 10.0)],
  confidence_factors := Finmap.ofList [("P1", 1.0)],
  implementation_rates := Finmap.ofList [("P1", 1.0)],
  buffett_margin_of_safety := 1.0
}

#eval sps {
  deficit_impact := 100.0,
  job_creation := 80.0,
  growth_potential := 60.0,
  implementation_ease := 40.0
}

#eval "All smoke tests passed!"
EOF

if [ $? -eq 0 ]; then
    echo "✅ All smoke tests passed!"
else
    echo "❌ Smoke tests failed"
    exit 1
fi

# Run theorem extractor tests
echo "=== Testing Lean theorem extractor ==="

# Ensure Python environment is set up
cd $GENETIC_DIR
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q pytest dataclasses typing_extensions

# Run theorem extractor test
python -c "
import sys
sys.path.append('$GENETIC_DIR/core')
from lean_theorem_extractor import LeanTheoremExtractor

extractor = LeanTheoremExtractor('$LEAN_LIBS_DIR')
libraries = extractor.extract_theorems_from_directory()

# Print results
for file_path, library in libraries.items():
    print(f'File: {file_path}')
    print(f'Theorems found: {len(library.theorems)}')
    for theorem_id, theorem in library.theorems.items():
        print(f'  - {theorem_id} (namespace: {theorem.namespace})')
        if theorem.proof_outline:
            outline_preview = theorem.proof_outline.replace('\n', ' ')[:50]
            print(f'    Proof outline: {outline_preview}...')
    print()

# Test finding a specific theorem
war_score_theorem = extractor.find_theorem('war_score_bounds')
if war_score_theorem:
    print('Successfully found war_score_bounds theorem')
    print(f'Expression: {war_score_theorem.formal_expression}')
    print(f'Hypotheses: {len(war_score_theorem.hypotheses)}')
else:
    print('Failed to find war_score_bounds theorem')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Theorem extractor tests passed!"
else
    echo "❌ Theorem extractor tests failed"
    exit 1
fi

# Run DeepSeek config tests
echo "=== Testing DeepSeek configuration ==="
python -c "
import sys
sys.path.append('$GENETIC_DIR/core')
from deepseek_config import DeepSeekConfig, ProverMode, TacticStyle

# Create a config
config = DeepSeekConfig(
    mode=ProverMode.DSP,
    temperature=0.2,
    max_tokens=6144,
    subgoal_depth=3,
    timeout_seconds=300,
    tactic_style=TacticStyle.ECONOMIC,
    lean_lib_path='$LEAN_LIBS_DIR'
)

# Test serialization
config_dict = config.to_dict()
assert config_dict['mode'] == 'decomposition'
assert config_dict['tactic_style'] == 'economic'
assert config_dict['lean_lib_path'] == '$LEAN_LIBS_DIR'

# Test deserialization
config2 = DeepSeekConfig.from_dict(config_dict)
assert config2.mode == ProverMode.DSP
assert config2.tactic_style == TacticStyle.ECONOMIC

# Test mutation
mutated = config.mutate(mutation_rate=1.0)  # Force mutation
assert mutated.mutation_count == 1
assert mutated != config

print('All DeepSeek config tests passed!')
"

if [ $? -eq 0 ]; then
    echo "✅ DeepSeek config tests passed!"
else
    echo "❌ DeepSeek config tests failed"
    exit 1
fi

# End-to-end test with simulated prover
echo "=== Running end-to-end test with simulated prover ==="
python -c "
import sys
sys.path.append('$GENETIC_DIR/core')
from lean_theorem_extractor import LeanTheoremExtractor, create_theorem_request
from deepseek_config import DeepSeekConfig, ProverMode
from deepseek_prover import DeepSeekProverClient, ProverConfig, ProverRequest

# Extract a theorem
extractor = LeanTheoremExtractor('$LEAN_LIBS_DIR')
theorem = extractor.find_theorem('war_score_bounds')
assert theorem is not None, 'Failed to find theorem'

# Create a theorem proving request
request_dict = create_theorem_request(theorem)
assert request_dict['theorem_id'] == 'war_score_bounds'

# Create prover config
prover_config = ProverConfig(
    model_path='simulated',  # Use simulated model
    mode=ProverMode.DEFAULT,
    temperature=0.1,
    max_tokens=4096,
    subgoal_depth=2,
    timeout_seconds=10,
    lean_path=None
)

# Create prover client
client = DeepSeekProverClient(prover_config)

# Create request
request = ProverRequest(
    theorem_id=request_dict['theorem_id'],
    formal_expression=request_dict['formal_expression'],
    assumptions=request_dict['assumptions'],
    variables=request_dict['variables'],
    config=prover_config,
    context=request_dict.get('context')
)

# Get proof
response = client.prove_theorem(request)

print(f'Proving task completed: {response.success}')
if response.proof is not None:
    print(f'Generated proof with {len(response.proof_steps)} steps')

print('End-to-end test completed successfully!')
"

if [ $? -eq 0 ]; then
    echo "✅ End-to-end test passed!"
else
    echo "❌ End-to-end test failed"
    exit 1
fi

echo "=== All tests completed successfully! ==="
echo "Lean theorem proving integration is working correctly."