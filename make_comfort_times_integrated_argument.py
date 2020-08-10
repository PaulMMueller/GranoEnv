#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:51:48 2019

@author: paul
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 15:47:45 2019

@author: paul
"""

import os
import numpy as np
dir_name = '/p/tmp/pmueller/Masterarbeit/Paper_Data/'
save_name = 'ana_paper_case1_01'

raw_dir_list = os.listdir(dir_name)
dir_list = []
for d in raw_dir_list:
    if save_name in d:
        dir_list.append(os.path.join(dir_name,d))
files = []
for d in dir_list:
    raw_file_list  = os.listdir(d)
    for f in raw_file_list:
        if '.csv' in f[-5:]:
            files.append(os.path.join(d,f))

pt_l = []
st_l = []

vul_l = []
far_l = []
th_l  = []

tau_l = []

dt_l  = []
it_l  = []

mean_X = [] 
mean_Y = []
ini_X  = []
ini_Y  = []

nn_l  = []
lp_l  = []
smp_l = []
con_l = []



error_marker = False
error_counter = 0
for file in files:
    print(f'Reading: {file}')
    data_pointer = False
    
    X = [-1] 
    Y = [-1]
    T = [-1]
    nn = -1
    smp = -1
    lp  = -1
    con = -1
    pt = -1  # Set everything to a unphyiscal value so that one can see which data is corrupted
    st = -1
    vul = -1
    far = -1
    th  = -1
    tau = -1
    dt  = -1
    it  = -1
    y0  = -1
    x0  = -1
    ### Read all the data and settings from the file
    with open(file) as f:   
        for line in f.readlines():
            if 'can not be one' in line:
                error_marker = True
                break
            if line == '\n':
                continue
            
            if '===CalculationEnded===' in line:
                break
            
            #Collect data
            if data_pointer:
                data = line.split(',')
                T.append(float(data[0]))
                X.append(float(data[1]))
                Y.append(float(data[2]))               
            
            # Check everything in the header
            if 'Nodes' in line:
                splitted_line  = line.split(',')
                nn = float(splitted_line[0].split()[-1])
                smp = float(splitted_line[2].split()[-1])
                lp = float(splitted_line[1].split()[-1])
            if 'Connected' in line:
                con = str(line.split()[-1])
            if 'Pollution Threshold' in line:
                pt = float(line.split(':')[-1])
            if 'Social Threshold' in line:
                st = float(line.split(':')[-1])
            if 'Vulnerability' in line:
                vul = float(line.split(':')[-1])
            if 'Farsightedness' in line:
                far = float(line.split(':')[-1])
            if 'Time Horizon' in line:
                th = float(line.split(':')[-1])
            if 'Lifetime of the ecological dynamics' in line:
                tau = float(line.split(':')[-1])
            if 'Step Size' in line:
                dt = float(line.split(':')[-1])
            if 'Integration Time' in line:
                it = float(line.split(':')[-1])
            if 'Initial Pollution' in line:
                y0 = float(line.split(':')[-1])
            if 'Initial Average Inactivity' in line:
                x0 = float(line.split(':')[-1])
            if 'Time,' in line:
                data_pointer = True 
    ### Data reading completed
    if error_marker:
        error_marker = False
        continue
    ### Process data


    
    ### Save data
    try: 
        mean_X.append(X[-1]) 
        mean_Y.append(Y[-1])
        ini_X.append(x0)
        ini_Y.append(y0)
    except IndexError:
        error_counter +=1
        print('Error in the file. No data was found. File is skipped')
        continue
    nn_l.append(nn)
    smp_l.append(smp)
    lp_l.append(lp)
    con_l.append(con)
    
    pt_l.append(pt)
    st_l.append(st)
    
    vul_l.append(vul)
    far_l.append(far)
    th_l.append(th)
    
    tau_l.append(tau) 

    dt_l.append(dt)
    it_l.append(it)
   
    
print('Writing to file')
with open(f'comfort_time_{save_name}.csv', 'w') as f:
    f.write('End X, End Y, '+
            'Ini X, Ini Y, ' +
            'Pollution Thres, '+
            'Social Thres, '+
            'Vulnerability, Farsightedness, Time Horizon, Tau,     '+
            'Nodes, RewiringP, AvDegree, Connected, '+
            'Step Size, Integration Time\n'      
        )
    for i in range(len(mean_X)):
        f.write(f'{mean_X[i]:.4f}, '+f'{mean_Y[i]:.4f}, '+
                f'{ini_X[i]:.4f}, '+f'{ini_Y[i]:.4f}, '+
                f'{pt_l[i]:.2f},  '+f'{st_l[i]:.2f}, '+
                f'{vul_l[i]:.4f}, '+f'{far_l[i]:.4f}, '+f'{th_l[i]:.4f}, '+f'{tau_l[i]:.4f}, '+
                f'{int(nn_l[i])}, '+f'{smp_l[i]:.4f}, '+f'{lp_l[i]:.4f}, '+f'{con_l[i]}, '+
                f'{dt_l[i]:.6f}, '+f'{it_l[i]:.1f}\n'
                )
print(f'comfort_time_{save_name}.csv written but {error_counter} Errors occured.')    
