#!/bin/bash
# Submission script for Lyra

#SBATCH --job-name=testlinger_baseline
#SBATCH --time=00:45:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --partition=batch   

#SBATCH --output=logs/%j_%x.out
#SBATCH --error=logs/%j_%x.err

# -------------------------
# Settings
# -------------------------

CONTAINER="images/linger.sif"

SCRIPT="code/testlinger.py"
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
    --bind $HOST_PATH:$CONTAINER_PATH \
    "$CONTAINER" bash -c " 
    python $SCRIPT
"

echo ""
echo "[JOB END] $(date)"
