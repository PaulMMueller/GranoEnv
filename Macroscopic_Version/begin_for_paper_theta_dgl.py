#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 13:06:51 2020

@author: paul
"""
import os
import numpy as np
import subprocess

def write_submit_file(file_name,dir_name,command):
    '''Create the submit file for the cluster from a template.'''
    new_sub_file_str = ''

    with open('/home/pmueller/Masterarbeit/Paper_Data/input/submit_template.sh') as sub_file:
        
        for line in sub_file:
            if 'job-name' in line:
                line = f'#SBATCH --job-name={save_name}\n'
            if 'output' in line:
                line = f'#SBATCH --output={os.path.join(dir_name,file_name)}.out\n'
            if 'error' in line:
                line = f'#SBATCH --error={os.path.join(dir_name,file_name)}.err\n'
            if 'workdir' in line:
                line =  f'#SBATCH --workdir={dir_name}\n'
                
            new_sub_file_str+=line
            
        new_sub_file_str+=command
    with open(os.path.join(dir_name,'submit_dgl.sh'),'w') as sub_file:
        sub_file.write(new_sub_file_str)

calculate = True
force_run = False
dir_name = '/home/pmueller/Masterarbeit/Paper_Data/output'


###Same in the analytical version
#Thresholds
pollution_threshold  = .6
social_threshold = .4

vulnerability = 1e-1 
farsightness = 1e1
time_horizon = 1e6
tau = 1e0

rand_file  = '/home/pmueller/Masterarbeit/Paper_Data/input/ini_pairs_21x21.npy'#random_pairs_1000.npy'
rands = np.load(rand_file)
number_of_random_pairs = len(rands)#  Has to be checked if correct file is linked

#Time evolution properties
#time_scaler = 1.0
delta_t = 1e-4#/time_scaler#/number_of_nodes
integration_time = 20

save_name = 'dgl_paper_theta_21x21'#'Ana_test_N__th_1000'#'test'#'network_size'
####



varying_param = np.logspace(0,6,7)#np.linspace(5,100,20)
approx_calc_length = 1
j = 1
for v in varying_param:
    
    time_horizon = v
    chuncks = 1 + (approx_calc_length*number_of_random_pairs)//(3600*10) # Every chunck should run about 2 hours

    start_end_ini = []
    for i in range(0,chuncks):  # Make an array of how many blocks of codes should be submitted and what they should have in them
        start_end_ini.append(int(np.round(i*number_of_random_pairs/chuncks,0)))
    start_end_ini.append(number_of_random_pairs)

    for i in range(len(start_end_ini)-1):

        command = 'srun -n 1 '
        command += f'~/Masterarbeit/GranoEnv/Macroscopic_Version/cluster_multiple_from_rand_dgl.py '
        command += (
               f'{pollution_threshold} '+
               f'{social_threshold} '+ 
               f'{vulnerability} '+
               f'{farsightness} '+ 
               f'{time_horizon} '+
               f'{tau} ' +
               f'{delta_t} '+ 
               f'{integration_time} '+
               f'{start_end_ini[i]} ' +
               f'{start_end_ini[i+1]} '+
               f'{save_name} '+ 
               f'{rand_file} ')       

        file_name = ( f'DGL_TG'+
                   f'_pt{pollution_threshold}'+
                   f'_st{social_threshold}'+
                   f'_v{vulnerability}'+ 
                   f'_f{farsightness}'+
                   f'_th{time_horizon}'+
                   f'_tau{tau}'+
                   f'_dt{delta_t}'+
                   f'_it{integration_time}'+
                   f'_fromIni{start_end_ini[i]}'+
                   f'_toIni{start_end_ini[i+1]}'+
                   f'_{save_name}')

        print(f'Writing submit file for: {os.path.join(dir_name,file_name)}.out') 
        write_submit_file(file_name,dir_name,command)
        if calculate:

            print(f'Starting calculation number: {j}\n')
            os.chdir(dir_name)
            p = p = subprocess.Popen(['sbatch', 'submit_dgl.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            
            j +=1

