In order to submit a job on slurm, please follow the instructions:

1. Split your datafiles per month using `src/CC_data_spliter_by_month.py`
2. Update the path of the `.sh` script to point to your `.py` script. 
3. Submit job by typing `sbatch NAME_OF_FILE.sh`. This will create a job ID which you can use to
track the status of your job. To check for the status of a job just type `checkjob JOB_ID`.
