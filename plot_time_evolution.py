#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 12:46:22 2019

@author: paul

Plot the time series of the pollution/average/acitivity of one/multiple files
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
font = {'family' : 'serif',
        'weight' : 'normal',
        'size'   : 11}
plt.rc('font',**font)
plt.rc('xtick', labelsize=11) 
plt.rc('ytick', labelsize=11) 

#plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
plt.rc('text',usetex = True)
#plt.rcParams['svg.fonttype'] = 'none'



files = ['Microscopic_Version/GranoEnv_output_example.csv']#sys.argv[2:]
last_step_in_t = 10 #float(sys.argv[1])
vul = 0
for file in files:
    print(f'Processing: {file}')
    up_th = 0
    lw_th = 0
    splitted_filename =  file.split('/')

    ### Get file name and change it to get a corresponding filename for the graph
    for l in range(len(splitted_filename)):
        if splitted_filename[l] == 'Data':
            splitted_filename[l] = 'Graphs'

    graph_file_name = [l.replace('csv','png') for l in splitted_filename]
    graph_file_name = os.path.join(*graph_file_name)


    ### Read in data from the given file
    time, pollution, average_activity, pollution_change = [],[],[], []
    header = ''
    marker = False
    skipper = False
    with open(file,'r') as f:
       for line in f.readlines():
           if line == '\n':
               continue
           if 'Upper_pollution_threshold' in line:
                up_th = line.split()[1]
                up_th =  float(up_th[:-1])
           if 'Lower_pollution_threshold' in line:
                lw_th = line.split()[1]
                lw_th =  float(lw_th[:-1])
           if 'Upper_social_threshold' in line:
                ust = line.split()[1]
                ust = float(ust[:-1])
           if 'Lower_social_threshold' in line:
                lst = line.split()[1]
                lst = float(lst[:-1])
            # If ana file
           if 'Upper Pollution Threshold' in line:
                up_th = line.split()[-1]
                up_th =  float(up_th)
           if 'Lower Pollution Threshold' in line:
                lw_th = line.split()[-1]
                lw_th =  float(lw_th)
           if 'Upper Social Threshold' in line:
                ust = line.split()[-1]
                ust = float(ust)
           if 'Lower Social Threshold' in line:
                lst = line.split()[-1]
                lst = float(lst)
           if line.startswith('Time,'):
               marker = True
               skipper = False
               continue
           if 'Average_waiting_time' in line:
               break
           if '===CalculationEnded===' in line:
               break
           if '===EndOfCalculation===' in line:
               break
           if marker:
               data =  line.split(',')
               time.append(float(data[0]))
               pollution.append(float(data[1]))
               average_activity.append(float(data[2]))
#               pollution_change.append(float(data[3]))
               continue
           if skipper:
               continue
           if line == '\n':
               continue
           if line.startswith('First inacitve node'):
               continue
           if 'Adjacency matrix' in line:
               skipper = True
               continue
           if 'Vulnerability' in line:
               splitted_line = line.split(',')
               vul = float(splitted_line[0].split()[-1])

           header += line

    header_parts = header.split(' ')
    ### Plot
    fig, (ax1) = plt.subplots(1,figsize=(3.2,2.4))
    X = np.array(average_activity)
    X = 1-X
    
    for i,t in enumerate(time):
        last_step = -1
        if last_step_in_t<t:
            last_step = i 

            break

    if up_th>lw_th:
        ax1.fill_between(time,up_th,lw_th,facecolor='salmon',alpha = .5)#,label = r'$Y^\pm$')
    try:
        ax1.axhline(up_th,linewidth =.5,color = 'k',linestyle = ':')
        ax1.axhline(lw_th,linewidth =.5,color = 'k',linestyle = ':')
        ax1.axhline(1-ust,linewidth =.5,color = 'k',linestyle = ':')
        ax1.axhline(1-lst,linewidth =.5,color = 'k',linestyle = ':')
        
        if ust > lst:
            ax1.fill_between(time,1-ust,1-lst,facecolor='lightsteelblue',alpha = .5)#,label = r'$1-\gamma^\pm$')
        else:
             ax1.axhline(1-ust,color='green',linestyle='--',alpha = .2)#,label = r'$1-\gamma^\pm$')
    except:
        pass
    ax1.plot(time[:last_step],X[:last_step], label = r'$1-X$',color='blue')
    ax1.plot(time[:last_step],pollution[:last_step],label = r'$Y$',color='red',linestyle= '-')
    if vul != 1:
        tswitch = 1/(1-vul) * np.log((pollution[0]-(1-average_activity[0])/(1-vul))/((1-average_activity[0])+1/(vul-1)))
        Y_fixed = ((1-average_activity[0])/(1-vul))*np.exp(-vul*tswitch) + ( ((average_activity[0]-1)/(1-vul)) +pollution[0])*np.exp(-tswitch)

        ax1.axhline(Y_fixed,color = 'k',linestyle='--',label = r'$Y(t_\mathrm{switch})$')
        # ax1.axvline(tswitch,color = 'k',label = r'$t_{switch}$')
    pos = np.linspace(0,1,11)
    ylabs =  list(np.round(np.linspace(0,1,11),1))
    for i, _ in enumerate(ylabs):
        if i%2==1:
            ylabs[i] = ''
    ax1.set_xticks(np.linspace(0,last_step_in_t,6))
    ax1.set_yticks(pos)
    ax1.set_yticklabels(ylabs)
    ax1.xaxis.set_ticks_position('both')
    ax1.yaxis.set_ticks_position('both')
    ax1.set_xlabel(r'Time $t$')
    ax1.set_ylabel(r'$Y$ / $1-X$')
    ax1.get_yaxis().set_tick_params(which='both', direction='in', length=4, width=1, colors='k')
    ax1.get_xaxis().set_tick_params(which='both', direction='in', length=4, width=1, colors='k')
    ax1.set_ylim(0,1)
    ax1.set_xlim(0,time[last_step])
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    ax2 = ax1.twinx()

    ax2.set_yticks(pos)
    ax2.set_yticklabels(['','','',r'$Y^-$',r'$Y^+=1-\gamma^+$',r'$1-\gamma^-$','','','','',''])
    ax2.get_yaxis().set_tick_params(which='both', direction='in', length=4, width=1, colors='k')
 #   ax1.set_title(f'NN={header_parts[4][:-1]} lp={header_parts[7][:-6]}'+r' $\alpha=$'+
#                f'{header_parts[-8][:-1]}'+r' $\beta=$'+f'{header_parts[-6][:-7]}'+
 #               r' $\theta=$'+f'{header_parts[-11][:-1]}'
  #              r' $ d_t=$'+f'{header_parts[-4][:-1]}'
   #                          ,fontdict = {'fontsize': 11, 'verticalalignment': 'baseline'})
    fig.tight_layout(rect=[0, 0, 1.05, 1])
    fig.savefig(graph_file_name,dpi = 1000)
    plt.close(fig)

