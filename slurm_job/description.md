In order to submit a job on slurm, please follow the instructions:

1. Update the path of the `.sh` script to point to your `.py` script. 
2. Submit job by typing `sbatch NAME_OF_FILE.sh`. This will create a job ID which you can use to
track the status of your job. To check for the status of a job just type `checkjob JOB_ID`.
