#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 12:02:17 2020

@author: paul
"""
import subprocess
import sys
import timeit 
import numpy as np
import os

start = timeit.default_timer()

def check_for_endend_calc(file):
    ''' Check if file has the ===CalculationEndedFlag===
    Watchout this is a work around only for Linux systems
    '''
    if not os.path.isfile(file):
        return False
    line = subprocess.check_output(['tail', '-2', file])
    if '===CalculationEnded===' in str(line):
        return True
    else:
        return False

calculate = True
force_run = False
input_parameters = sys.argv

#Thresholds
pollution_threshold  = float(input_parameters[1])

social_threshold = float(input_parameters[2])

#Weight of processes
vulnerability = float(input_parameters[3])
farsightness = float(input_parameters[4])

time_horizon = float(input_parameters[5])
tau = float(input_parameters[6])
#Time evolution properties
delta_t = float(input_parameters[7])
integration_time = float(input_parameters[8])

#Initial conditions
from_initial_condition = int(input_parameters[9])
to_initial_conditon= input_parameters[10]
if  to_initial_conditon == 'End':
    to_initial_conditon = None
else:
    to_initial_conditon = int(to_initial_conditon)
#



save_name =  input_parameters[11]

rand_val_file = input_parameters[12] 

in_vals = np.load(rand_val_file)
j = 1
for initial_average_inactivity,initial_pollution in in_vals[from_initial_condition:to_initial_conditon]:


    command = ['python3']
    command.append('/home/pmueller/Masterarbeit/GranoEnv/Macroscopic_Version/macro_dgl_for_cluster.py')
    command.append(f'{pollution_threshold}')   
    command.append(f'{social_threshold}') 
    command.append(f'{vulnerability}') 
    command.append(f'{farsightness}')
    command.append(f'{time_horizon}')
    command.append(f'{tau}')
    command.append(f'{delta_t}')
    command.append(f'{integration_time}')
    command.append(f'{initial_average_inactivity}')
    command.append(f'{initial_pollution}')

    
    save_string = (f'DGL_TG'+
                   f'_pt{pollution_threshold}'+
                   f'_st{social_threshold}'+
                   f'_v{vulnerability}'+
                   f'_f{farsightness}'+
                   f'_th{time_horizon}'+
                   f'_tau{tau}'+
                   f'_dt{delta_t}'+
                   f'_it{integration_time}')
    dir_name = '/p/tmp/pmueller/Masterarbeit/Paper_Data/'+save_string+save_name
    save_string += f'_ia{initial_average_inactivity}_ip{initial_pollution}.csv'
    
    if not os.path.isdir(dir_name):
         os.mkdir(dir_name)
    if check_for_endend_calc(os.path.join(dir_name,save_string)) and not force_run:
        print(f'Already calculated: {os.path.join(dir_name,save_string)}')
        continue
    outfile = open(os.path.join(dir_name,save_string),'w')
    errfile = open(os.path.join(dir_name,save_string)+'.err','w')

    print(f'Starting calc number{j}:\n {os.path.join(dir_name,save_string)}')
    if calculate:
        p = subprocess.Popen(command, stdout=outfile, stderr=errfile)
        p.wait()
    j +=1
stop = timeit.default_timer()
print('Runtime: ', stop - start)
