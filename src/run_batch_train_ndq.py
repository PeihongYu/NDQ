import subprocess
import os
from itertools import product
from types import SimpleNamespace as SN


# Define the maximum number of jobs for each account
# max_job_nums = [4, 2, 2, 8]
max_job_nums = [4, 2]
account_combinations = [
    ["nexus", "tron", "medium"],      # 2 days, for qmix, 4 jobs max
    ["cml-tokekar", "cml-dpart", "cml-medium"],     # 3 days, for ippo/dm2, 2 jobs max
    # ["cml-tokekar", "cml-dpart", "cml-high"],     # 1.5 days, for qmix, 2 jobs max
    # ["cml-tokekar", "cml-dpart", "cml-high_long"],    # 14 days, for ippo/dm2, 8 jobs max, but actually 2 jobs max due to resources
]

# Define the parameters you want to iterate over
# for smac
# parameters = {
#     "algo_name": ["ndq", "tarmac"],
#     "env_name": ["sc2", "sc2_hard"],
#     "map_name": ['3s_vs_5z', 'bane_vs_hM', '1o_10b_vs_1r'],
#     "seed": [112358, 1285842, 78590, 119527, 122529],
# }

# for smacv2
parameters = {
    "algo_name": ["ndq", "tarmac"],
    "map_name": ["sc2_gen_terran"], #"sc2_gen_zerg", "sc2_gen_protoss", "sc2_gen_terran", "sc2_gen_protoss_epo", "sc2_gen_terran_epo", "sc2_gen_zerg_epo"],
    "sight_range": [0.2, 1, 5],
    "agent_num": [5, 10, 20],
    "seed": [112358] #, 1285842, 78590, 119527, 122529],
}

root_dir = "/fs/nexus-projects/Guided_MARL/smacv2_masia_ndq"
smac_dir = "/fs/nexus-scratch/peihong/3rdparty/StarCraftII_2410"
os.makedirs(f'{root_dir}/slurm_scripts', exist_ok=True)
os.makedirs(f'{root_dir}/slurm_logs', exist_ok=True)

param_names = list(parameters.keys())
param_values = [v for v in parameters.values()]
combinations = list(product(*param_values))


# Iterate over parameter combinations
jobs_num = 0
for combo in combinations:
    param_dict = {key: value for key, value in zip(param_names, combo)}
    param = SN(**param_dict)

    # for smac
    # job_name = f"{param.algo_name}__{param.map_name}__seed_{param.seed}"
    # python_command = f"python src/main.py --config={param.algo_name} --env-config={param.env_name} with env_args.map_name={param.map_name} t_max=10050000 seed={param.seed}"

    # for smacv2
    job_name = f"{param.algo_name}__{param.map_name}__seed_{param.seed}_sr{param.sight_range}_{param.agent_num}_vs_{param.agent_num}"
    python_command = f"python src/main.py --config={param.algo_name} --env-config={param.map_name} with env_args.sight_range_ratio={param.sight_range} env_args.capability_config.n_units={param.agent_num} env_args.capability_config.n_enemies={param.agent_num} t_max=10050000 seed={param.seed}"

    print("----------")
    print(job_name)
    print(python_command)

    # get qos info
    remainder = jobs_num % sum(max_job_nums)
    for j, val in enumerate(max_job_nums):
        if remainder < sum(max_job_nums[:j+1]):
            account, partition, qos = account_combinations[j]
            print(f"job num: {jobs_num}, account: {account}, partition: {partition}, qos: {qos}")
            break
    jobs_num += 1

    # Create a unique job script for each combination 
    # note: change time accordingly
    job_script_content = f'''#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={root_dir}/slurm_logs/%x.%j.out
#SBATCH --time=36:00:00
#SBATCH --account={account}
#SBATCH --partition={partition}
#SBATCH --qos={qos}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:1

# Load any necessary modules
# For example, if you need Python, you might load a Python module
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda activate marl
export SC2PATH={smac_dir}

# Your Python script with parameters
srun bash -c "{python_command}"
''' 

    # Write the job script to a file
    job_script_path = f'{root_dir}/slurm_scripts/submit_job__{job_name}.sh'
    with open(job_script_path, 'w') as job_script_file:
        job_script_file.write(job_script_content)

    # Submit the job using sbatch
    subprocess.run(['sbatch', job_script_path])

    # Print the job submission info
    result = ", ".join([f"{name}: {value}" for name, value in zip(param_names, combo)])
    print(f'Job submitted for parameters: {result}')
