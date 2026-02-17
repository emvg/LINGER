#!/bin/bash
# Submission script for Dragon2

#SBATCH --job-name=Linger_img_v3
#SBATCH --time=9:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem=128G
#SBATCH --partition=batch

#SBATCH --output=logs/%j_%x.out
#SBATCH --error=logs/%j_%x.err

#SBATCH --mail-user=emile.vangysel@student.uclouvain.be
#SBATCH --mail-type=ALL

# -------------------------
# Settings
# -------------------------

CONTAINER="images/linger_v3.sif"
CONDA_ENV="LINGER"

SCRIPT="code/linger.py"
HOST_PATH="/globalscratch/vangysel/Linger"
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


srun singularity exec \
    --nv \
    --bind $HOST_PATH:$CONTAINER_PATH \
    "$CONTAINER" bash -c "

    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate $CONDA_ENV || exit 1

    echo \"Conda env : \$CONDA_DEFAULT_ENV\"

    # Run script
    python $SCRIPT
"

echo ""
echo "[JOB END] $(date)"

#     echo "GPU : $(nvidia-smi --query-gpu=name --format=csv,noheader)"
