#!/bin/bash
#SBATCH -A p31516
#SBATCH -p xlong
#SBATCH -N 1
#SBATCH -t 503:30:00
#SBATCH --mem=5G
#SBATCH --ntasks-per-node=1
#SBATCH --mail-user=EMAIL@u.northwestern.edu
#SBATCH --mail-type=ALL
#SBATCH --output=2020_cc_log_%A_%a.log
#SBATCH --array=1-12

# unload any modules that carried over from your command line session
module purge all
module load python/anaconda3.6
module load python-miniconda3
source activate my-virtenv-py38 

# Define an array of input files
input_files=("NW_CC_2020_month_12_lowcred_v2.csv" 
             "NW_CC_2020_month_11_lowcred_v2.csv" 
             "NW_CC_2020_month_10_lowcred_v2.csv" 
             "NW_CC_2020_month_9_lowcred_v2.csv" 
             "NW_CC_2020_month_8_lowcred_v2.csv" 
             "NW_CC_2020_month_7_lowcred_v2.csv" 
             "NW_CC_2020_month_6_lowcred_v2.csv" 
             "NW_CC_2020_month_5_lowcred_v2.csv" 
             "NW_CC_2020_month_4_lowcred_v2.csv" 
             "NW_CC_2020_month_3_lowcred_v2.csv" 
             "NW_CC_2020_month_2_lowcred_v2.csv" 
             "NW_CC_2020_month_1_lowcred_v2.csv")

# Get the current input file based on the job index
current_file="${input_files[$SLURM_ARRAY_TASK_ID - 1]}"

# Run the Python script on the current input file
~/.conda/envs/my-virtenv-py38/bin/python  /projects/p31516/mah3870/climate_change_project/Contrarian\ Claims/ICA_Submission/scripts/2020_parallel_job.py "$current_file"

