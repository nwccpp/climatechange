#!/bin/bash
#SBATCH -A p31516
#SBATCH -p xlong
#SBATCH -N 1
#SBATCH -t 503:30:00
#SBATCH --mem=5G
#SBATCH --ntasks-per-node=1
#SBATCH --mail-user=EMAIL@u.northwestern.edu
#SBATCH --mail-type=ALL
#SBATCH --output=2017_cc_log.log

# unload any modules that carried over from your command line session
module purge all

module load python/anaconda3.6
source activate my-virtenv-py38
python /projects/p31516/mah3870/climate_change_project/Contrarian\ Claims/ICA_Submission/scripts/2017_cc_script.py
