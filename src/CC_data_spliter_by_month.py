"""
This python script can be used to split input files by month before submitting parallel jobs to Slurm
"""

import pandas as pd

data = pd.read_csv("PATH_TO_FILE.csv")

# convert to datetime and extract the month
data['month'] = pd.DatetimeIndex(data['date']).month

# split and write files per month
for month in data['month'].unique():
    data[data['month']==month].to_csv("/projects/p31516/mah3870/climate_change_project/Contrarian Claims/ICA_Submission/data/v2/split_files/NW_CC_2021_month_{}_lowcred_v2.csv".format(m),index=False)    
    
