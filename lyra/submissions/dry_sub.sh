#!/bin/bash
# Submission script for Lyra

#SBATCH --job-name=dryRun
#SBATCH --time=00:01:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --partition=batch

#SBATCH --gres="gpu:0"

#SBATCH --output=logs/%j_%x.out
#SBATCH --error=logs/%j_%x.err

# -------------------------
# Settings
# -------------------------

CONTAINER="images/linger_v2.sif"
CONDA_ENV="LINGER"

SCRIPT="code/dry_run.py"
HOST_PATH="/globalsc/ucl/inma/vangysel/Linger"
CONTAINER_PATH="/project"

# -------------------------
# Prepare logs
# -------------------------

mkdir -p logs
#rm -rf logs/*

echo "[JOB START] $(date)"
echo "Running on: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"

# -------------------------
# Run inside container
# -------------------------

srun apptainer exec \
    --nv \
    --bind $HOST_PATH:$CONTAINER_PATH \
    "$CONTAINER" bash -c "

    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate $CONDA_ENV || exit 1

    echo \"Conda env : \$CONDA_DEFAULT_ENV\"

    nvidia-smi >/dev/null 2>&1

    # Run script
    python $SCRIPT
"

echo ""
echo "[JOB END] $(date)"
