#!/bin/bash
# Submission script for Lyra

#SBATCH --job-name=lingerv1.106
#SBATCH --time=9:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem=128G
#SBATCH --partition=batch

#SBATCH --exclusive

#SBATCH --output=logs/%j_%x.out
#SBATCH --error=logs/%j_%x.err

#SBATCH --mail-user=emile.vangysel@student.uclouvain.be
#SBATCH --mail-type=ALL

# -------------------------
# Settings
# -------------------------

CONTAINER="images/linger.sif"

SCRIPT="code/linger.py"
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
echo "Script : $SCRIPT"

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
