#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-/mnt/h/cuhk-2025fALL/6013RP-wyf}"
ENV_NAME="${PHASE17_ENV_NAME:-sle-bcell-v7}"
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find_conda() {
  if command -v conda >/dev/null 2>&1; then
    return 0
  fi
  for candidate in \
    "$HOME/miniforge3/etc/profile.d/conda.sh" \
    "$HOME/mambaforge/etc/profile.d/conda.sh" \
    "$HOME/miniconda3/etc/profile.d/conda.sh" \
    "$HOME/anaconda3/etc/profile.d/conda.sh"
  do
    if [[ -f "$candidate" ]]; then
      # shellcheck disable=SC1090
      source "$candidate"
      return 0
    fi
  done
  return 1
}

if ! find_conda; then
  echo "[ERROR] conda was not found in WSL."
  echo "Install Miniforge or activate the existing conda installation."
  exit 3
fi

if ! conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  echo "[ERROR] Conda environment '$ENV_NAME' does not exist."
  echo "Create it first:"
  echo "  conda env create -f '$TOOL_DIR/environment_phase17_v7.yml'"
  exit 4
fi

GATEC1_ROOT="$PROJECT_ROOT/phase17_v7/gateC1"
GATEC1_DIR="$(find "$GATEC1_ROOT" -maxdepth 1 -type d -name '*_hotfix_v1_1' | sort | tail -n 1)"
if [[ -z "$GATEC1_DIR" ]]; then
  echo "[ERROR] No Gate C1 hotfix directory found under $GATEC1_ROOT"
  exit 5
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="$PROJECT_ROOT/phase17_v7/gateC2A/${STAMP}_smoke"
mkdir -p "$OUTPUT_DIR"

echo "[INFO] Project : $PROJECT_ROOT"
echo "[INFO] Gate C1 : $GATEC1_DIR"
echo "[INFO] Output  : $OUTPUT_DIR"
echo "[INFO] Env     : $ENV_NAME"

conda run -n "$ENV_NAME" python "$TOOL_DIR/phase17_c2a_01_prepare_smoke.py" \
  --project-root "$PROJECT_ROOT" \
  --gatec1-dir "$GATEC1_DIR" \
  --output-dir "$OUTPUT_DIR" \
  --target-cells 20000

conda run -n "$ENV_NAME" python "$TOOL_DIR/phase17_c2a_02_smoke_recluster.py" \
  --input-h5ad "$OUTPUT_DIR/05_smoke_raw_counts.h5ad" \
  --output-dir "$OUTPUT_DIR" \
  --n-hvg 3000

cat > "$OUTPUT_DIR/WORKFLOW_GATE_C2A.md" <<EOF
# Gate C2A smoke workflow

- Time: $(date --iso-8601=seconds)
- Project: \`$PROJECT_ROOT\`
- Gate C1: \`$GATEC1_DIR\`
- Output: \`$OUTPUT_DIR\`
- Environment: \`$ENV_NAME\`
- Target cells: 20,000
- Disease-blind: true

No source H5AD was modified.
EOF

printf 'run_dir=%s\n' "$OUTPUT_DIR" > "$PROJECT_ROOT/phase17_v7/gateC2A/_LATEST_GATE_C2A.txt"
echo "[SUCCESS] Gate C2A completed: $OUTPUT_DIR"
