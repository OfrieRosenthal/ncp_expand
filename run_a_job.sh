#!/bin/bash
# run with the command: sbatch run_a_job.sh

## SBATCH -A ash                                   # Account
## SBATCH -p ash                                   # Partition
#SBATCH --job-name=exp                           # Job name
#SBATCH -o ./terminal_runs/%A/out_job_%a.txt       # stdout file with job ID (%A) and task ID (%a)
#SBATCH -e ./terminal_runs/%A/err_job_%a.txt       # stderr file with job ID (%A) and task ID (%a)
#SBATCH --array=0-0                                # Array range for 9 jobs (0 to 8)
#SBATCH --ntasks=1                               # One task per job
#SBATCH --gres=gpu:A40:2                             # Num GPUs per job
#SBATCH --cpus-per-task=16                       # Number of CPU cores per task

## module purge                                      # Clean active modules list

# Load Conda properly (don't use `conda init` inside the script)
# source ~/anaconda3/bin/activate w25_adv           # Adjust the path to your Conda installation
source ~/miniconda3/etc/profile.d/conda.sh
conda activate spv_attack311

# Ensure output directory exists
mkdir -p ./terminal_runs/${SLURM_ARRAY_JOB_ID}

# Get number of GPUs allocated by SLURM
NUM_GPUS=${SLURM_GPUS_ON_NODE:-1}

UNIQUE_PORT=$((29500 + ${SLURM_ARRAY_JOB_ID:-0} % 1000))

# Define the base command
# make sure not to add space between the 'BASE_CMD=' and the command

# BASE_CMD="python /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/ANeurIPS2024_SPV-MIA_not_official/pipeline_attack.py"


BASE_CMD="accelerate launch \
    --num_processes=${NUM_GPUS} \
    --mixed_precision=fp16 \
    --main_process_port=${UNIQUE_PORT} \
    /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/ANeurIPS2024_SPV-MIA_not_official/pipeline_attack.py"

# "ipython /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/ANeurIPS2024_SPV-MIA_not_official/pipeline_colab.ipynb"
#"ipython /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/ANeurIPS2024_SPV-MIA_not_official/gpt2_wikitext_mia_colab.ipynb"
# "/home/liranc6/miniconda3/envs/w25_adv/bin/python /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/src/MIA_run.py"
# "/home/liranc6/miniconda3/envs/w25_adv/bin/python /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/neighbour-mia/attack.py"
# "/home/liranc6/miniconda3/envs/w25_adv/bin/python /home/liranc6/W25/adversarial-attacks-on-deep-learning/project/src/MIA_run.py"

# Define the array of flag sets
FLAG_SETS=(
    ""
    # Add actual flag sets here if needed
)

# Select the flag set for this job
FLAGS="${FLAG_SETS[${SLURM_ARRAY_TASK_ID}]}"

# Run the command with the selected flags
eval "$BASE_CMD $FLAGS"